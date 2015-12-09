from psutil import disk_io_counters

def diskio(disks=[]):
    with open("/proc/uptime", "r") as f:
        uptime = int(float(f.read().split(" ")[0]))
    diskinfo = disk_io_counters(perdisk=True)
    for disk,stats in diskinfo.items():
        if disks and disk not in disks:
            continue
        stats = {
            "disk": disk,
            "reads_ps": round(stats.read_count/uptime, 2),
            "writes_ps":round(stats.write_count/uptime, 2),
            "read_ps":  round(stats.read_bytes/uptime, 2),
            "write_ps": round(stats.write_bytes/uptime, 2),
            "reads":    stats.read_count,
            "writes":   stats.write_count,
            "read":     stats.read_bytes,
            "written":  stats.write_bytes,
            "read_size":round(stats.read_bytes/stats.read_count, 2),
            "write_size":round(stats.write_bytes/stats.write_count, 2)
        }
        yield(stats)

mapping = {
    "diskio": {
        "properties": {
            "disk": {
                "type": "string"
            },
            "reads_ps": {
                "type": "double"
            },
            "writes_ps": {
                "type": "double"
            },
            "read_ps": {
                "type": "double"
            },
            "write_ps": {
                "type": "double"
            },
            "reads": {
                "type": "long"
            },
            "writes": {
                "type": "long"
            },
            "read": {
                "type": "long"
            },
            "written": {
                "type": "long"
            },
            "read_size": {
                "type": "double"
            },
            "write_size": {
                "type": "double"
            }
        }
    }
}

if __name__ == '__main__':
    for item in diskio():
        print(item)

