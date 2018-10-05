from pymonitor import Metric
from os import statvfs
import logging


def diskspace(filesystems=[], discover=True, omit=[]):
    """
    Emit disk space usage statistics for the passed filesystems.
    :param filesystems: list of mountpoints to gather stats for
    :param discover: automatically find non-temporary filesystems to gather statistics for. Duplicates from the
                     filesystems param will be ignored.
    :param omit: list of paths that, if prefix a discovered mountpoint, to not report on
    """
    filesystems = [f.rstrip("/") if f != "/" else f for f in filesystems]
    if discover:
        with open("/proc/mounts") as f:
            for line in f.readlines():
                device, mountpoint, fstype, options, _, _ = line.split(" ")
                # filter out some mountpoints we probably don't care about space on
                if any([mountpoint.startswith(prefix) for prefix in ["/sys", "/proc", "/dev", "/run"]]):
                    continue
                filesystems.append(mountpoint)

    for fs in set(filesystems):
        if any([fs.startswith(i) for i in omit or []]):
            continue
        try:
            stats = statvfs(fs)
        except FileNotFoundError:
            logging.warning("filesystem not found: %s", repr(fs))
            continue

        info = {
            "diskfree": stats.f_bsize * stats.f_bavail,
            "diskused": (stats.f_blocks - stats.f_bavail) * stats.f_bsize,
            "disksize": stats.f_bsize * stats.f_blocks,
            "inodesmax": stats.f_files,
            "inodesfree": stats.f_favail,
            "inodesused": stats.f_files - stats.f_favail
        }

        info["diskpctused"] = round(info["diskused"] / info["disksize"] if info["disksize"] > 0 else 0.0, 5)
        info["diskpctfree"] = round(info["diskfree"] / info["disksize"] if info["disksize"] > 0 else 0.0, 5)

        info["inodesused_pct"] = round(info["inodesused"] / info["inodesmax"] if info["inodesmax"] > 0 else 0.0, 5)
        info["inodesfree_pct"] = round(info["inodesfree"] / info["inodesmax"] if info["inodesmax"] > 0 else 0.0, 5)

        yield Metric(info, {"fs": fs})


mapping = {
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
        "type": "text"
    },
    "fs_raw": {
        "type": "keyword"
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
    }
}


if __name__ == '__main__':
    from pprint import pprint
    for item in diskspace(filesystems=[], discover=True, omit=None):
        pprint(item)
