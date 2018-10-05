from pymonitor import Metric

def load():
    with open("/proc/loadavg", "r") as f:
        m1, m5, m15, procs, pid = f.read().strip().split(" ")
        yield Metric({"load_1m": float(m1),
                      "load_5m": float(m5),
                      "load_15m": float(m15)})


mapping = {
    "load_15m": {
        "type": "double"
    },
    "load_5m": {
        "type": "double"
    },
    "load_1m": {
        "type": "double"
    }
}


if __name__ == '__main__':
    for item in load():
        print(item)
