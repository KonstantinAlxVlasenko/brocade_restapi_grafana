from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeToolbar:

    chassis_wwn_key = ['chassis-wwn']
    switch_wwn_key = ['switch-wwn']
    chassis_name_keys = chassis_wwn_key +   ['chassis-name']
    switch_name_keys = switch_wwn_key +  ['switch-name']


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry) -> None:
        
        self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry

    @property
    def sw_telemetry(self):
        return self._sw_telemetry