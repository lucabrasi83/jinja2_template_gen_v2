from ipaddress import IPv4Network, IPv4Address


# Jinja2 Custom Filters
def getipfromsub(input, position):
    input = IPv4Network(input)
    _ip = input[position]
    return str(_ip)


def getnextip(input):
    input = IPv4Address(input)
    _ip = input + 1
    return str(_ip)


def getiffullname(input, vlanid):
    interface_name = input + '.' + str(vlanid)
    return interface_name


def convbps2mbps(input):
    input *= 1000000
    input = round(input)
    return str(input)
