def uptime():
    with open("/proc/uptime", "r") as f:
        return {"uptime":int(float(f.read().split(" ")[0]))}

mapping = {
    "uptime": {
        "properties": {
            "uptime": {
                "type": "integer"
            }
        }
    }
}

if __name__ == '__main__':
    print(uptime()["uptime"])
