"""
SAN: Ost_stg
Fabric: A
Switch name: n3-g620-117-stg-f1
Switch IP: 10.213.164.101
"""


from switch_metrics_collection import collect_switch_metrics

if __name__ == '__main__':
    collect_switch_metrics(sw_ipaddress="10.213.164.101")
