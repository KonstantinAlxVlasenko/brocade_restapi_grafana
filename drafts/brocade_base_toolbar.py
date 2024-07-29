from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeToolbar:

    chassis_wwn_key = ['chassis-wwn']
    switch_wwn_key = ['switch-wwn']
    # chassis_name_keys = chassis_wwn_key +   ['chassis-name']
    # switch_name_keys = switch_wwn_key +  ['switch-name']
    # switch_ip_keys = ['switch-wwn', 'ip-address']
    # switch_fabric_name_keys = ['switch-wwn', 'fabric-user-friendly-name']
    switch_port_keys = ['switch-wwn', 'name', 'slot-number', 'port-number']

    
    
    PORT_PHYSICAL_STATE_ID = {0: 'Offline', 1: 'Online', 2: 'Testing', 3: 'Faulty', 4: 'E_Port', 5: 'F_Port', 
                            6: 'Segmented', 7: 'Unknown',8: 'No_Port', 9: 'No_Module', 10: 'Laser_Flt', 
                            11: 'No_Light', 12: 'No_Sync', 13: 'In_Sync', 14: 'Port_Flt', 15: 'Hard_Flt', 
                            16: 'Diag_Flt', 17: 'Lock_Ref', 18: 'Mod_Inv', 19: 'Mod_Val', 20: 'No_Sigdet', 
                            100: 'Unknown_ID'}
    
    PORT_TYPE_ID = {0: 'Unknown', 7: 'E-Port', 10: 'G-Port', 11: 'U-Port', 15: 'F-Port', 16: 'L-Port',
                    17: 'FCoE Port', 19: 'EX-Port', 20: 'D-Port', 21: 'SIM Port', 22: 'AF-Port',
                    23: 'AE-Port', 25: 'VE-Port', 26: 'Ethernet Flex Port', 29: 'Flex Port',
                    30: 'N-Port', 32768: 'LB-Port'}
    
    SPEED_MODE_ID = {0: 'G', 1: 'N'}

    
    STATUS_ID = {1: 'OK', 2: 'Unknown', 3: 'Warning', 4: 'Critical'}

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry) -> None:
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

    @property
    def sw_telemetry(self):
        return self._sw_telemetry