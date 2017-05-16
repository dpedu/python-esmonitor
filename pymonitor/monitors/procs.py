from glob import glob
import re


KTHREADD_PID = 2
PAT_REMOVE_PROC_SPACES = re.compile(r'(\([^\)]+\))')


def procs():
    # Get uid->name mapping
    users = {}
    with open('/etc/passwd', 'r') as passwd:
        while True:
            line = passwd.readline()
            if not line:
                break
            uname, _, uid, gid, opts, home, shell = line.split(":")
            users[int(uid)] = uname

    # Get gid->groupname mapping
    groups = {}
    with open('/etc/group', 'r') as group:
        while True:
            line = group.readline()
            if not line:
                break
            gname, _, gid, y = line.split(":")
            groups[int(gid)] = gname

    num_procs = 0
    num_threads = 0
    num_kthreads = 0

    for f in glob('/proc/[0-9]*/stat'):
        try:
            with open(f, "r") as statfile:
                # Read stat info
                stat = statfile.read().strip()
                # Fix spaces in process names
                stat = PAT_REMOVE_PROC_SPACES.sub("PROCNAME", stat)
                stat = stat.split(" ")

                proc_parent = int(stat[3])

                if proc_parent == KTHREADD_PID:
                    num_kthreads += 1
                else:
                    num_procs += 1
                    num_threads += int(stat[19])

        except Exception as e:
            print(e)
            print("Failed to open %s" % f)

    yield {"procs": num_procs, "threads": num_threads, "kthreads": num_kthreads}


mapping = {
    "procs": {
        "properties": {
            "procs": {
                "type": "integer"
            },
            "threads": {
                "type": "integer"
            },
            "kthreads": {
                "type": "integer"
            }
        }
    }
}


if __name__ == '__main__':
    for item in procs():
        print(item)
