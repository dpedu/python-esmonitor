from os import statvfs

def diskspace(filesystems=[]):
    for fs in filesystems:
        stats = statvfs(fs)
        
        info = {
            "fs": fs,
            "diskfree": stats.f_bsize * stats.f_bavail,
            "diskused": (stats.f_blocks-stats.f_bavail) * stats.f_bsize,
            "disksize": stats.f_bsize * stats.f_blocks
        }
        
        info["diskpctused"] = round(info["diskfree"]/info["disksize"], 2)
        info["diskpctfree"] = round(info["diskused"]/info["disksize"], 2)
        
        yield info

mapping = {
    "diskspace": {
        "properties": {
            "diskfree": {
                "type": "long"
            },
            "diskused": {
                "type": "long"
            },
            "disksize": {
                "type": "long"
            },
            "diskpctused": {
                "type": "double"
            },
            "diskpctfree": {
                "type": "double"
            },
            "fs": {
                "type": "string"
            }
        }
    }
}

if __name__ == '__main__':
    #avg = load()
    #print(' '.join([avg["load_1m"], avg["load_5m"], avg["load_15m"]]))
    for item in diskspace(filesystems=["/", "/tmp/monitor"]):
        print(item)
