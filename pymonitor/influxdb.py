from pymonitor import Backend
from influxdb import InfluxDBClient
import datetime


class InfluxBackend(Backend):
    def __init__(self, master, conf):
        super().__init__(master, conf)
        self.client = None

    def connect(self):
        """
        Connect to the backend and do any prep work
        """
        self.client = InfluxDBClient(self.conf["host"], self.conf["port"], self.conf["user"], self.conf["password"])  # DBNAME
        dbname = self.conf.get("database", "monitoring")
        self.client.create_database(dbname)
        self.client.switch_database(dbname)


    def add_data(self, metric):
        """
        Accept a Metric() object and send it off to the backend
        """
        metric.tags.update(**self.sysinfo)
        body = [{
                "measurement": metric.tags["type"],
                "tags": metric.tags,
                "time": datetime.datetime.utcnow().isoformat(),
                "fields": metric.values
            }
        ]
        self.client.write_points(body)
