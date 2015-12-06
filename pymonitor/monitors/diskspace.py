from os import statvfs

def diskspace(filesystems=[]):
    for fs in filesystems:
        stats = statvfs(fs)
        
        info = {
            "fs": fs,
            "fs.raw": fs,
            "diskfree": stats.f_bsize * stats.f_bavail,
            "diskused": (stats.f_blocks-stats.f_bavail) * stats.f_bsize,
            "disksize": stats.f_bsize * stats.f_blocks
        }
        
        info["diskpctused"] = round(info["diskused"]/info["disksize"], 2)
        info["diskpctfree"] = round(info["diskfree"]/info["disksize"], 2)
        
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
            },
            "fs.raw": {
                "type" : "string",
                "index" : "not_analyzed"
            }
        }
    }
}

if __name__ == '__main__':
    for item in diskspace(filesystems=["/", "/tmp/monitor"]):
        print(item)
