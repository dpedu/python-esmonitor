def uptime():
    with open("/proc/uptime", "r") as f:
        return {"uptime":int(float(f.read().split(" ")[0]))}

if __name__ == '__main__':
    print(uptime()["uptime"])
