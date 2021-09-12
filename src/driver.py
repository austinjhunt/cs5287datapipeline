""" Driver Module, Controls Execution of Project """
import argparse
import os
import json
import logging
from lib.producer import Producer
from lib.consumer import Consumer

class Driver:

    def __init__(self,verbose=False):
        self.setup_logging(verbose)
        self.sink_host = None
        self.consumer_host = None
        self.bootstrap_server = None
        self.configure()

    def run_consumer(self, topic='stock-market-data', verbose=False):
        """ Method to drive a Kafka Consumer process (run this from a Cloud VM where Apache Kafka is installed) """
        self.info("Running Kafka Consumer...")
        self.consumer = Consumer(
            verbose=verbose,
            bootstrap_server=self.bootstrap_server,
            topics=[topic]
        )
        self.consumer.consume()

    def run_producer(self,topic='stock-market-data', producer_alias="Producer 1",stock_symbol="AMZN",
        sleep_interval=1, verbose=False,num_messages=100):
        """ Method to drive a Kafka Producer process (run this from a local VM in VirtualBox) """
        self.info("Running Kafka Producer...")
        self.producer = Producer(
            bootstrap_server=self.bootstrap_server,
            producer_alias=producer_alias,
            stock_symbol=stock_symbol,
            sleep_interval=sleep_interval,
            verbose=verbose
        )
        self.producer.produce(num_messages=num_messages, topic=topic)

    def setup_logging(self, verbose):
        """ set up self.logger for Driver logging """
        self.logger = logging.getLogger('driver')
        formatter = logging.Formatter('%(prefix)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.prefix = {'prefix': 'DRIVER'}
        self.logger.addHandler(handler)
        self.logger = logging.LoggerAdapter(self.logger, self.prefix )
        if verbose:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Debug mode enabled', extra=self.prefix )
        else:
            self.logger.setLevel(logging.INFO)

    def debug(self, msg):
        self.logger.debug(msg, extra=self.prefix)

    def info(self, msg):
        self.logger.info(msg, extra=self.prefix)

    def error(self, msg):
        self.logger.error(msg, extra=self.prefix)

    def configure(self):
        """ Parse configuration file (config.json) """
        self.info("Configuring driver")
        config_file = os.path.join(
            os.path.dirname(__file__),
            'config.json'
        )
        with open(config_file) as f:
            try:
                config = json.load(f)
                cloud_hosts = config['cloud_hosts']
                # Should be 2 VMs.
                # First will run Kafka Broker, Zookeeper, and Consumer.
                self.consumer_host = cloud_hosts[0]
                self.bootstrap_server = self.consumer_host['public']
                # Second will Run Kafka Broker and CouchDB, functioning as sink.
                self.sink_host = cloud_hosts[1]
                self.debug(f"Consumer host: {self.consumer_host}")
                self.debug(f"Sink Host: {self.sink_host}")
            except Exception as e:
                self.error(e)


parser = argparse.ArgumentParser(
    description='pass arguments to run the driver for the project'
)
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
parser.add_argument('-t', '--topic',
    help='topic to produce (if running producer with -p) or consume (if running consumer with -c)',
    type=str,required=True)
parser.add_argument('-p', '--run_producer', help='whether to run producer', action='store_true')
parser.add_argument('-pa', '--producer_alias', default='Producer 1',
    help='friendly alias/name of producer', type=str)
parser.add_argument('-n', '--num_messages', type=int, default=100, help='number of messages to produce')
parser.add_argument('-s', '--sleep_interval', default=1, type=int,
    help='number of seconds to sleep between each message sent')
parser.add_argument('-ss', '--stock_symbol', default='AMZN', help='stock symbol to produce data for', type=str)

parser.add_argument('-c', '--run_consumer', help='whether to run consumer', action='store_true')

args = parser.parse_args()
driver = Driver(verbose=args.verbose)

if args.run_producer:
    producer_alias = args.producer_alias
    topic = args.topic
    stock_symbol = args.stock_symbol
    sleep_interval = args.sleep_interval
    driver.run_producer(
        topic=topic,
        producer_alias=producer_alias,
        stock_symbol=stock_symbol,
        num_messages=args.num_messages,
        sleep_interval=sleep_interval,
        verbose=args.verbose
    )
elif args.run_consumer:
    topic = args.topic
    driver.run_consumer(
        topic=topic,
        verbose=args.verbose
    )