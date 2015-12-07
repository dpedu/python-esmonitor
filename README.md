python-esmonitor
================
**Modular monitoring tool for logging data to elasticsearch**

Quick start
-----------

* Install: `python3 setup.py install ; pip3 install -r requirements.txt`
* Configure: `cd examples ; vim config.json`
* Run: `pymonitor -c config.json`
 
Requires the [python elasticsearch module](https://github.com/elastic/elasticsearch-py).

Configuring
-----------

The config file should contain a json object with the keys `backend` and `monitors`. Backend contains only one key, `url`. This should be the full url to elasticsearch:

```
{
    "backend": {
        "url": "http://192.168.1.210:8297/"
    },
```

The `monitors` key contains a list of monitor modules to run:

```
    "monitors": [
        {
            "type":"diskspace",
            "freq":"30",
            "args": {
                "filesystems": [
                    "/",
                    "/tmp/monitor"
                ]
            }
        },
        { ... }
    ]
}
```

The name of the module to run for a monitor is `type`. The `freq` option is the frequency, in seconds, that this monitor will check and report data. If the monitor being used takes any options, they can be passed as a object with the `args` option,

Developing Modules
------------------

**How to create a module:**

Add a new python file in *pymonitor/monitors/*, such as `uptime.py`. Add a function named the same as the file, accepting any needed params as keyword args:
```
def uptime():
```
Add your code to retrieve any metrics:
```
    with open("/proc/uptime", "r") as f:
        uptime_stats = {"uptime":int(float(f.read().split(" ")[0]))}
```
This function must yield one or more dictionaries. This dictonary will be sent as a document to elasticsearch, with a `_type` matching the name if this module ("uptime"). System hostname, ip address, and timestamp will be added automatically.
```
        yield uptime_stats
```
The module file must set a variable named `mapping`. This contains data mapping information sent to elasticsearch so our data is structured correctly. This value is used verbatim, so any other elasticsearch options for this type can be specified here.
```
mapping = {
    "uptime": {
        "properties": {
            "uptime": {
                "type": "integer"
            }
        }
    }
}
```
Finally, it's often convenient to test your monitor by adding some code so the script can be ran individually:
```
if __name__ == '__main__':
    for item in uptime():
        print(item["uptime"])
```
Since this module is named 'uptime' and takes no args, the following added to the monitors array in `config.json` would activate it:
```
{
    "type":"uptime",
    "freq":"30",
    "args":{}
}
```
Roadmap
-------

* Complete API docs
* More builtin monitors
* Local logging in case ES can't be reached
