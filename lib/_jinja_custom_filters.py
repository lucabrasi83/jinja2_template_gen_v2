from ipaddress import IPv4Network, IPv4Address


# Jinja2 Custom Filters
def jinj_getipfromsub(input, position):
    input = IPv4Network(input)
    _ip = input[position]
    return str(_ip)


def jinj_getnextip(input):
    input = IPv4Address(input)
    _ip = input + 1
    return str(_ip)


def jinj_getiffullname(input, vlanid):
    interface_name = input + '.' + str(vlanid)
    return interface_name


def jinj_convbps2mbps(input):
    input *= 1000000
    input = round(input)
    return str(input)


def jinj_convmbps2kbps(input):
    input *= 1000
    input = round(input)
    return str(input)


def jinj_getnetworkadd(input):
    input = IPv4Network(input)
    net_address = input.network_address
    return str(net_address)


def jinj_getwildcardmask(input):
    input = IPv4Network(input)
    wildcard_mask = input.hostmask
    return str(wildcard_mask)
