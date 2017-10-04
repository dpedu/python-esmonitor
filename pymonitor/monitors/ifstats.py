from collections import defaultdict
from time import time


rx_bytes, rx_packets, rx_errs, rx_drop, rx_fifo, rx_frame, rx_compressed, rx_multicast, \
    tx_bytes, tx_packets, tx_errs, tx_drop, tx_fifo, tx_colls, tx_carrier, tx_compressed = range(16)


previous = defaultdict(lambda: [-1 for i in range(17)])


def ifstats():
    with open("/proc/net/dev", "r") as f:
        _, _ = f.readline(), f.readline()

        for line in f.readlines():
            fields = line.split()
            ifname = fields.pop(0).rstrip(":")
            for i in range(0, len(fields)):
                fields[i] = int(fields[i])

            record = {"iface": ifname,
                      "rx_bytes": fields[rx_bytes],
                      "tx_bytes": fields[tx_bytes],
                      "rx_packets": fields[rx_packets],
                      "tx_packets": fields[tx_packets],
                      }

            prev = previous[ifname]
            if prev[rx_bytes] != -1:
                tdelta = time() - prev[-1]
                record["rx_traffic"] = round((fields[rx_bytes] - prev[rx_bytes]) / tdelta)
                record["tx_traffic"] = round((fields[tx_bytes] - prev[tx_bytes]) / tdelta)
                record["tx_packetcnt"] = round((fields[tx_packets] - prev[tx_packets]) / tdelta)
                record["rx_packetcnt"] = round((fields[rx_packets] - prev[rx_packets]) / tdelta)

            previous[ifname] = fields + [time()]

            yield record


mapping = {
    "ifstats": {
        "properties": {
            "iface": {
                "type": "string",
                "index": "not_analyzed"
            },
            "rx_bytes": {
                "type": "long"
            },
            "tx_bytes": {
                "type": "long"
            },
            "rx_packets": {
                "type": "long"
            },
            "tx_packets": {
                "type": "long"
            },
            "rx_traffic": {
                "type": "long"
            },
            "tx_traffic": {
                "type": "long"
            },
            "tx_packetcnt": {
                "type": "long"
            },
            "rx_packetcnt": {
                "type": "long"
            }
        }
    }
}


if __name__ == '__main__':
    from time import sleep
    for item in ifstats():
        print(item)
    print("-")
    sleep(2)
    for item in ifstats():
        print(item)
