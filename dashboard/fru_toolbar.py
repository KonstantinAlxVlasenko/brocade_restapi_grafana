from .base_gauge import BaseGauge
from .base_toolbar import BaseToolbar

from collection.switch_telemetry_request import SwitchTelemetryRequest

from parser.switch_parser import SwitchParser
from parser.fru_parser import FRUParser


class FRUToolbar(BaseToolbar):
    """
    Class to create field replaceable units (FRU) toolbar.
    FRU Toolbar is a set of prometheus gauges:
    fan state, fan speed, ps state, sensor state, sensor temperature.
    Each unique ps identified by chassis wwn, unit-number.
    Each unique fan identified by chassis wwn, unit-number, airflow-direction.
    Each unique sensor identified by chassis wwn, unit-number, slot-number, index.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch
    """

    # fru_id_keys  =  ['chassis-wwn', 'unit-number']

    fru_id_keys  =  ['chassis-wwn', 'switch-wwn', 'unit-number']

    fan_id_keys = fru_id_keys + ['airflow-direction']
    sensor_keys = fru_id_keys + ['slot-number', 'index']

    FAN_STATE_ID = {0: 'absent', 1: 'ok', 2: 'below minimum', 3: 'above maximum', 4:'unknown', 5: 'not ok', 6: 'faulty'}
    PS_STATE_ID = {0: 'absent', 1: 'ok', 2: 'predicting failure', 3: 'unknown', 4: 'try reseating unit', 5: 'faulty'}
    SENSOR_STATE_ID = {0: 'absent', 1: 'ok'}


    def __init__(self, sw_telemetry: SwitchTelemetryRequest):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch.
        """
        
        super().__init__(sw_telemetry)

        # fan chassis name
        self._gauge_fan_chname = BaseGauge(name='fan_chname', description='FAN chassis name', 
                                                    unit_keys=FRUToolbar.chassis_switch_wwn_keys, parameter_key='chassis-name')
        
        self._gauge_fan_swname = BaseGauge(name='fan_swname', description='FAN switch name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='switch-name')
        self._gauge_fan_fabricname = BaseGauge(name='fan_fabric_name', description='FAN fabric name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_fan_vfid = BaseGauge(name='fan_vfid', description='FAN VF ids', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, metric_key='vf-id')
        # fan state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'below minimum', 3 - 'above maximum', 4- 'unknown', 5 -'not ok', 6 - 'faulty'
        fan_state_description = f'Status of each fan in the system {FRUToolbar.FAN_STATE_ID}'
        self._gauge_fan_state = BaseGauge(name='fan_state', description=fan_state_description, 
                                             unit_keys=FRUToolbar.fan_id_keys, metric_key='operational-state-id')
        # fan speed gauge
        self._gauge_fan_speed = BaseGauge(name='fan_speed', description='Speed of each fan in the system', 
                                             unit_keys=FRUToolbar.fan_id_keys, metric_key='speed')
        # ps chassis name
        self._gauge_ps_chname = BaseGauge(name='ps_chname', description='PS chassis name', 
                                                    unit_keys=FRUToolbar.chassis_switch_wwn_keys, parameter_key='chassis-name')
        self._gauge_ps_swname = BaseGauge(name='ps_swname', description='PS switch name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='switch-name')
        self._gauge_ps_fabricname = BaseGauge(name='ps_fabric_name', description='PS fabric name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_ps_vfid = BaseGauge(name='ps_vfid', description='PS VF ids', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, metric_key='vf-id')
        # ps state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'predicting failure', 3 - 'unknown', 4 - 'try reseating unit', 5 - 'faulty'
        ps_state_description = f'Status of the switch power supplies {FRUToolbar.PS_STATE_ID}'
        self._gauge_ps_state = BaseGauge(name='ps_state', description=ps_state_description, 
                                             unit_keys=FRUToolbar.fru_id_keys, metric_key='operational-state-id')
        # sensor chassis name
        self._gauge_sensor_chname = BaseGauge(name='sensor_chname', description='Sensor chassis name', 
                                                    unit_keys=FRUToolbar.chassis_switch_wwn_keys, parameter_key='chassis-name')
        self._gauge_sensor_swname = BaseGauge(name='sensor_swname', description='Sensor switch name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='switch-name')
        self._gauge_sensor_fabricname = BaseGauge(name='sensor_fabric_name', description='Sensor fabric name', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # vf id
        self._gauge_sensor_vfid = BaseGauge(name='sensor_vfid', description='Sensor VF ids', 
                                                    unit_keys=FRUToolbar.switch_wwn_key, metric_key='vf-id')
        # sensor state gauge
        # 0 - 'absent', 1 - 'ok'
        sensor_state_description = f'The current operational state of the sensor {FRUToolbar.SENSOR_STATE_ID}'
        self._gauge_sensor_state = BaseGauge(name='sensor_state', description=sensor_state_description, 
                                             unit_keys=FRUToolbar.sensor_keys, metric_key='operational-state-id')
        # sensor temperature gauge
        self._gauge_sensor_temp = BaseGauge(name='sensor_temp', description='Sensor temperature', 
                                             unit_keys=FRUToolbar.sensor_keys, metric_key='temperature')


    def fill_toolbar_gauge_metrics(self, fru_parser: FRUParser, sw_parser: SwitchParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            fru_parser (BrocadeFRUParser): object contains required data to fill the gauge metrics.
            sw_parser (BrocadeSwitchParser): object contains vf details.
        """
        
        # copy fru params to all virtual switches
        fru_ps = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_ps, sw_parser, component_level=True)
        fru_fan = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_fan, sw_parser, component_level=True)
        fru_sensor = BaseToolbar.clone_chassis_to_vf(fru_parser.fru_sensor, sw_parser, component_level=True)

        fan_gauge_lst = [self.gauge_fan_chname, self.gauge_fan_swname, self.gauge_fan_fabricname, 
                         self.gauge_fan_vfid, self.gauge_fan_state, self.gauge_fan_speed]
        
        ps_gauge_lst = [self.gauge_ps_chame, self.gauge_ps_swname, self.gauge_ps_fabricname,
                        self.gauge_ps_vfid, self.gauge_ps_state]
        
        sensor_gauge_lst = [self.gauge_sensor_chame, self.gauge_sensor_swname, self.gauge_sensor_fabricname, 
                            self.gauge_sensor_vfid, self.gauge_sensor_state, self.gauge_sensor_temp]


        for gauge in fan_gauge_lst:
            gauge.fill_port_gauge_metrics(fru_fan)

        for gauge in ps_gauge_lst:
            gauge.fill_port_gauge_metrics(fru_ps)

        for gauge in sensor_gauge_lst:
            gauge.fill_port_gauge_metrics(fru_sensor)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_fan_chname(self):
        return self._gauge_fan_chname


    @property
    def gauge_fan_state(self):
        return self._gauge_fan_state
    

    @property
    def gauge_fan_speed(self):
        return self._gauge_fan_speed
    

    @property
    def gauge_ps_chame(self):
        return self._gauge_ps_chname


    @property
    def gauge_ps_state(self):
        return self._gauge_ps_state


    @property
    def gauge_sensor_chame(self):
        return self._gauge_sensor_chname


    @property
    def gauge_sensor_state(self):
        return self._gauge_sensor_state


    @property
    def gauge_sensor_temp(self):
        return self._gauge_sensor_temp
    

    @property
    def gauge_fan_swname(self):
        return self._gauge_fan_swname


    @property
    def gauge_fan_fabricname(self):
        return self._gauge_fan_fabricname
    
    @property
    def gauge_fan_vfid(self):
        return self._gauge_fan_vfid
    

    @property
    def gauge_ps_swname(self):
        return self._gauge_ps_swname


    @property
    def gauge_ps_fabricname(self):
        return self._gauge_ps_fabricname
    

    @property
    def gauge_ps_vfid(self):
        return self._gauge_ps_vfid


    @property
    def gauge_sensor_swname(self):
        return self._gauge_sensor_swname


    @property
    def gauge_sensor_fabricname(self):
        return self._gauge_sensor_fabricname
    

    @property
    def gauge_sensor_vfid(self):
        return self._gauge_sensor_vfid