#!/usr/bin/env python3

from threading import Thread
from time import time,sleep
import logging
import json
import sys
import os

class MonitorDaemon(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.config = config
        self.threads = []
    
    def run(self):
        """
        Start all monitoring threads and block until they exit
        """
        logger = logging.getLogger("monitordaemon")
        
        checkerPath = os.path.dirname(os.path.realpath(__file__))+"/monitors/"
        sys.path.append(checkerPath)
        logger.info("path %s" % checkerPath)
        
        # Create/start all monitoring threads
        logger.info("starting monitor threads")
        for instance in self.config["monitors"]:
            monitor_thread = MonitorThread(instance)
            monitor_thread.start()
            self.threads.append(monitor_thread)
        
        # Tear down all threads
        logger.info("joining monitor threads")
        for monitor_thread in self.threads:
            monitor_thread.join()
        
        logger.info("joined monitor threads")
    
    def shutdown(self):
        """
        Signal all monitoring threads to stop
        """
        for monitor_thread in self.threads:
            monitor_thread.shutdown()


class MonitorThread(Thread):
    def __init__(self, config):
        """
        Load checker function and prepare scheduler
        """
        Thread.__init__(self)
        self.config = config
        self.logger = logging.getLogger("monitordaemon.monitorthread.%s"%self.config["type"])
        self.logger.info("initing worker thread with config %s" % self.config)
        
        self.logger.info("importing %s" % self.config["type"])
        self.checker_func = getattr(__import__(self.config["type"]), self.config["type"])
        self.logger.info("checker func %s" % self.checker_func)
        
        self.alive = True
        self.delay = int(self.config["freq"])
        self.lastRun = 0
    
    def run(self):
        """
        Call execute method every x seconds forever
        """
        self.logger.info("starting scheduler")
        while self.alive:
            if time() - self.lastRun > self.delay:
                self.lastRun = time()
                self.execute(self.config["args"])
        self.logger.info("scheduler exited")
    
    def execute(self, args):
        """
        Run the loaded checker function
        """
        result = self.checker_func(**args)
        self.logger.info("result: %s" % (result,))
    
    def shutdown(self):
        """
        Tell thread to exit
        """
        self.logger.info("cancelling scheduler")
        self.alive=False

if __name__ == '__main__':
    from optparse import OptionParser
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(levelname)-8s %(name)s@%(filename)s:%(lineno)d %(message)s")
    logger = logging.getLogger("init")
    
    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", type="string", dest="config", help="Path to config file")
    
    (options, args) = parser.parse_args()
    logger.debug("options: %s" % options)
    
    if options.config == None:
        parser.print_help()
        sys.exit()
    
    with open(options.config, "r") as c:
        conf = json.load(c)
    
    logger.info("starting daemon with conf: %s" % conf)
    
    daemon = MonitorDaemon(conf)
    try:
        daemon.start()
        daemon.join()
    except KeyboardInterrupt:
        print("")
        daemon.shutdown()
    
