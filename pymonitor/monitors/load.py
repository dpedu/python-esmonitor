def load():
    with open("/proc/loadavg", "r") as f:
        m1, m5, m15, procs, pid = f.read().strip().split(" ")
        return {
            "load_1m": m1,
            "load_5m": m5,
            "load_15m":m15
        }

mapping = {
    "load": {
        "properties": {
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
    }
}

if __name__ == '__main__':
    avg = load()
    print(' '.join([avg["load_1m"], avg["load_5m"], avg["load_15m"]]))
