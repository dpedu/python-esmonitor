#!/usr/bin/env python3

from threading import Thread
from time import time, sleep
import traceback
import logging
import json
import sys
import os
from pymonitor.elasticsearch import ESBackend
from pymonitor.influxdb import InfluxBackend


class MonitorDaemon(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.config = config
        self.threads = []
        self.backend = {"elasticsearch": ESBackend,
                        "influxdb": InfluxBackend}[self.config["backend"]["type"]](self, self.config["backend"])

    def run(self):
        """
        Start all monitoring threads and block until they exit
        """
        logger = logging.getLogger("monitordaemon")

        checkerPath = os.path.dirname(os.path.realpath(__file__)) + "/monitors/"
        sys.path.append(checkerPath)
        logger.debug("path %s" % checkerPath)

        # Create all monitoring threads
        logger.debug("creating monitor threads")
        for instance in self.config["monitors"]:
            monitor_thread = MonitorThread(instance, self.backend)
            self.threads.append(monitor_thread)

        # Setup backend
        self.backend.connect()

        logger.debug("starting monitor threads")
        for monitor_thread in self.threads:
            monitor_thread.start()

        # Tear down all threads
        logger.debug("joining monitor threads")
        for monitor_thread in self.threads:
            monitor_thread.join()

        logger.debug("joined monitor threads")

    def shutdown(self):
        """
        Signal all monitoring threads to stop
        """
        for monitor_thread in self.threads:
            monitor_thread.shutdown()


class MonitorThread(Thread):
    def __init__(self, config, backend):
        """
        Load checker function and prepare scheduler
        """
        Thread.__init__(self)
        self.config = config
        self.backend = backend
        self.logger = logging.getLogger("monitordaemon.monitorthread.%s" % self.config["type"])
        self.logger.debug("initing worker thread with config %s" % self.config)

        self.logger.debug("importing %s" % self.config["type"])
        self.imported = __import__(self.config["type"])
        self.checker_func = getattr(self.imported, self.config["type"])
        self.logger.debug("checker func %s" % self.checker_func)

        self.alive = True
        self.delay = int(self.config["freq"])
        self.lastRun = 0

    def run(self):
        """
        Call execute method every x seconds forever
        """
        self.logger.debug("starting scheduler")
        while self.alive:
            if time() - self.lastRun > self.delay:
                self.lastRun = time()
                try:
                    self.execute(self.config["args"])
                except:
                    tb = traceback.format_exc()
                    self.logger.warning(tb)
            sleep(0.5)
        self.logger.debug("scheduler exited")

    def execute(self, args):
        """
        Run the loaded checker function. Pass each Metric object yielded to the backend.
        """
        before = time()
        for result in self.checker_func(**args):
            result.tags.update(type=self.config["type"])
            self.logger.debug("result: %s" % (result,))
            self.backend.add_data(result)
        duration = time() - before
        self.logger.info("runtime: %.3f" % duration)

    def shutdown(self):
        """
        Tell thread to exit
        """
        self.logger.debug("canceling scheduler")
        self.alive = False


def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", type="string", dest="config", help="Path to config file")
    parser.add_option("-l", "--logging", action="store", dest="logging", help="Logging level", default="INFO",
                      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO',  'DEBUG'])

    (options, args) = parser.parse_args()

    logging.basicConfig(level=getattr(logging, options.logging),
                        format="%(asctime)-15s %(levelname)-8s %(name)s@%(filename)s:%(lineno)d %(message)s")
    logger = logging.getLogger("init")

    logger.debug("options: %s" % options)

    if options.config is None:
        parser.print_help()
        sys.exit()

    with open(options.config, "r") as c:
        if options.config.endswith('.json'):
            conf = json.load(c)
        elif options.config.endswith('.yml'):
            from yaml import load as yaml_load
            conf = yaml_load(c)
        else:
            raise Exception("Invalid config format")

    logger.debug("starting daemon with conf: %s" % conf)

    daemon = MonitorDaemon(conf)
    try:
        daemon.start()
        daemon.join()
    except KeyboardInterrupt:
        print("")
        daemon.shutdown()
