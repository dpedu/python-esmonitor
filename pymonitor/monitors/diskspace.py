from os import statvfs


def diskspace(filesystems=[]):
    for fs in filesystems:
        stats = statvfs(fs)

        info = {
            "fs": fs,
            "fs_raw": fs,
            "diskfree": stats.f_bsize * stats.f_bavail,
            "diskused": (stats.f_blocks - stats.f_bavail) * stats.f_bsize,
            "disksize": stats.f_bsize * stats.f_blocks,
            "inodesmax": stats.f_files,
            "inodesfree": stats.f_favail,
            "inodesused": stats.f_files - stats.f_favail
        }

        info["diskpctused"] = round(info["diskused"] / info["disksize"] if info["disksize"] > 0 else 0, 2)
        info["diskpctfree"] = round(info["diskfree"] / info["disksize"] if info["disksize"] > 0 else 0, 2)

        info["inodesused_pct"] = round(info["inodesused"] / info["inodesmax"] if info["inodesmax"] > 0 else 0, 2)
        info["inodesfree_pct"] = round(info["inodesfree"] / info["inodesmax"] if info["inodesmax"] > 0 else 0, 2)

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
            "fs_raw": {
                "type": "string",
                "index": "not_analyzed"
            },
            "inodesmax": {
                "type": "long"
            },
            "inodesfree": {
                "type": "long"
            },
            "inodesused": {
                "type": "long"
            },
            "inodesused_pct": {
                "type": "double"
            },
            "inodesfree_pct": {
                "type": "double"
            },
        }
    }
}


if __name__ == '__main__':
    for item in diskspace(filesystems=["/", "/dev"]):
        print(item)
