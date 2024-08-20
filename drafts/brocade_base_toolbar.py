from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_switch_parser import BrocadeSwitchParser

class BrocadeToolbar:
    """
    Class to create a toolbar. Toolbar is a group of prometheus gauges for Brocade switch.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """

    chassis_wwn_key = ['chassis-wwn']
    switch_wwn_key = ['switch-wwn']
    switch_port_keys = ['switch-wwn', 'name', 'slot-number', 'port-number']
    chassis_switch_wwn_keys = ['chassis-wwn', 'switch-wwn']
    
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
        """  
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry


    @staticmethod
    def clone_chassis_to_vf(chassis_level_parser: dict, sw_parser: BrocadeSwitchParser, component_level=False) -> dict:
        """
        Method converts chassis_level_parser to switch_level_parser 
        by adding VF details to the chassis_level_parser or chassis components parser (fru for example).
        VF details: ['switch-name', 'switch-wwn', 'vf-id', 'fabric-user-friendly-name']

        Args:
            chassis_level_parser (dict): data to convert from chassis to switch level parser
            sw_parser (BrocadeSwitchParser): contains VF details
            component_level (bool): identify if chassis dictionary contains dictionaries with chassis components parameters
        Returns:
            dict: converted switch level parser
        """
        
        switch_level_parser = {}

        if chassis_level_parser is None:
            return
        elif not chassis_level_parser:
            return switch_level_parser
        
        # list of chassis level disctionaries (switch licenses)
        if isinstance(chassis_level_parser, list):
            # add vf_id to the switch level parser
            for vf_id, vf_details in sw_parser.vf_details.items():
                switch_level_parser[vf_id] = []
                # add switch details to each chassis dictionary of the list
                for chassis_component_dct in chassis_level_parser:
                    if not isinstance(chassis_component_dct, dict):
                        continue
                    mod_chassis_component_dct = chassis_component_dct.copy()
                    mod_chassis_component_dct.update(vf_details)
                    # add modified chassis level dictionary to the switch level parser with current vf-id key
                    switch_level_parser[vf_id].append(mod_chassis_component_dct)
        
        # chassis level dictionary
        elif isinstance(chassis_level_parser, dict):
            # add vf_id to the switch level parser
            for vf_id, vf_details in sw_parser.vf_details.items():
                switch_level_parser[vf_id] = {}
                # nested chassis components dictionaries (ps, fan, etc)
                if component_level:
                    # add switch details to each chassis component dictionary
                    for component_id, chassis_component_dct in chassis_level_parser.items():
                        mod_chassis_component_dct = chassis_component_dct.copy()
                        mod_chassis_component_dct.update(vf_details)
                        # add modified chassis component dictionary with component_id 
                        # to the switch level parser with current vf-id key
                        switch_level_parser[vf_id][component_id] = mod_chassis_component_dct
                # single chassis level dictionary (chassis parameters, ntp settings)
                else:
                    # add switch details to the chassis dictionary
                    mod_chassis_dct = chassis_level_parser.copy()
                    mod_chassis_dct.update(vf_details)
                    # add modified chassis level dictionary to the switch level parser with current vf-id key
                    switch_level_parser[vf_id] = mod_chassis_dct
        return switch_level_parser


    @property
    def sw_telemetry(self):
        return self._sw_telemetry