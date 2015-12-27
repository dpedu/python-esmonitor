#!/usr/bin/env python3

from threading import Thread
from elasticsearch import Elasticsearch
from time import time,sleep
from pymonitor.builtins import sysinfo
import traceback
import datetime
import logging
import json
import sys
import os

class MonitorDaemon(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.config = config
        self.threads = []
        self.backend = Backend(self.config["backend"]["url"])
    
    def run(self):
        """
        Start all monitoring threads and block until they exit
        """
        logger = logging.getLogger("monitordaemon")
        
        checkerPath = os.path.dirname(os.path.realpath(__file__))+"/monitors/"
        sys.path.append(checkerPath)
        logger.info("path %s" % checkerPath)
        
        # Create/start all monitoring threads
        logger.info("creating monitor threads")
        for instance in self.config["monitors"]:
            monitor_thread = MonitorThread(instance, self.backend)
            self.threads.append(monitor_thread)
            self.backend.mapping.update(monitor_thread.mapping)
        
        self.backend.connect()
        
        logger.info("starting monitor threads")
        for monitor_thread in self.threads:
            monitor_thread.start()
        
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


class Backend:
    def __init__(self, es_url):
        """
        Init elasticsearch client
        """
        self.es_url = es_url
        self.mapping = {}
        self.logger = logging.getLogger("monitordaemon.backend")
        
        self.sysinfo = {}
        self.update_sys_info()
        self.logger.info("running on %(hostname)s (%(ipaddr)s)" % self.sysinfo)
    
    def connect(self):
        self.logger.info("final mapping %s" % self.mapping)
        self.logger.info("connecting to backend at %s" % self.es_url)
        self.es = Elasticsearch([self.es_url])
        self.logger.info("connected to backend")
        self.current_index = ""
        self.check_before_entry()
    
    def update_sys_info(self):
        """
        Fetch generic system info that is sent with every piece of monitoring data
        """
        self.sysinfo["hostname"] = sysinfo.hostname()
        self.sysinfo["hostname.raw"] = self.sysinfo["hostname"]
        self.sysinfo["ipaddr"] = sysinfo.ipaddr()
    
    def get_index_name(self):
        """
        Return name of current index such as 'monitor-2015.12.05'
        """
        return "monitor-%s" % datetime.datetime.now().strftime("%Y.%m.%d")
    
    def create_index(self, indexName):
        """
        Check if current index exists, and if not, create it
        """
        if not self.es.indices.exists(index=indexName):
            mapping = {
                "mappings": {
                    "_default_":{
                        "properties": {
                            "ipaddr": {
                                "type": "ip"
                            },
                            "hostname": {
                                "type": "string"
                            },
                            "hostname.raw": {
                                "type" : "string",
                                "index" : "not_analyzed"
                            }
                        }
                    }
                }
            }
            mapping["mappings"].update(self.mapping)
            self.logger.info("creating index %s with mapping %s" % (indexName, json.dumps(mapping, indent=4)))
            self.es.indices.create(index=indexName, ignore=400, body=mapping)# ignore already exists error
        self.current_index = indexName
    
    def check_before_entry(self):
        """
        Called before adding any data to ES. Checks if a new index should be created due to date change
        """
        indexName = self.get_index_name()
        if indexName != self.current_index:
            self.create_index(indexName)
    
    def add_data(self, data_type, data):
        """
        Submit a piece of monitoring data
        """
        self.check_before_entry()
        
        doc = self.sysinfo.copy()
        doc.update(data)
        doc["@timestamp"] = datetime.datetime.utcnow().isoformat()
        
        self.logger.info("logging type %s: %s" % (data_type, doc))
        res = self.es.index(index=self.current_index, doc_type=data_type, body=doc)
        self.logger.info("%s created %s" % (data_type, res["_id"]))
    

class MonitorThread(Thread):
    def __init__(self, config, backend):
        """
        Load checker function and prepare scheduler
        """
        Thread.__init__(self)
        self.config = config
        self.backend = backend
        self.logger = logging.getLogger("monitordaemon.monitorthread.%s"%self.config["type"])
        self.logger.info("initing worker thread with config %s" % self.config)
        
        self.logger.info("importing %s" % self.config["type"])
        self.checker_func = getattr(__import__(self.config["type"]), self.config["type"])
        self.logger.info("checker func %s" % self.checker_func)
        
        self.mapping = {}
        #try:
        self.mapping.update(__import__(self.config["type"]).mapping)
        #except:
        #    pass
        self.logger.info("mapping %s" % self.mapping)
        
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
                try:
                    self.execute(self.config["args"])
                except:
                    tb = traceback.format_exc()
                    print(tb)
            sleep(0.5)
        self.logger.info("scheduler exited")
    
    def execute(self, args):
        """
        Run the loaded checker function
        """
        for result in self.checker_func(**args):
            self.logger.info("result: %s" % (result,))
            self.backend.add_data(self.config["type"], result)
    
    def shutdown(self):
        """
        Tell thread to exit
        """
        self.logger.info("cancelling scheduler")
        self.alive=False

def run_cli():
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

if __name__ == '__main__':
    run_cli()
