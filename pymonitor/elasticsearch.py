from pymonitor import Backend
import datetime
import json


class ESBackend(Backend):
    def __init__(self, master, conf):
        """
        Init elasticsearch client
        """
        super().__init__(master, conf)
        self.mapping = {}
        self.current_index = None

    def connect(self):
        self.logger.debug("connecting to elasticsearch at %s" % self.conf["url"])
        from elasticsearch import Elasticsearch
        self.es = Elasticsearch([self.conf["url"]])
        self.logger.debug("connected to backend")

        for monitor_thread in self.master.threads:
            self.mapping.update(monitor_thread.imported.mapping)
        self.logger.debug("final mapping: ", self.mapping)
        self.create_mapping_template()

        self.check_index()

    def get_index_name(self):
        """
        Return name of current index such as 'monitor-2015.12.05'
        """
        return "monitor-%s" % datetime.datetime.now().strftime("%Y.%m.%d")

    def check_index(self):
        """
        Called before adding any data to ES. Checks if a new index should be created due to date change
        """
        indexName = self.get_index_name()
        if indexName != self.current_index:
            self.create_index(indexName)

    def create_index(self, indexName):
        """
        Check if current index exists, and if not, create it
        """
        if not self.es.indices.exists(index=indexName):
            self.es.indices.create(index=indexName, ignore=400)  # ignore already exists error
        self.current_index = indexName

    def create_mapping_template(self):
        default_fields = {"ipaddr": {"type": "ip"},  # TODO i dont like how these default fields are handled in general
                          "hostname": {"type": "text"},
                          "hostname_raw": {"type": "keyword"},
                          "@timestamp": {"type": "date"}}  #"field": "@timestamp"

        fields = dict(**self.mapping)
        fields.update(**default_fields)
        template = {"index_patterns": ["monitor-*"],
                    "settings": {"number_of_shards": 1},  # TODO shard info from config file
                    "mappings": {"_default_": {"properties": fields}}}
        self.logger.debug("creating template with body %s", json.dumps(template, indent=4))
        self.es.indices.put_template(name="monitor", body=template)

    def add_data(self, metric):
        """
        Submit a piece of monitoring data
        """
        self.check_index()

        metric.tags.update(**self.sysinfo)
        metric.values["@timestamp"] = datetime.datetime.utcnow().isoformat()

        metric_dict = {}
        metric_dict.update(metric.values)
        metric_dict.update(metric.tags)

        # We'll likely group by tags on the eventual frontend, and under elasticsearch this works best if the entire
        # field is handled as a single keyword. Duplicate all tags into ${NAME}_raw fields, expected to be not analyzed
        for k, v in metric.tags.items():
            metric_dict["{}_raw".format(k)] = v

        self.logger.debug("logging type %s: %s" % (metric.tags["type"], metric))
        res = self.es.index(index=self.current_index, doc_type="monitor_data", body=metric_dict)
        self.logger.debug("%s created %s" % (metric.tags["type"], res["_id"]))
