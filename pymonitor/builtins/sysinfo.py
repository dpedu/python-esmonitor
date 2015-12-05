from subprocess import Popen,PIPE

def ipaddr():
    """
    Return first entry of hostname --all-ip-addresses
    """
    return Popen(["hostname", "--all-ip-addresses"], stdout=PIPE).communicate()[0].decode().split(" ")[0].strip()

def hostname():
    """
    Return system hostname from hostname -f
    """
    return Popen(["hostname", "-f"], stdout=PIPE).communicate()[0].decode().strip()
