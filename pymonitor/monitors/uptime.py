from pymonitor import Metric


def uptime():
    with open("/proc/uptime", "r") as f:
        yield Metric({"uptime": int(float(f.read().split(" ")[0]))})


mapping = {"uptime": {"type": "integer"}}


if __name__ == '__main__':
    for item in uptime():
        print(item)
