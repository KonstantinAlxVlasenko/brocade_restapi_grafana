from brocade_base_gauge import BrocadeGauge
from brocade_base_toolbar import BrocadeToolbar
from brocade_fcport_stats_parser import BrocadeFCPortStatisticsParser
from switch_telemetry_httpx_cls import BrocadeSwitchTelemetry


class BrocadeFCPortStatsToolbar(BrocadeToolbar):
    """
    Class to create fc port statistics toolbar.
    FC port statistics Toolbar is a set of prometheus gauges:
    number of frames received and transmitted at this port, 
    port errors, port errors status for high, medium and low errors,
    io rates and io rate status.

    Each unique port identified by 'switch-wwn', 'name', 'slot-number', 'port-number'.

    Attributes:
        sw_telemetry: set of switch telemetry retrieved from the switch.
    """


    def __init__(self, sw_telemetry: BrocadeSwitchTelemetry):
        """
        Args:
            sw_telemetry: set of switch telemetry retrieved from the switch
        """

        super().__init__(sw_telemetry)

        # sfp media switch name gauge
        self._gauge_swname = BrocadeGauge(name='fcport_stats_switchname', description='Switch name in the SFP media output.', 
                                          unit_keys=BrocadeFCPortStatsToolbar.switch_wwn_key, parameter_key='switch-name')
        # sfp media fabric name gauge
        self._gauge_fabricname = BrocadeGauge(name='fcport_stats_fabricname', description='Fabric name in the SFP media output.', 
                                              unit_keys=BrocadeFCPortStatsToolbar.switch_wwn_key, parameter_key='fabric-user-friendly-name')
        # sfp media port name gauge
        self._gauge_portname = BrocadeGauge(name='fcport_stats_portname', description='Port name in the SFP media output.',
                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, parameter_key='port-name')  
        # sfp media switch VF ID gauge
        self._gauge_switch_vfid = BrocadeGauge(name='fcport_stats_switch_vfid', description='Switch virtual fabric ID in the SFP media output.', 
                                               unit_keys=BrocadeFCPortStatsToolbar.switch_wwn_key, metric_key='vf-id')
        # sfp media port speed gbps gauge
        self._gauge_port_speed_value = BrocadeGauge(name='fcport_stats_port_speed_value', description='The speed of the port.', 
                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key='port-speed-gbps')
        # sfp media port speed mode gauge
        # 0 - 'G', 1 - 'N'
        speed_mode_description = f'Whether the port speed is auto-negotiated on the specified port {BrocadeFCPortStatsToolbar.SPEED_MODE_ID}.'
        self._gauge_port_speed_mode = BrocadeGauge(name='fcport_stats_port_speed_mode', description=speed_mode_description, 
                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key='auto-negotiate')
        # sfp media physical state gauge
        # 0 - 'Offline', 1 - 'Online', 2 - 'Testing', 3 - 'Faulty', 4 - 'E_port', 5 - 'F_port', 
        # 6 - 'Segmented', 7 - 'Unknown', 8 - 'No_port', 9 - 'No_module', 10 - 'Laser_flt',
        # 11 - 'No_light', 12 - 'No_sync', 13 - 'In_sync', 14 - 'Port_flt', 15 - 'Hard_flt',
        # 16 - 'Diag_flt', 17 - 'Lock_ref', 18 - 'Mod_inv', 19 - 'Mod_val', 20 - 'No_sigdet'
        # 100 - 'Unknown_ID'
        port_physical_state_description = f'The physical state of a port {BrocadeFCPortStatsToolbar.PORT_PHYSICAL_STATE_ID}.'
        self._gauge_port_physical_state = BrocadeGauge(name='fcport_stats_physical_state', description=port_physical_state_description,
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key='physical-state-id')
        # sfp media port type gauge
        # 0 - 'Unknown', 7 - 'E_Port', 10 - 'G_Port', 11 - 'U_Port', 15 - 'F_Port',
        # 16 - 'L_Port', 17 - 'FCoE Port', 19 - 'EX_Port', 20 - 'D_Port', 21 - 'SIM Port',
        # 22 - 'AF_Port', 23 - 'AE_Port', 25 - 'VE_Port', 26 - 'Ethernet Flex Port',
        # 29 - 'Flex Port', 30 - 'N_Port', 32768 - 'LB_Port'
        port_type_description = f'The port type currently enabled for the specified port {BrocadeFCPortStatsToolbar.PORT_TYPE_ID}.'
        self._gauge_port_type = BrocadeGauge(name='fcport_stats_port_type', description=port_type_description,
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key='port-type-id')
        # port max speed gauge
        self._gauge_max_speed = BrocadeGauge(name="fcport_stats_max_speed", description="The maximum speed the port is capable of supporting in bits per second.", 
                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="max-speed")

        # number of received frames
        self._gauge_class_3_frames = BrocadeGauge(name="fcport_stats_class_3_frames", description="The number of Class 3 frames received at this port (stat_c3_frx).", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class-3-frames")
        self._gauge_class_3_frames_delta = BrocadeGauge(name="fcport_stats_class_3_frames_delta", description="Delta of Class 3 frames received at this port (stat_c3_frx).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class-3-frames-delta")
        self._gauge_in_frames = BrocadeGauge(name="fcport_stats_in_frames", description="The number of frames received at this port (stat_frx).", 
                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-frames")
        self._gauge_in_frames_delta = BrocadeGauge(name="fcport_stats_in_frames_delta", description="Delta of frames received at this port (stat_frx).", 
                                                   unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-frames-delta")
        # number of transmitted frames
        self._gauge_out_frames = BrocadeGauge(name="fcport_stats_out_frames", description="The number of frames transmitted from this port (stat_ftx).", 
                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-frames")
        self._gauge_out_frames_delta = BrocadeGauge(name="fcport_stats_out_frames_delta", description="Delta of frames transmitted from this port (stat_ftx).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-frames-delta")
        # port errors
        self._gauge_address_errors = BrocadeGauge(name="fcport_stats_address_errors", description="Count of frames received with unknown addressing (portshow Address_err).", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="address-errors")
        self._gauge_address_errors_delta = BrocadeGauge(name="fcport_stats_address_errors_delta", description="Delta of frames received with unknown addressing (portshow Address_err).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="address-errors-delta")
        self._gauge_bad_eofs_received = BrocadeGauge(name="fcport_stats_bad_eofs_received", description="The number of bad EOF frames received (er_bad_os).", 
                                                     unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="bad-eofs-received")
        self._gauge_bad_eofs_received_delta = BrocadeGauge(name="fcport_stats_bad_eofs_received_delta", description="Delta of bad EOF frames received (er_bad_os).", 
                                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="bad-eofs-received-delta")
        self._gauge_bb_credit_zero = BrocadeGauge(name="fcport_stats_bb_credit_zero", description="The number of transitions in and out of the BB credit zero state (tim_txcrd_z).", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="bb-credit-zero")
        self._gauge_bb_credit_zero_delta = BrocadeGauge(name="fcport_stats_bb_credit_zero_delta", description="Delta of transitions in and out of the BB credit zero state (tim_txcrd_z).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="bb-credit-zero-delta")
        self._gauge_class3_in_discards = BrocadeGauge(name="fcport_stats_class3_in_discards", description="The number of class 3 receive frames discarded due to timeout (er_rx_c3_timeout).", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class3-in-discards")
        self._gauge_class3_in_discards_delta = BrocadeGauge(name="fcport_stats_class3_in_discards_delta", description="Delta of class 3 receive frames discarded due to timeout (er_rx_c3_timeout).", 
                                                            unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class3-in-discards-delta")
        self._gauge_class3_out_discards = BrocadeGauge(name="fcport_stats_class3_out_discards", description="The number of class 3 transmit frames discarded due to timeout (er_tx_c3_timeout).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class3-out-discards")
        self._gauge_class3_out_discards_delta = BrocadeGauge(name="fcport_stats_class3_out_discards_delta", description="Delta of class 3 transmit frames discarded due to timeout (er_tx_c3_timeout).", 
                                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class3-out-discards-delta")
        self._gauge_class_3_discards = BrocadeGauge(name="fcport_stats_class_3_discards", description="The number of Class 3 frames discarded by this port (er_rx_c3_timeout + er_tx_c3_timeout).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class-3-discards")
        self._gauge_class_3_discards_delta = BrocadeGauge(name="fcport_stats_class_3_discards_delta", description="Delta of Class 3 frames discarded by this port (er_rx_c3_timeout + er_tx_c3_timeout).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="class-3-discards-delta")
        self._gauge_crc_errors = BrocadeGauge(name="fcport_stats_crc_errors", description="The number of times that the CRC in a frame does not match the CRC that is computed by the receiver (er_crc).", 
                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="crc-errors")
        self._gauge_crc_errors_delta = BrocadeGauge(name="fcport_stats_crc_errors_delta", description="Delta of times that the CRC in a frame does not match the CRC that is computed by the receiver (er_crc).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="crc-errors-delta")
        self._gauge_delimiter_errors = BrocadeGauge(name="fcport_stats_delimiter_errors", 
                                                    description="Count of invalid frame delimiters that are received at this port. An example would be a frame that has a class 2 at the start and a class 3 at the end (portshow Delim_err).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="delimiter-errors")
        self._gauge_delimiter_errors_delta = BrocadeGauge(name="fcport_stats_delimiter_errors_delta", 
                                                          description="Delta of invalid frame delimiters that are received at this port. An example would be a frame that has a class 2 at the start and a class 3 at the end (portshow Delim_err).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="delimiter-errors-delta")
        self._gauge_encoding_disparity_errors = BrocadeGauge(name="fcport_stats_encoding_disparity_errors", description="The total number of disparity errors received at this port (er_enc_in).", 
                                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="encoding-disparity-errors")
        self._gauge_encoding_disparity_errors_delta = BrocadeGauge(name="fcport_stats_encoding_disparity_errors_delta", description="Delta number of disparity errors received at this port (er_enc_in).", 
                                                                   unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="encoding-disparity-errors-delta")
        self._gauge_encoding_errors_outside_frame = BrocadeGauge(name="fcport_stats_encoding_errors_outside_frame", description="The number of encoding-error or disparity-error outside frames received (er_enc_out).", 
                                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="encoding-errors-outside-frame")
        self._gauge_encoding_errors_outside_frame_delta = BrocadeGauge(name="fcport_stats_encoding_errors_outside_frame_delta", description="Delta of encoding-error or disparity-error outside frames received (er_enc_out).", 
                                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="encoding-errors-outside-frame-delta")
        self._gauge_f_busy_frames = BrocadeGauge(name="fcport_stats_f_busy_frames", description="The number of F_BSY (fabric busy) frames generated (portshow Fbsy).", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="f-busy-frames")
        self._gauge_f_busy_frames_delta = BrocadeGauge(name="fcport_stats_f_busy_frames_delta", description="Delta of F_BSY (fabric busy) frames generated (portshow Fbsy).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="f-busy-frames-delta")
        self._gauge_f_rjt_frames = BrocadeGauge(name="fcport_stats_f_rjt_frames", description="The number of F_RJT (fabric frame reject) frames generated (portshow Frjt).", 
                                                unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="f-rjt-frames")
        self._gauge_f_rjt_frames_delta = BrocadeGauge(name="fcport_stats_f_rjt_frames_delta", description="Delta of F_RJT (fabric frame reject) frames generated (portshow Frjt).", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="f-rjt-frames-delta")
        self._gauge_frames_processing_required = BrocadeGauge(name="fcport_stats_frames_processing_required", description="The number of frames which required processing on the port (portshow Proc_rqrd).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-processing-required")
        self._gauge_frames_processing_required_delta = BrocadeGauge(name="fcport_stats_frames_processing_required_delta", description="Delta of frames which required processing on the port (portshow Proc_rqrd).", 
                                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-processing-required-delta")
        self._gauge_frames_timed_out = BrocadeGauge(name="fcport_stats_frames_timed_out", description="The number of frames which timed out during transmit on the port (portshow Timed_out).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-timed-out")
        self._gauge_frames_timed_out_delta = BrocadeGauge(name="fcport_stats_frames_timed_out_delta", description="Delta of frames which timed out during transmit on the port (portshow Timed_out).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-timed-out-delta")
        self._gauge_frames_too_long = BrocadeGauge(name="fcport_stats_frames_too_long", description="The number of frames longer than the maximum frame length (er_toolong).", 
                                                   unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-too-long")
        self._gauge_frames_too_long_delta = BrocadeGauge(name="fcport_stats_frames_too_long_delta", description="Delta of frames longer than the maximum frame length (er_toolong).", 
                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-too-long-delta")
        self._gauge_frames_transmitter_unavailable_errors = BrocadeGauge(name="fcport_stats_frames_transmitter_unavailable_errors", description="The number of frames returned by an unavailable transmitter (portshow Tx_unavail).", 
                                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-transmitter-unavailable-errors")
        self._gauge_frames_transmitter_unavailable_errors_delta = BrocadeGauge(name="fcport_stats_frames_transmitter_unavailable_errors_delta", description="Delta of frames returned by an unavailable transmitter (portshow Tx_unavail).", 
                                                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="frames-transmitter-unavailable-errors-delta")
        self._gauge_in_crc_errors = BrocadeGauge(name="fcport_stats_in_crc_errors", description="The number of CRC errors for all frames received (portshow Invalid_crc).", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-crc-errors")
        self._gauge_in_crc_errors_delta = BrocadeGauge(name="fcport_stats_in_crc_errors_delta", description="Delta of CRC errors for all frames received (portshow Invalid_crc).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-crc-errors-delta")
        self._gauge_in_lcs = BrocadeGauge(name="fcport_stats_in_lcs", description="The number of link control (lcs) frames received (stat_lc_rx).", 
                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-lcs")
        self._gauge_in_lcs_delta = BrocadeGauge(name="fcport_stats_in_lcs_delta", description="Delta of link control (lcs) frames received (stat_lc_rx).", 
                                                unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-lcs-delta")
        self._gauge_invalid_ordered_sets = BrocadeGauge(name="fcport_stats_invalid_ordered_sets", description="The total number of invalid ordered sets received (er_bad_os).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="invalid-ordered-sets")
        self._gauge_invalid_ordered_sets_delta = BrocadeGauge(name="fcport_stats_invalid_ordered_sets_delta", description="Delta of invalid ordered sets received (er_bad_os).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="invalid-ordered-sets-delta")
        self._gauge_invalid_transmission_words = BrocadeGauge(name="fcport_stats_invalid_transmission_words", description="The number of invalid transmission words received at this port (portshow Invalid_word).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="invalid-transmission-words")
        self._gauge_invalid_transmission_words_delta = BrocadeGauge(name="fcport_stats_invalid_transmission_words_delta", description="Delta of invalid transmission words received at this port (portshow Invalid_word).", 
                                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="invalid-transmission-words-delta")
        self._gauge_link_level_interrpts = BrocadeGauge(name="fcport_stats_link_level_interrpts", description="Total number of interrupts (portshow Interrupts).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="link-level-interrpts")
        self._gauge_link_level_interrpts_delta = BrocadeGauge(name="fcport_stats_link_level_interrpts_delta", description="Delta of interrupts (portshow Interrupts).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="link-level-interrpts-delta")
        self._gauge_multicast_timeouts = BrocadeGauge(name="fcport_stats_multicast_timeouts", description="The number of multicast frames that have timed out (er_multi_credit_loss).", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="multicast-timeouts")
        self._gauge_multicast_timeouts_delta = BrocadeGauge(name="fcport_stats_multicast_timeouts_delta", description="Delta of multicast frames that have timed out (er_multi_credit_loss).", 
                                                            unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="multicast-timeouts-delta")
        self._gauge_pcs_block_errors = BrocadeGauge(name="fcport_stats_pcs_block_errors", 
                                                    description="The number of physical coding sublayer (PCS) block errors. This counter records encoding violations on 10-Gb/s or 16-Gb/s ports (er_pcs_blk).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="pcs-block-errors")
        self._gauge_pcs_block_errors_delta = BrocadeGauge(name="fcport_stats_pcs_block_errors_delta", 
                                                          description="Delta of physical coding sublayer (PCS) block errors. This counter records encoding violations on 10-Gb/s or 16-Gb/s ports (er_pcs_blk).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="pcs-block-errors-delta")
        self._gauge_primitive_sequence_protocol_error = BrocadeGauge(name="fcport_stats_primitive_sequence_protocol_error", 
                                                                     description="The number of primitive sequence protocol errors detected at this port (portshow Protocol_err).", 
                                                                     unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="primitive-sequence-protocol-error")
        self._gauge_primitive_sequence_protocol_error_delta = BrocadeGauge(name="fcport_stats_primitive_sequence_protocol_error_delta", 
                                                                           description="Delta of primitive sequence protocol errors detected at this port (portshow Protocol_err).", 
                                                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="primitive-sequence-protocol-error-delta")
        
        # Link reset on the remote switch (Lr_in)
        self._gauge_in_link_resets = BrocadeGauge(name="fcport_stats_in_link_resets", description="The number of link resets received (portshow Lr_in).", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-link-resets")
        self._gauge_in_link_resets_delta = BrocadeGauge(name="fcport_stats_in_link_resets_delta", description="Delta of link resets received (portshow Lr_in).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-link-resets-delta")
        # Number of Offline Primitive OLS received (Ols_in)
        self._gauge_in_offline_sequences = BrocadeGauge(name="fcport_stats_in_offline_sequences", description="The total number of offline sequences received (portshow Ols_in).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-offline-sequences")
        self._gauge_in_offline_sequences_delta = BrocadeGauge(name="fcport_stats_in_offline_sequences_delta", description="Delta of offline sequences received (portshow Ols_in).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-offline-sequences-delta")
        # Link reset on the local switch (Lr_out)
        self._gauge_out_link_resets = BrocadeGauge(name="fcport_stats_out_link_resets", description="The total number of link resets transmitted (portshow Lr_out).", 
                                                   unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-link-resets")
        self._gauge_out_link_resets_delta = BrocadeGauge(name="fcport_stats_out_link_resets_delta", description="Delta of link resets transmitted (portshow Lr_out).", 
                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-link-resets-delta")
        # Number of Offline Primitive OLS transmitted (Ols_out)
        self._gauge_out_offline_sequences = BrocadeGauge(name="fcport_stats_out_offline_sequences", description="The total number of offline sequences transmitted (portshow Ols_out).", 
                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-offline-sequences")
        self._gauge_out_offline_sequences_delta = BrocadeGauge(name="fcport_stats_out_offline_sequences_delta", description="Delta of offline sequences transmitted (portshow Ols_out).", 
                                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-offline-sequences-delta")
        # Difference between delta Lr_in and delta Ols_out
        self._gauge_lrin_delta_subtract_olsout_delta = BrocadeGauge(name="fcport_stats_lrin_delta_subtract_olsout_delta", 
                                                                    description="Difference between delta of link resets received (portshow Lr_in) and delta of offline sequences transmitted (portshow Ols_out).", 
                                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="lrin-delta_subtract_olsout-delta")
        # Difference between delta Lr_out and delta Ols_in
        self._gauge_lrout_delta_subtract_olsin_delta = BrocadeGauge(name="fcport_stats_lrout_delta_subtract_olsin_delta", 
                                                                    description="Difference between delta of link resets transmitted (portshow Lr_out) and delta of offline sequences received (portshow Ols_in).", 
                                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="lrout-delta_subtract_olsin-delta")
        # Number of link failures (Link_failure)
        self._gauge_link_failures = BrocadeGauge(name="fcport_stats_link_failures", description="The number of link failures at this port (portshow, porterrshow Link_failure).", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="link-failures")
        self._gauge_link_failures_delta = BrocadeGauge(name="fcport_stats_link_failures_delta", description="Delta of link failures at this port (portshow, porterrshow Link_failure).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="link-failures-delta")
        # Number of instances of signal loss detected (Loss_of_sig)
        self._gauge_loss_of_signal = BrocadeGauge(name="fcport_stats_loss_of_signal", description="The number of signal loss instances detected at this port (portshow, porterrshow Loss_of_sig).", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="loss-of-signal")
        self._gauge_loss_of_signal_delta = BrocadeGauge(name="fcport_stats_loss_of_signal_delta", description="Delta of signal loss instances detected at this port (portshow, porterrshow Loss_of_sig).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="loss-of-signal-delta")
        # Number of instances of synchronization loss detected (Loss_of_sync)
        self._gauge_loss_of_sync = BrocadeGauge(name="fcport_stats_loss_of_sync", description="The number of instances of synchronization loss detected at this port (portshow, porterrshow Loss_of_sync).", 
                                                unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="loss-of-sync")
        self._gauge_loss_of_sync_delta = BrocadeGauge(name="fcport_stats_loss_of_sync_delta", description="Delta of instances of synchronization loss detected at this port (portshow, porterrshow Loss_of_sync).", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="loss-of-sync-delta")

        # remote port errors
        self._gauge_remote_crc_errors = BrocadeGauge(name="fcport_stats_remote_crc_errors", description="The number of frames received with invalid CRC at the remote F_Port (remote_er_crc).", 
                                                     unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-crc-errors")
        self._gauge_remote_crc_errors_delta = BrocadeGauge(name="fcport_stats_remote_crc_errors_delta", description="Delta of frames received with invalid CRC at the remote F_Port (remote_er_crc).", 
                                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-crc-errors-delta")
        self._gauge_remote_fec_uncorrected = BrocadeGauge(name="fcport_stats_remote_fec_uncorrected", description="The number of frames uncorrected by the FEC block at the remote F_Port (remote_uncor_err).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-fec-uncorrected")
        self._gauge_remote_fec_uncorrected_delta = BrocadeGauge(name="fcport_stats_remote_fec_uncorrected_delta", description="Delta of frames uncorrected by the FEC block at the remote F_Port (remote_uncor_err).", 
                                                                unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-fec-uncorrected-delta")
        self._gauge_remote_invalid_transmission_words = BrocadeGauge(name="fcport_stats_remote_invalid_transmission_words", 
                                                                     description="The number of invalid transmission words received at the remote F_Port (portshow remote_Invalid_word).", 
                                                                     unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-invalid-transmission-words")
        self._gauge_remote_invalid_transmission_words_delta = BrocadeGauge(name="fcport_stats_remote_invalid_transmission_words_delta", 
                                                                           description="Delta of invalid transmission words received at the remote F_Port (portshow remote_Invalid_word).", 
                                                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-invalid-transmission-words-delta")
        self._gauge_remote_link_failures = BrocadeGauge(name="fcport_stats_remote_link_failures", description="The number of link failures at the remote F-port (portshow, porterrshow remote_Link_failure).", 
                                                        unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-link-failures")
        self._gauge_remote_link_failures_delta = BrocadeGauge(name="fcport_stats_remote_link_failures_delta", description="Delta of link failures at the remote F-port (portshow, porterrshow remote_Link_failure).", 
                                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-link-failures-delta")
        self._gauge_remote_loss_of_signal = BrocadeGauge(name="fcport_stats_remote_loss_of_signal", 
                                                         description="The number of instances of signal loss detected at the remote F_Port (portshow, porterrshow remote_Loss_of_sig).", 
                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-loss-of-signal")
        self._gauge_remote_loss_of_signal_delta = BrocadeGauge(name="fcport_stats_remote_loss_of_signal_delta", 
                                                               description="Delta of instances of signal loss detected at the remote F_Port (portshow, porterrshow remote_Loss_of_sig).", 
                                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-loss-of-signal-delta")
        self._gauge_remote_loss_of_sync = BrocadeGauge(name="fcport_stats_remote_loss_of_sync", 
                                                       description="The number of instances of synchronization loss detected at the remote F_Port (portshow, porterrshow remote_Loss_of_sync).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-loss-of-sync")
        self._gauge_remote_loss_of_sync_delta = BrocadeGauge(name="fcport_stats_remote_loss_of_sync_delta", 
                                                             description="Delta of instances of synchronization loss detected at the remote F_Port (portshow, porterrshow remote_Loss_of_sync).", 
                                                             unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-loss-of-sync-delta")
        self._gauge_remote_primitive_sequence_protocol_error = BrocadeGauge(name="fcport_stats_remote_primitive_sequence_protocol_error", 
                                                                            description="The number of primitive sequence protocol errors detected at the remote F_Port (portshow remote_Protocol_err).", 
                                                                            unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-primitive-sequence-protocol-error")
        self._gauge_remote_primitive_sequence_protocol_error_delta = BrocadeGauge(name="fcport_stats_remote_primitive_sequence_protocol_error_delta", 
                                                                                  description="Delta of primitive sequence protocol errors detected at the remote F_Port (portshow remote_Protocol_err).", 
                                                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="remote-primitive-sequence-protocol-error-delta")
        self._gauge_too_many_rdys = BrocadeGauge(name="fcport_stats_too_many_rdys", description="The number of instances in which the number of RDYs (readys) exceeded the number of frames received (tim_rdy_pri).", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="too-many-rdys")
        self._gauge_too_many_rdys_delta = BrocadeGauge(name="fcport_stats_too_many_rdys_delta", description="Delta of instances in which the number of RDYs (readys) exceeded the number of frames received (tim_rdy_pri).", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="too-many-rdys-delta")
        self._gauge_truncated_frames = BrocadeGauge(name="fcport_stats_truncated_frames", description="The total number of truncated frames received (er_trunc).", 
                                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="truncated-frames")
        self._gauge_truncated_frames_delta = BrocadeGauge(name="fcport_stats_truncated_frames_delta", description="Delta of truncated frames received (er_trunc).", 
                                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="truncated-frames-delta")

        # summary port error status id
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        # low severiry errors port status id
        description_low_severity_errors_port_status_id = f"Port error status ID {BrocadeFCPortStatsToolbar.STATUS_ID} for the LOW severity errors {BrocadeFCPortStatisticsParser.LOW_SEVERITY_ERROR_LEAFS}."
        self._gauge_low_severity_errors_port_status_id = BrocadeGauge(name="fcport_stats_low_severity_errors_port_status_id", description=description_low_severity_errors_port_status_id, 
                                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="low-severity-errors_port-status-id")
        # medium severiry errors port status id
        description_medium_severity_errors_port_status_id = f"Port error status ID {BrocadeFCPortStatsToolbar.STATUS_ID} for the MEDIUM severity errors {BrocadeFCPortStatisticsParser.MEDIUM_SEVERITY_ERROR_LEAFS}."
        self._gauge_medium_severity_errors_port_status_id = BrocadeGauge(name="fcport_stats_medium_severity_errors_port_status_id", description=description_medium_severity_errors_port_status_id, 
                                                                         unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="medium-severity-errors_port-status-id")
        # high severiry errors port status id
        description_high_severity_errors_port_status_id = f"Port error status ID {BrocadeFCPortStatsToolbar.STATUS_ID} for the HIGH severity errors {BrocadeFCPortStatisticsParser.HIGH_SEVERITY_ERROR_LEAFS}."
        self._gauge_high_severity_errors_port_status_id = BrocadeGauge(name="fcport_stats_high_severity_errors_port_status_id", description=description_high_severity_errors_port_status_id, 
                                    unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="high-severity-errors_port-status-id")
        
        # in rate gauges
        self._gauge_in_peak_rate = BrocadeGauge(name="fcport_stats_in_peak_rate", description="The peak byte receive rate in MB/s.", 
                                                unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-peak-rate-megabytes")
        self._gauge_in_peak_rate_percentage = BrocadeGauge(name="fcport_stats_in_peak_rate_percentage", description="The percentage of peak receive rate from maximum port throughput.", 
                                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-peak-rate-percentage")
        # self._gauge_in_peak_rate_bits = BrocadeGauge(name="fcport_stats_in_peak_rate_bits", description="The peak bit receive rate.", 
        #                                              unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-peak-rate-bits")
        self._gauge_in_rate = BrocadeGauge(name="fcport_stats_in_rate", description="The instantaneous byte receive rate in MB/s.", 
                                           unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-rate-megabytes")
        self._gauge_in_rate_percentage = BrocadeGauge(name="fcport_stats_in_rate_percentage", description="The percentage of the instantaneous receive rate from maximum port throughput.", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-rate-percentage")
        # self._gauge_in_rate_bits = BrocadeGauge(name="fcport_stats_in_rate_bits", description="The instantaneous bit receive rate.", unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-rate-bits")
        
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        description_in_rate_status_id = f"The instantaneous receive rate status id {BrocadeFCPortStatsToolbar.STATUS_ID}."
        self._gauge_in_rate_status_id = BrocadeGauge(name="fcport_stats_in_rate_status_id", description=description_in_rate_status_id, 
                                                     unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="in-rate-status-id")
        
        # out rate gauges
        self._gauge_out_peak_rate = BrocadeGauge(name="fcport_stats_out_peak_rate", description="The peak byte transmit rate in MB/s.", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-peak-rate-megabytes")
        self._gauge_out_peak_rate_percentage = BrocadeGauge(name="fcport_stats_out_peak_rate_percentage", description="The percentage of peak transmit rate from maximum port throughput.", 
                                                            unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-peak-rate-percentage")
        # self._gauge_out_peak_rate_bits = BrocadeGauge(name="fcport_stats_out_peak_rate_bits", description="The peak bit transmit rate.", 
        #                                               unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-peak-rate-bits")
        self._gauge_out_rate = BrocadeGauge(name="fcport_stats_out_rate", description="The instantaneous byte transmit rate in MB/s.", 
                                            unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-rate-megabytes")
        self._gauge_out_rate_percentage = BrocadeGauge(name="fcport_stats_out_rate_percentage", description="The percentage of the instantaneous transmit rate from maximum port throughput.", 
                                                       unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-rate-percentage")
        # self._gauge_out_rate_bits = BrocadeGauge(name="fcport_stats_out_rate_bits", description="The instantaneous bit transmit rate.", 
        #                                          unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-rate-bits")
        # 1 - 'OK', 2 - 'Unknown', 3 - 'Warning', 4 - 'Critical'
        description_out_rate_status_id = f"The instantaneous transmit rate status id {BrocadeFCPortStatsToolbar.STATUS_ID}."
        self._gauge_out_rate_status_id = BrocadeGauge(name="fcport_stats_out_rate_status_id", description=description_out_rate_status_id, 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, metric_key="out-rate-status-id")

        # total number of frames in human-readable format counters gauges
        self._gauge_class_3_frames_hrf = BrocadeGauge(name="fcport_stats_class_3_frames_hrf", description="The number of Class 3 frames received at this port (stat_c3_frx) in human-readable format.", 
                                                      unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, parameter_key="class-3-frames-hrf")
        self._gauge_in_frames_hrf = BrocadeGauge(name="fcport_stats_in_frames_hrf", description="The number of frames received at this port (stat_frx) in human-readable format.", 
                                                 unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, parameter_key="in-frames-hrf")
        self._gauge_out_frames_hrf = BrocadeGauge(name="fcport_stats_out_frames_hrf", description="The number of frames transmitted from this port (stat_ftx) in human-readable format.", 
                                                  unit_keys=BrocadeFCPortStatsToolbar.switch_port_keys, parameter_key="out-frames-hrf")



    def fill_toolbar_gauge_metrics(self, fcport_stats_parser: BrocadeFCPortStatisticsParser) -> None:
        """Method to fill the gauge metrics for the toolbar.

        Args:
            sfp_media_parser (BrocadeSfpMediaParser): object contains required data to fill the gauge metrics.
        """
        

        gauge_lst = [
            self.gauge_swname, self.gauge_fabricname, self.gauge_switch_vfid, self.gauge_portname, self.gauge_port_speed_value, 
            self.gauge_port_speed_mode, self.gauge_port_physical_state, self.gauge_port_type, self.gauge_address_errors, 
            self.gauge_address_errors_delta, self.gauge_bad_eofs_received, self.gauge_bad_eofs_received_delta, 
            self.gauge_bb_credit_zero, self.gauge_bb_credit_zero_delta, self.gauge_class3_in_discards, 
            self.gauge_class3_in_discards_delta, self.gauge_class3_out_discards, self.gauge_class3_out_discards_delta, 
            self.gauge_class_3_discards, self.gauge_class_3_discards_delta, self.gauge_class_3_frames, self.gauge_class_3_frames_delta, 
            self.gauge_class_3_frames_hrf, self.gauge_crc_errors, self.gauge_crc_errors_delta, self.gauge_delimiter_errors, 
            self.gauge_delimiter_errors_delta, self.gauge_encoding_disparity_errors, self.gauge_encoding_disparity_errors_delta, 
            self.gauge_encoding_errors_outside_frame, self.gauge_encoding_errors_outside_frame_delta, self.gauge_f_busy_frames, 
            self.gauge_f_busy_frames_delta, self.gauge_f_rjt_frames, self.gauge_f_rjt_frames_delta, self.gauge_frames_processing_required, 
            self.gauge_frames_processing_required_delta, self.gauge_frames_timed_out, self.gauge_frames_timed_out_delta, self.gauge_frames_too_long, 
            self.gauge_frames_too_long_delta, self.gauge_frames_transmitter_unavailable_errors, self.gauge_frames_transmitter_unavailable_errors_delta, 
            self.gauge_high_severity_errors_port_status_id, self.gauge_in_crc_errors, self.gauge_in_crc_errors_delta, self.gauge_in_frames, 
            self.gauge_in_frames_delta, self.gauge_in_frames_hrf, self.gauge_in_lcs, self.gauge_in_lcs_delta, self.gauge_in_link_resets, 
            self.gauge_in_link_resets_delta, self.gauge_in_offline_sequences, self.gauge_in_offline_sequences_delta, self.gauge_in_peak_rate, 
            self.gauge_in_peak_rate_percentage, self.gauge_in_rate, self.gauge_in_rate_percentage, 
            self.gauge_in_rate_status_id, self.gauge_invalid_ordered_sets, self.gauge_invalid_ordered_sets_delta, self.gauge_invalid_transmission_words, 
            self.gauge_invalid_transmission_words_delta, self.gauge_link_failures, self.gauge_link_failures_delta, self.gauge_link_level_interrpts, 
            self.gauge_link_level_interrpts_delta, self.gauge_loss_of_signal, self.gauge_loss_of_signal_delta, self.gauge_loss_of_sync, 
            self.gauge_loss_of_sync_delta, self.gauge_low_severity_errors_port_status_id, self.gauge_lrin_delta_subtract_olsout_delta, 
            self.gauge_lrout_delta_subtract_olsin_delta, self.gauge_max_speed, self.gauge_medium_severity_errors_port_status_id, self.gauge_multicast_timeouts, 
            self.gauge_multicast_timeouts_delta, self.gauge_out_frames, self.gauge_out_frames_delta, self.gauge_out_frames_hrf, self.gauge_out_link_resets, 
            self.gauge_out_link_resets_delta, self.gauge_out_offline_sequences, self.gauge_out_offline_sequences_delta, self.gauge_out_peak_rate, 
            self.gauge_out_peak_rate_percentage, self.gauge_out_rate, self.gauge_out_rate_percentage, 
            self.gauge_out_rate_status_id, self.gauge_pcs_block_errors, self.gauge_pcs_block_errors_delta, self.gauge_primitive_sequence_protocol_error, 
            self.gauge_primitive_sequence_protocol_error_delta, self.gauge_remote_crc_errors, self.gauge_remote_crc_errors_delta, self.gauge_remote_fec_uncorrected, 
            self.gauge_remote_fec_uncorrected_delta, self.gauge_remote_invalid_transmission_words, self.gauge_remote_invalid_transmission_words_delta, 
            self.gauge_remote_link_failures, self.gauge_remote_link_failures_delta, self.gauge_remote_loss_of_signal, self.gauge_remote_loss_of_signal_delta, 
            self.gauge_remote_loss_of_sync, self.gauge_remote_loss_of_sync_delta, self.gauge_remote_primitive_sequence_protocol_error, 
            self.gauge_remote_primitive_sequence_protocol_error_delta, self.gauge_too_many_rdys, self.gauge_too_many_rdys_delta, self.gauge_truncated_frames, 
            self.gauge_truncated_frames_delta
            ]
        
        for gauge in gauge_lst:
            gauge.fill_port_gauge_metrics(fcport_stats_parser.fcport_stats)


    def __repr__(self):
        return f"{self.__class__.__name__} ip_address: {self.sw_telemetry.sw_ipaddress}"


    @property
    def gauge_swname(self):
        return self._gauge_swname


    @property
    def gauge_fabricname(self):
         return self._gauge_fabricname


    @property
    def gauge_portname(self):
        return self._gauge_portname
    

    @property
    def gauge_switch_vfid(self):
        return self._gauge_switch_vfid


    @property
    def gauge_port_speed_value(self):
        return self._gauge_port_speed_value


    @property
    def gauge_port_speed_mode(self):
        return self._gauge_port_speed_mode


    @property
    def gauge_port_physical_state(self):
        return self._gauge_port_physical_state


    @property
    def gauge_port_type(self):
        return self._gauge_port_type


    @property
    def gauge_max_speed(self):
        return self._gauge_max_speed


    @property
    def gauge_address_errors(self):
        return self._gauge_address_errors
    

    @property
    def gauge_address_errors_delta(self):
        return self._gauge_address_errors_delta
    

    @property
    def gauge_bad_eofs_received(self):
        return self._gauge_bad_eofs_received
    

    @property
    def gauge_bad_eofs_received_delta(self):
        return self._gauge_bad_eofs_received_delta
    

    @property
    def gauge_bb_credit_zero(self):
        return self._gauge_bb_credit_zero
    

    @property
    def gauge_bb_credit_zero_delta(self):
        return self._gauge_bb_credit_zero_delta
    

    @property
    def gauge_class3_in_discards(self):
        return self._gauge_class3_in_discards
    

    @property
    def gauge_class3_in_discards_delta(self):
        return self._gauge_class3_in_discards_delta
    

    @property
    def gauge_class3_out_discards(self):
        return self._gauge_class3_out_discards
    

    @property
    def gauge_class3_out_discards_delta(self):
        return self._gauge_class3_out_discards_delta
    

    @property
    def gauge_class_3_discards(self):
        return self._gauge_class_3_discards
    

    @property
    def gauge_class_3_discards_delta(self):
        return self._gauge_class_3_discards_delta
    

    @property
    def gauge_class_3_frames(self):
        return self._gauge_class_3_frames
    

    @property
    def gauge_class_3_frames_delta(self):
        return self._gauge_class_3_frames_delta
    

    @property
    def gauge_class_3_frames_hrf(self):
        return self._gauge_class_3_frames_hrf
    

    @property
    def gauge_crc_errors(self):
        return self._gauge_crc_errors
    

    @property
    def gauge_crc_errors_delta(self):
        return self._gauge_crc_errors_delta
    

    @property
    def gauge_delimiter_errors(self):
        return self._gauge_delimiter_errors
    

    @property
    def gauge_delimiter_errors_delta(self):
        return self._gauge_delimiter_errors_delta
    

    @property
    def gauge_encoding_disparity_errors(self):
        return self._gauge_encoding_disparity_errors
    

    @property
    def gauge_encoding_disparity_errors_delta(self):
        return self._gauge_encoding_disparity_errors_delta
    
    
    @property
    def gauge_encoding_errors_outside_frame(self):
        return self._gauge_encoding_errors_outside_frame
    

    @property
    def gauge_encoding_errors_outside_frame_delta(self):
        return self._gauge_encoding_errors_outside_frame_delta
    

    @property
    def gauge_f_busy_frames(self):
        return self._gauge_f_busy_frames
    

    @property
    def gauge_f_busy_frames_delta(self):
        return self._gauge_f_busy_frames_delta
    

    @property
    def gauge_f_rjt_frames(self):
        return self._gauge_f_rjt_frames
    

    @property
    def gauge_f_rjt_frames_delta(self):
        return self._gauge_f_rjt_frames_delta
    

    @property
    def gauge_frames_processing_required(self):
        return self._gauge_frames_processing_required
    

    @property
    def gauge_frames_processing_required_delta(self):
        return self._gauge_frames_processing_required_delta
    

    @property
    def gauge_frames_timed_out(self):
        return self._gauge_frames_timed_out


    @property
    def gauge_frames_timed_out_delta(self):
        return self._gauge_frames_timed_out_delta
    

    @property
    def gauge_frames_too_long(self):
        return self._gauge_frames_too_long
    

    @property
    def gauge_frames_too_long_delta(self):
        return self._gauge_frames_too_long_delta
    

    @property
    def gauge_frames_transmitter_unavailable_errors(self):
        return self._gauge_frames_transmitter_unavailable_errors
    

    @property
    def gauge_frames_transmitter_unavailable_errors_delta(self):
        return self._gauge_frames_transmitter_unavailable_errors_delta
    

    @property
    def gauge_high_severity_errors_port_status_id(self):
        return self._gauge_high_severity_errors_port_status_id
    

    @property
    def gauge_in_crc_errors(self):
        return self._gauge_in_crc_errors
    

    @property
    def gauge_in_crc_errors_delta(self):
        return self._gauge_in_crc_errors_delta
    

    @property
    def gauge_in_frames(self):
        return self._gauge_in_frames
    

    @property
    def gauge_in_frames_delta(self):
        return self._gauge_in_frames_delta
    

    @property
    def gauge_in_frames_hrf(self):
        return self._gauge_in_frames_hrf
    

    @property
    def gauge_in_lcs(self):
        return self._gauge_in_lcs
    

    @property
    def gauge_in_lcs_delta(self):
        return self._gauge_in_lcs_delta
    

    @property
    def gauge_in_link_resets(self):
        return self._gauge_in_link_resets
    

    @property
    def gauge_in_link_resets_delta(self):
        return self._gauge_in_link_resets_delta
    

    @property
    def gauge_in_offline_sequences(self):
        return self._gauge_in_offline_sequences
    

    @property
    def gauge_in_offline_sequences_delta(self):
        return self._gauge_in_offline_sequences_delta
    

    @property
    def gauge_in_peak_rate(self):
        return self._gauge_in_peak_rate
    

    @property
    def gauge_in_peak_rate_percentage(self):
        return self._gauge_in_peak_rate_percentage
    

    # @property
    # def gauge_in_peak_rate_bits(self):
    #     return self._gauge_in_peak_rate_bits
    

    @property
    def gauge_in_rate(self):
        return self._gauge_in_rate
    

    @property
    def gauge_in_rate_percentage(self):
        return self._gauge_in_rate_percentage
    

    # @property
    # def gauge_in_rate_bits(self):
    #     return self._gauge_in_rate_bits
    

    @property
    def gauge_in_rate_status_id(self):
        return self._gauge_in_rate_status_id
    

    @property
    def gauge_invalid_ordered_sets(self):
        return self._gauge_invalid_ordered_sets
    

    @property
    def gauge_invalid_ordered_sets_delta(self):
        return self._gauge_invalid_ordered_sets_delta
    

    @property
    def gauge_invalid_transmission_words(self):
        return self._gauge_invalid_transmission_words
    

    @property
    def gauge_invalid_transmission_words_delta(self):
        return self._gauge_invalid_transmission_words_delta
    

    @property
    def gauge_link_failures(self):
        return self._gauge_link_failures
    

    @property
    def gauge_link_failures_delta(self):
        return self._gauge_link_failures_delta
    

    @property
    def gauge_link_level_interrpts(self):
        return self._gauge_link_level_interrpts
    

    @property
    def gauge_link_level_interrpts_delta(self):
        return self._gauge_link_level_interrpts_delta
    

    @property
    def gauge_loss_of_signal(self):
        return self._gauge_loss_of_signal
    

    @property
    def gauge_loss_of_signal_delta(self):
        return self._gauge_loss_of_signal_delta
    

    @property
    def gauge_loss_of_sync(self):
        return self._gauge_loss_of_sync
    

    @property
    def gauge_loss_of_sync_delta(self):
        return self._gauge_loss_of_sync_delta
    

    @property
    def gauge_low_severity_errors_port_status_id(self):
        return self._gauge_low_severity_errors_port_status_id
    

    @property
    def gauge_lrin_delta_subtract_olsout_delta(self):
        return self._gauge_lrin_delta_subtract_olsout_delta
    

    @property
    def gauge_lrout_delta_subtract_olsin_delta(self):
        return self._gauge_lrout_delta_subtract_olsin_delta
    

    @property
    def gauge_medium_severity_errors_port_status_id(self):
        return self._gauge_medium_severity_errors_port_status_id
    

    @property
    def gauge_multicast_timeouts(self):
        return self._gauge_multicast_timeouts
    

    @property
    def gauge_multicast_timeouts_delta(self):
        return self._gauge_multicast_timeouts_delta
    

    @property
    def gauge_out_frames(self):
        return self._gauge_out_frames
    

    @property
    def gauge_out_frames_delta(self):
        return self._gauge_out_frames_delta
    

    @property
    def gauge_out_frames_hrf(self):
        return self._gauge_out_frames_hrf
    

    @property
    def gauge_out_link_resets(self):
        return self._gauge_out_link_resets
    
    @property
    def gauge_out_link_resets_delta(self):
        return self._gauge_out_link_resets_delta
    

    @property
    def gauge_out_offline_sequences(self):
        return self._gauge_out_offline_sequences
    

    @property
    def gauge_out_offline_sequences_delta(self):
        return self._gauge_out_offline_sequences_delta
    

    @property
    def gauge_out_peak_rate(self):
        return self._gauge_out_peak_rate
    

    @property
    def gauge_out_peak_rate_percentage(self):
        return self._gauge_out_peak_rate_percentage
    

    # @property
    # def gauge_out_peak_rate_bits(self):
    #     return self._gauge_out_peak_rate_bits
    

    @property
    def gauge_out_rate(self):
        return self._gauge_out_rate
    

    @property
    def gauge_out_rate_percentage(self):
        return self._gauge_out_rate_percentage
    

    # @property
    # def gauge_out_rate_bits(self):
    #     return self._gauge_out_rate_bits
    

    @property
    def gauge_out_rate_status_id(self):
        return self._gauge_out_rate_status_id
    

    @property
    def gauge_pcs_block_errors(self):
        return self._gauge_pcs_block_errors
    

    @property
    def gauge_pcs_block_errors_delta(self):
        return self._gauge_pcs_block_errors_delta
    

    @property
    def gauge_primitive_sequence_protocol_error(self):
        return self._gauge_primitive_sequence_protocol_error
    

    @property
    def gauge_primitive_sequence_protocol_error_delta(self):
        return self._gauge_primitive_sequence_protocol_error_delta
    

    @property
    def gauge_remote_crc_errors(self):
        return self._gauge_remote_crc_errors
    

    @property
    def gauge_remote_crc_errors_delta(self):
        return self._gauge_remote_crc_errors_delta
    

    @property
    def gauge_remote_fec_uncorrected(self):
        return self._gauge_remote_fec_uncorrected
    

    @property
    def gauge_remote_fec_uncorrected_delta(self):
        return self._gauge_remote_fec_uncorrected_delta
    

    @property
    def gauge_remote_invalid_transmission_words(self):
        return self._gauge_remote_invalid_transmission_words
    

    @property
    def gauge_remote_invalid_transmission_words_delta(self):
        return self._gauge_remote_invalid_transmission_words_delta
    

    @property
    def gauge_remote_link_failures(self):
        return self._gauge_remote_link_failures
    

    @property
    def gauge_remote_link_failures_delta(self):
        return self._gauge_remote_link_failures_delta
    
    
    @property
    def gauge_remote_loss_of_signal(self):
        return self._gauge_remote_loss_of_signal
    

    @property
    def gauge_remote_loss_of_signal_delta(self):
        return self._gauge_remote_loss_of_signal_delta
    

    @property
    def gauge_remote_loss_of_sync(self):
        return self._gauge_remote_loss_of_sync
    

    @property
    def gauge_remote_loss_of_sync_delta(self):
        return self._gauge_remote_loss_of_sync_delta
    

    @property
    def gauge_remote_primitive_sequence_protocol_error(self):
        return self._gauge_remote_primitive_sequence_protocol_error
    

    @property
    def gauge_remote_primitive_sequence_protocol_error_delta(self):
        return self._gauge_remote_primitive_sequence_protocol_error_delta
    

    @property
    def gauge_too_many_rdys(self):
        return self._gauge_too_many_rdys
    

    @property
    def gauge_too_many_rdys_delta(self):
        return self._gauge_too_many_rdys_delta
    

    @property
    def gauge_truncated_frames(self):
        return self._gauge_truncated_frames
    

    @property
    def gauge_truncated_frames_delta(self):
        return self._gauge_truncated_frames_delta
