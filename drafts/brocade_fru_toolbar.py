from brocade_base_gauge import BrocadeGauge

from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry
from brocade_base_toolbar import BrocadeToolbar
from brocade_fru_parser import BrocadeFRUParser


class BrocadeFRUToolbar(BrocadeToolbar):
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

    fru_id_keys  =  ['chassis-wwn', 'unit-number']
    fan_id_keys = fru_id_keys + ['airflow-direction']
    sensor_keys = fru_id_keys + ['slot-number', 'index']

    FAN_STATE_ID = {0: 'absent', 1: 'ok', 2: 'below minimum', 3: 'above maximum', 4:'unknown', 5: 'not ok', 6: 'faulty'}
    PS_STATE_ID = {0: 'absent', 1: 'ok', 2: 'predicting failure', 3: 'unknown', 4: 'try reseating unit', 5: 'faulty'}
    SENSOR_STATE_ID = {0: 'absent', 1: 'ok'}

    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):

        
        super().__init__(sw_telemetry)

        # self._sw_telemetry: BrocadeSwitchTelemetry = sw_telemetry
        
        # # fan chassis name
        # self._gauge_fan_chname = BrocadeGauge(name='fan_chname', description='FAN chassis name', 
        #                                             label_keys=BrocadeFRUToolbar.chassis_name_keys)
        # # fan state gauge
        # # 0 - 'absent', 1 - 'ok', 2 - 'below minimum', 3 - 'above maximum', 4- 'unknown', 5 -'not ok', 6 - 'faulty'
        # self._gauge_fan_state = BrocadeGauge(name='fan_state', description='Status of each fan in the system', 
        #                                      label_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='operational-state-id')
        # # fan speed gauge
        # self._gauge_fan_speed = BrocadeGauge(name='fan_speed', description='Speed of each fan in the system', 
        #                                      label_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='speed')
        
        
        # # ps chassis name
        # self._gauge_ps_chname = BrocadeGauge(name='ps_chname', description='PS chassis name', 
        #                                             label_keys=BrocadeFRUToolbar.chassis_name_keys)
        # # ps state gauge
        # # 0 - 'absent', 1 - 'ok', 2 - 'predicting failure', 3 - 'unknown', 4 - 'try reseating unit', 5 - 'faulty'
        # self._gauge_ps_state = BrocadeGauge(name='ps_state', description='Status of the switch power supplies', 
        #                                      label_keys=BrocadeFRUToolbar.fru_id_keys, metric_key='operational-state-id')
        
        # # sensor chassis name
        # self._gauge_sensor_chname = BrocadeGauge(name='sensor_chname', description='Sensor chassis name', 
        #                                             label_keys=BrocadeFRUToolbar.chassis_name_keys)
        # # sensor state gauge
        # # 0 - 'absent', 1 - 'ok'
        # self._gauge_sensor_state = BrocadeGauge(name='sensor_state', description='The current operational state of the sensor', 
        #                                      label_keys=BrocadeFRUToolbar.sensor_keys, metric_key='operational-state-id')
        # # sensor temperature gauge
        # self._gauge_sensor_temp = BrocadeGauge(name='sensor_temp', description='Sensor temperature', 
        #                                      label_keys=BrocadeFRUToolbar.sensor_keys, metric_key='temperature')
        


        # fan chassis name
        self._gauge_fan_chname = BrocadeGauge(name='fan_chname', description='FAN chassis name', 
                                                    unit_keys=BrocadeFRUToolbar.chassis_wwn_key, parameter_key='chassis-name')
        # fan state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'below minimum', 3 - 'above maximum', 4- 'unknown', 5 -'not ok', 6 - 'faulty'
        fan_state_description = f'Status of each fan in the system {BrocadeFRUToolbar.FAN_STATE_ID}'
        self._gauge_fan_state = BrocadeGauge(name='fan_state', description=fan_state_description, 
                                             unit_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='operational-state-id')
        # fan speed gauge
        self._gauge_fan_speed = BrocadeGauge(name='fan_speed', description='Speed of each fan in the system', 
                                             unit_keys=BrocadeFRUToolbar.fan_id_keys, metric_key='speed')
        
        
        # ps chassis name
        self._gauge_ps_chname = BrocadeGauge(name='ps_chname', description='PS chassis name', 
                                                    unit_keys=BrocadeFRUToolbar.chassis_wwn_key, parameter_key='chassis-name')
        # ps state gauge
        # 0 - 'absent', 1 - 'ok', 2 - 'predicting failure', 3 - 'unknown', 4 - 'try reseating unit', 5 - 'faulty'
        ps_state_description = f'Status of the switch power supplies {BrocadeFRUToolbar.PS_STATE_ID}'
        self._gauge_ps_state = BrocadeGauge(name='ps_state', description=ps_state_description, 
                                             unit_keys=BrocadeFRUToolbar.fru_id_keys, metric_key='operational-state-id')
        
        # sensor chassis name
        self._gauge_sensor_chname = BrocadeGauge(name='sensor_chname', description='Sensor chassis name', 
                                                    unit_keys=BrocadeFRUToolbar.chassis_wwn_key, parameter_key='chassis-name')
        # sensor state gauge
        # 0 - 'absent', 1 - 'ok'
        sensor_state_description = f'The current operational state of the sensor {BrocadeFRUToolbar.SENSOR_STATE_ID}'
        self._gauge_sensor_state = BrocadeGauge(name='sensor_state', description=sensor_state_description, 
                                             unit_keys=BrocadeFRUToolbar.sensor_keys, metric_key='operational-state-id')
        # sensor temperature gauge
        self._gauge_sensor_temp = BrocadeGauge(name='sensor_temp', description='Sensor temperature', 
                                             unit_keys=BrocadeFRUToolbar.sensor_keys, metric_key='temperature')


    def fill_toolbar_gauge_metrics(self, fru_parser: BrocadeFRUParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            fru_parser (BrocadeFRUParser): object contains required data to fill the gauge metrics.
        """
        
        self.gauge_fan_chame.fill_chassis_gauge_metrics(fru_parser.fru_fan)
        self.gauge_fan_state.fill_chassis_gauge_metrics(fru_parser.fru_fan)
        self.gauge_fan_speed.fill_chassis_gauge_metrics(fru_parser.fru_fan)
        self.gauge_ps_chame.fill_chassis_gauge_metrics(fru_parser.fru_ps)
        self.gauge_ps_state.fill_chassis_gauge_metrics(fru_parser.fru_ps)
        self.gauge_sensor_chame.fill_chassis_gauge_metrics(fru_parser.fru_sensor)
        self.gauge_sensor_state.fill_chassis_gauge_metrics(fru_parser.fru_sensor)
        self.gauge_sensor_temp.fill_chassis_gauge_metrics(fru_parser.fru_sensor)



    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    # @property
    # def sw_telemetry(self):
    #     return self._sw_telemetry


    @property
    def gauge_fan_chame(self):
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