__version__ = "0.4.0"
from itertools import chain
import logging
from pymonitor.builtins import sysinfo


class Backend(object):
    """
    Base class for data storage backends
    """
    def __init__(self, master, conf):
        self.master = master
        self.conf = conf
        self.sysinfo = {}
        self.logger = logging.getLogger("monitordaemon.backend")
        self.update_sys_info()

    def update_sys_info(self):
        """
        Fetch generic system info that is sent with every piece of monitoring data
        """
        self.sysinfo["hostname"] = sysinfo.hostname()
        self.sysinfo["ipaddr"] = sysinfo.ipaddr()

    def connect(self):
        """
        Connect to the backend and do any prep work
        """
        raise NotImplementedError()

    def add_data(self, metric):
        """
        Accept a Metric() object and send it off to the backend
        """
        raise NotImplementedError()


class Metric(object):
    """
    Wrapper for holding metrics gathered from the system. All monitor modules yield multiple of these objects.
    """
    def __init__(self, values, tags=None):
        """
        :param values: dict of name->value metric data
        :param tags: dict of key->value tags associated with the metric data
        """
        self.values = values
        self.tags = tags or {}

    def __repr__(self):
        fields = []
        for k, v in chain(self.values.items(), self.tags.items()):
            fields.append("{}={}".format(k, v))
        return "<{}{{{}}}>".format(self.__class__.__name__, ','.join(fields))
