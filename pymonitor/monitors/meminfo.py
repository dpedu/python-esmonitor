import re

memline_pattern = re.compile(r'^(?P<key>[^\\:]+)\:\s+(?P<value>[0-9]+)(\s(?P<unit>[a-zA-Z]+))?')

computed_fields = {
    "mempctused": lambda items: round((items["memtotal"]-items["memfree"])/items["memtotal"], 2),
    "mempctfree": lambda items: 1-round((items["memtotal"]-items["memfree"])/items["memtotal"], 2),
    "mempctused_nocache": lambda items: round((items["memtotal"]-items["memfree"]-items["cached"])/items["memtotal"], 2),
    "mempctfree_nocache": lambda items: 1-round((items["memtotal"]-items["memfree"]-items["cached"])/items["memtotal"], 2),
    "swappctused": lambda items: round((items["swaptotal"]-items["swapfree"])/items["swaptotal"], 2),
    "swappctfree": lambda items: 1-round((items["swaptotal"]-items["swapfree"])/items["swaptotal"], 2)
}

def meminfo(whitelist=[]):
    if not whitelist:
        whitelist = ["swaptotal", "swapfree", "swapcached", 
                     "memtotal", "memfree", "cached", 
                     "active", "inactive", ]
        
    result = {}
    with open("/proc/meminfo", "r") as f:
        for line in f.read().strip().split("\n"):
            matches = memline_pattern.match(line)
            
            value = int(matches.group("value"))
            unit = matches.group("unit")
            
            if unit:
                if unit == "kB":
                    value*=1024
                else:
                    raise Exception("Unknown unit")
            
            name = ''.join(c for c in matches.group("key").lower() if 96<ord(c)<123)
            if name in whitelist:
                result[name] = value
            
        for key in computed_fields:
            result[key] = computed_fields[key](result)
    
    yield result

mapping = {
    "meminfo": {
        "properties": {
            "swaptotal":    { "type": "long" },
            "swapfree":     { "type": "long" },
            "swapcached":   { "type": "long" },
            "memtotal":     { "type": "long" },
            "memfree":      { "type": "long" },
            "memavailable": { "type": "long" },
            "cached":       { "type": "long" },
            "active":       { "type": "long" },
            "inactive":     { "type": "long" },
            "mempctused":   { "type": "double" },
            "mempctfree":   { "type": "double" },
            "mempctused_nocache": { "type": "double" },
            "mempctfree_nocache": { "type": "double" },
            "swappctused":  { "type": "double" },
            "swappctfree":  { "type": "double" }
        }
    }
}

if __name__ == '__main__':
    for item in meminfo():
        for k,v in item.items():
            print("%s: %s"%(k,v))
