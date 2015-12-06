from glob import glob
import re

KTHREADD_PID = 2
PAT_UID = re.compile(r'Uid:\s+(?P<uid>[0-9]+)\s')
PAT_GID = re.compile(r'Gid:\s+(?P<gid>[0-9]+)\s')

def procs():
    
    # Get uid->name mapping
    users = {}
    with open('/etc/passwd', 'r') as passwd:
        while True:
            line = passwd.readline()
            if not line:
                break
            uname,x,uid,gid,opts,home,shell = line.split(":")
            users[int(uid)]=uname
    
    # Get gid->groupname mapping
    groups = {}
    with open('/etc/group', 'r') as group:
        while True:
            line = group.readline()
            if not line:
                break
            gname,x,gid,y = line.split(":")
            groups[int(gid)]=gname
    
    num_procs = 0
    num_threads = 0
    num_kthreads = 0
    
    for f in glob('/proc/[0-9]*/stat'):
        try:
            with open(f, "r") as statfile:
                with open(f+"us", "r") as statusfile:
                    # Read stat info
                    stat = statfile.read().strip().split(" ")
                    
                    # Read uid/gid from status
                    status = statusfile.read()
                    
                    proc_uid = PAT_UID.findall(status)
                    proc_gid = PAT_GID.findall(status)
                    
                    proc_id = int(stat[0])
                    proc_parent = int(stat[3])
                    
                    if proc_parent == KTHREADD_PID:
                        num_kthreads+=1
                    else:
                        num_procs+=1
                        num_threads += int(stat[19])
        
        except Exception as e:
            print(e)
            print("Failed to open %s" % f)
    
    return {"procs": num_procs, "threads":num_threads, "kthreads": num_kthreads}

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
    stats = procs()
    print("%s procs %s kthreads %s threads" % (stats["procs"], stats["kthreads"], stats["threads"]))
