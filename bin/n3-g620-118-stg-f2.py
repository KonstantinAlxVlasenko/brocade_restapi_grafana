"""
SAN: Ost_stg
Fabric: B
Switch name: n3-g620-118-stg-f2
Switch IP: 10.213.164.102
"""

from switch_metrics_collection import collect_switch_metrics

if __name__ == '__main__':
    collect_switch_metrics(sw_ipaddress="10.213.164.102")
