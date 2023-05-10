import logging

import pandapower as pp
from numpy import nan
import pandas as pd
from pandas import read_json

logger = logging.getLogger(__name__)

class create_network:
    def __init__(self, network_name:str, der_opt:str):
        
        '''all option으로 구현되는 ESS는 현재 ieee123에만 구현'''
        self.network_name = network_name
        self.der_opt = der_opt
        available_networks = ['cigre14', 'ieee123']
        assert self.network_name in available_networks, f"(networks) network name must be in {available_networks}, but got {self.network_name}"
        available_der_opts = ['pv_wind', 'all']
        assert self.der_opt in available_der_opts, f"(networks) der_opt must be in {available_der_opts}, but got {self.der_opt}"
        
        if network_name=='cigre14':
            self.net=self.create_cigre_network_mv_OSH(der_opt)
            self.sw_to_be_opened = 3 
        elif network_name=='ieee123':
            self.net=self.create_ieee_123_network(der_opt)
            self.sw_to_be_opened = 10


    '''CIGRE 14 network'''
    @staticmethod
    def create_cigre_network_mv_OSH(with_der):
        """
        Create the CIGRE MV Grid from final Report of Task Force C6.04.02:
        "Benchmark Systems for Network Integration of Renewable and Distributed Energy Resources”, 2014.

        OPTIONAL:
            **with_der** (boolean or str, False) - Range of DER consideration, which should be in
                (False, "pv_wind", "all"). The DER types, dimensions and locations are taken from CIGRE
                CaseStudy: "DER in Medium Voltage Systems"

        OUTPUT:
            **net** - The pandapower format network.
        """

        net_cigre_mv = pp.create_empty_network(name="cigre14")

        # Linedata
        line_data = {'c_nf_per_km': 151.1749, 'r_ohm_per_km': 0.501,
                    'x_ohm_per_km': 0.716, 'max_i_ka': 0.145,
                    'type': 'cs'}
        pp.create_std_type(net_cigre_mv, line_data, name='CABLE_CIGRE_MV', element='line')

        line_data = {'c_nf_per_km': 10.09679, 'r_ohm_per_km': 0.510,
                    'x_ohm_per_km': 0.366, 'max_i_ka': 0.195,
                    'type': 'ol'}
        pp.create_std_type(net_cigre_mv, line_data, name='OHL_CIGRE_MV', element='line')

        # Busses
        bus0 = pp.create_bus(net_cigre_mv, name='Bus 0', vn_kv=110, type='b', zone='CIGRE_MV')
        buses = pp.create_buses(net_cigre_mv, 14, name=['Bus %i' % i for i in range(1, 15)], vn_kv=20,
                                type='b', zone='CIGRE_MV')

        # Lines
        ''' modified for personal purpose '''
        line1_2 = pp.create_line(net_cigre_mv, buses[0], buses[1], length_km=2.82,
                    std_type='CABLE_CIGRE_MV', name='Line0')
        line2_3 = pp.create_line(net_cigre_mv, buses[1], buses[2], length_km=4.42,
                    std_type='CABLE_CIGRE_MV', name='Line1')
        line3_4 = pp.create_line(net_cigre_mv, buses[2], buses[3], length_km=0.61,
                    std_type='CABLE_CIGRE_MV', name='Line2')
        line4_5 = pp.create_line(net_cigre_mv, buses[3], buses[4], length_km=0.56,
                    std_type='CABLE_CIGRE_MV', name='Line3')
        line5_6 = pp.create_line(net_cigre_mv, buses[4], buses[5], length_km=1.54,
                    std_type='CABLE_CIGRE_MV', name='Line4')
        line7_8 = pp.create_line(net_cigre_mv, buses[6], buses[7], length_km=1.67,
                    std_type='CABLE_CIGRE_MV', name='Line5')
        line8_9 = pp.create_line(net_cigre_mv, buses[7], buses[8], length_km=0.32,
                    std_type='CABLE_CIGRE_MV', name='Line6')
        line9_10 = pp.create_line(net_cigre_mv, buses[8], buses[9], length_km=0.77,
                    std_type='CABLE_CIGRE_MV', name='Line7')
        line10_11 = pp.create_line(net_cigre_mv, buses[9], buses[10], length_km=0.33,
                    std_type='CABLE_CIGRE_MV', name='Line8')
        line3_8 = pp.create_line(net_cigre_mv, buses[2], buses[7], length_km=1.3,
                    std_type='CABLE_CIGRE_MV', name='Line9')
        line12_13 = pp.create_line(net_cigre_mv, buses[11], buses[12], length_km=4.89,
                    std_type='OHL_CIGRE_MV', name='Line10')
        line13_14 = pp.create_line(net_cigre_mv, buses[12], buses[13], length_km=2.99,
                    std_type='OHL_CIGRE_MV', name='Line11')
        line6_7 = pp.create_line(net_cigre_mv, buses[5], buses[6], length_km=0.24,
                                std_type='CABLE_CIGRE_MV', name='Line12')
        line4_11 = pp.create_line(net_cigre_mv, buses[10], buses[3], length_km=0.49,
                                std_type='CABLE_CIGRE_MV', name='Line13')
        line8_14 = pp.create_line(net_cigre_mv, buses[13], buses[7], length_km=2.,
                                std_type='OHL_CIGRE_MV', name='Line14')

        # Ext-Grid
        ## pandapower1.5->2.11에 맞게 변수명 변경 (230317)
        pp.create_ext_grid(net_cigre_mv, bus0, vm_pu=1, va_degree=0.,
                        s_sc_max_mva=5000, s_sc_min_mva=5000, rx_max=0.1, rx_min=0.1)

        # Trafos
        trafo0 = pp.create_transformer_from_parameters(net_cigre_mv, bus0, buses[0], sn_mva=25,
                                                    vn_hv_kv=110, vn_lv_kv=20, vkr_percent=0.16,
                                                    vk_percent=12.00107, pfe_kw=0, i0_percent=0,
                                                    shift_degree=30.0, name='Trafo 0-1',
                                                    tap_side='lv', tap_neutral=0, tap_max=2, tap_min=-2, tap_step_percent=1)
        trafo1 = pp.create_transformer_from_parameters(net_cigre_mv, bus0, buses[11], sn_mva=25,
                                                    vn_hv_kv=110, vn_lv_kv=20, vkr_percent=0.16,
                                                    vk_percent=12.00107, pfe_kw=0, i0_percent=0,
                                                    shift_degree=30.0, name='Trafo 0-12',
                                                    tap_side='lv', tap_neutral=0, tap_max=2, tap_min=-2, tap_step_percent=1)

        # Switches
        '''original switches modified for personal purpose'''
        pp.create_switch(net_cigre_mv, buses[6], line6_7, et='l', closed=False, type='LBS', name='S01')
        pp.create_switch(net_cigre_mv, buses[3], line4_11, et='l', closed=False, type='LBS', name='S02')
        pp.create_switch(net_cigre_mv, buses[7], line8_14, et='l', closed=False, type='LBS', name='S03')

        '''additional switches for personal purpose'''
        pp.create_switch(net_cigre_mv, buses[0], line1_2, 'l', closed=True, type='LBS', name='S04', index=None)
        pp.create_switch(net_cigre_mv, buses[1], line2_3, 'l', closed=True, type='LBS', name='S05', index=None)
        pp.create_switch(net_cigre_mv, buses[2], line3_4, 'l', closed=True, type='LBS', name='S06', index=None)
        pp.create_switch(net_cigre_mv, buses[2], line3_8, 'l', closed=True, type='LBS', name='S07', index=None)
        pp.create_switch(net_cigre_mv, buses[3], line4_5, 'l', closed=True, type='LBS', name='S08', index=None)
        pp.create_switch(net_cigre_mv, buses[4], line5_6, 'l', closed=True, type='LBS', name='S09', index=None)
        pp.create_switch(net_cigre_mv, buses[6], line7_8, 'l', closed=True, type='LBS', name='S10', index=None)
        pp.create_switch(net_cigre_mv, buses[7], line8_9, 'l', closed=True, type='LBS', name='S11', index=None)
        pp.create_switch(net_cigre_mv, buses[8], line9_10, 'l', closed=True, type='LBS', name='S12', index=None)
        pp.create_switch(net_cigre_mv, buses[9], line10_11, 'l', closed=True, type='LBS', name='S13', index=None)
        pp.create_switch(net_cigre_mv, buses[11], line12_13, 'l', closed=True, type='LBS', name='S14', index=None)
        pp.create_switch(net_cigre_mv, buses[12], line13_14, 'l', closed=True, type='LBS', name='S15', index=None)

        # Loads
        # Residential
        ## pandapower1.5->2.11에 맞게 단위 및 option명 변경
        pp.create_load_from_cosphi(net_cigre_mv, buses[0], 15.3, 0.98, "underexcited", name='Load R1')
        pp.create_load_from_cosphi(net_cigre_mv, buses[2], 0.285, 0.97, "underexcited", name='Load R3')
        pp.create_load_from_cosphi(net_cigre_mv, buses[3], 0.445, 0.97, "underexcited", name='Load R4')
        pp.create_load_from_cosphi(net_cigre_mv, buses[4], 0.750, 0.97, "underexcited", name='Load R5')
        pp.create_load_from_cosphi(net_cigre_mv, buses[5], 0.565, 0.97, "underexcited", name='Load R6')
        pp.create_load_from_cosphi(net_cigre_mv, buses[7], 0.605, 0.97, "underexcited", name='Load R8')
        pp.create_load_from_cosphi(net_cigre_mv, buses[9], 0.490, 0.97, "underexcited", name='Load R10')
        pp.create_load_from_cosphi(net_cigre_mv, buses[10], 0.340, 0.97, "underexcited", name='Load R11')
        pp.create_load_from_cosphi(net_cigre_mv, buses[11], 15.3, 0.98, "underexcited", name='Load R12')
        pp.create_load_from_cosphi(net_cigre_mv, buses[13], 0.215, 0.97, "underexcited", name='Load R14')

        # Commercial / Industrial
        pp.create_load_from_cosphi(net_cigre_mv, buses[0], 5.1, 0.95, "underexcited", name='Load CI1')
        pp.create_load_from_cosphi(net_cigre_mv, buses[2], 0.265, 0.85, "underexcited", name='Load CI3')
        pp.create_load_from_cosphi(net_cigre_mv, buses[6], 0.090, 0.85, "underexcited", name='Load CI7')
        pp.create_load_from_cosphi(net_cigre_mv, buses[8], 0.675, 0.85, "underexcited", name='Load CI9')
        pp.create_load_from_cosphi(net_cigre_mv, buses[9], 0.080, 0.85, "underexcited", name='Load CI10')
        pp.create_load_from_cosphi(net_cigre_mv, buses[11], 5.28, 0.95, "underexcited", name='Load CI12')
        pp.create_load_from_cosphi(net_cigre_mv, buses[12], 0.04, 0.85, "underexcited", name='Load CI13')
        pp.create_load_from_cosphi(net_cigre_mv, buses[13], 0.390, 0.85, "underexcited", name='Load CI14')

        # Optional distributed energy recources
        ## pandapower1.5->2.11에 맞게 단위 및 option명 변경
        if with_der in ["pv_wind", "all"]:
            pp.create_sgen(net_cigre_mv, buses[4], p_mw=1.300, q_mvar=0, sn_mva=1.500, scaling=1., name='WT1', type='WT')
            pp.create_sgen(net_cigre_mv, buses[5], p_mw=1.300, q_mvar=0, sn_mva=1.500, scaling=1., name='WT2', type='WT')
            pp.create_sgen(net_cigre_mv, buses[6], p_mw=1.300, q_mvar=0, sn_mva=1.500, scaling=1., name='WT3', type='WT')
            #pp.create_sgen(net_cigre_mv, buses[8],p_mw= -.1500, q_mvar=0, sn_mva=1.500, scaling=1., name='WT4', type='WP')
            pp.create_sgen(net_cigre_mv, buses[8], p_mw=1.000, q_mvar=0, sn_mva=3.000, scaling=1., name='PV1', type='PV')
            pp.create_sgen(net_cigre_mv, buses[9], p_mw=1.300, q_mvar=0, sn_mva=1.500, scaling=1., name='WT4', type='WT')
            pp.create_sgen(net_cigre_mv, buses[10],p_mw=1.300, q_mvar=0, sn_mva=1.500, scaling=1., name='WT5', type='WT')
            #pp.create_sgen(net_cigre_mv, buses[11], p_mw=1.500, q_mvar=0, sn_mva=1.500, scaling=1., name='WT7', type='WP')
            #pp.create_sgen(net_cigre_mv, buses[12], p_mw=1.500, q_mvar=0, sn_mva=1.500, scaling=1., name='WT8', type='WP')
            #pp.create_sgen(net_cigre_mv, buses[13], p_mw=1.500, q_mvar=0, sn_mva=1.500, scaling=1., name='WT9', type='WP')
            pp.create_sgen(net_cigre_mv, buses[11],p_mw=3.500, q_mvar=0, sn_mva=3.000, scaling=1., name='PV2', type='PV')
            pp.create_sgen(net_cigre_mv, buses[12],p_mw=3.500, q_mvar=0, sn_mva=3.000, scaling=1., name='PV3', type='PV')
            pp.create_sgen(net_cigre_mv, buses[13],p_mw=3.500, q_mvar=0, sn_mva=3.000, scaling=1., name='PV4', type='PV')
            if with_der == "all":
                pp.create_storage(net_cigre_mv, bus=buses[4], p_mw=0.6, max_e_mwh=nan, sn_mva=0.2,
                                name='Battery 1', type='Battery', max_p_mw=0.6, min_p_mw=-0.6)
                pp.create_sgen(net_cigre_mv, bus=buses[4], p_mw=0.033, sn_mva=0.033,
                            name='Residential fuel cell 1', type='Residential fuel cell')
                pp.create_sgen(net_cigre_mv, bus=buses[8], p_mw=0.310, sn_mva=0.31, name='CHP diesel 1',
                            type='CHP diesel')
                pp.create_sgen(net_cigre_mv, bus=buses[8], p_mw=0.212, sn_mva=0.212, name='Fuel cell 1',
                            type='Fuel cell')
                pp.create_storage(net_cigre_mv, bus=buses[9], p_mw=0.200, max_e_mwh=nan, sn_mva=0.2,
                                name='Battery 2', type='Battery', max_p_mw=0.2, min_p_mw=-0.2)
                pp.create_sgen(net_cigre_mv, bus=buses[9], p_mw=0.014, sn_mva=.014,
                            name='Residential fuel cell 2', type='Residential fuel cell')

        # Bus geo data
        net_cigre_mv.bus_geodata = read_json(
            """{"x":{"0":7.0,"1":4.0,"2":4.0,"3":4.0,"4":2.5,"5":1.0,"6":1.0,"7":8.0,"8":8.0,"9":6.0,
            "10":4.0,"11":4.0,"12":10.0,"13":10.0,"14":10.0},"y":{"0":16,"1":15,"2":13,"3":11,"4":9,
            "5":7,"6":3,"7":3,"8":5,"9":5,"10":5,"11":7,"12":15,"13":11,"14":5}}""")
        # Match bus.index
        net_cigre_mv.bus_geodata = net_cigre_mv.bus_geodata.loc[net_cigre_mv.bus.index]
        return net_cigre_mv


    '''IEEE 123 network'''
    @staticmethod
    def create_ieee_123_network(with_der=False):
        
        net = pp.create_empty_network(name='ieee123')

        # Busses
        bus0 = pp.create_bus(net, name='Bus 0',
                            vn_kv=115, type='b', zone=None)
        buses = pp.create_buses(net, 115, name=['Bus %i' % i for i in range(1, 116)], vn_kv=4.16,
                                type='b', zone=None)

        # Lines

        # Linedata "94-AL1/15-ST1A 10.0" (MV std type 중 하나로 std_types.py에 정의)
        line_data = {"c_nf_per_km": 10.75,
            "r_ohm_per_km": 0.3060,
            "x_ohm_per_km": 0.33,
            "max_i_ka": 0.350,
            "type": "ol",
            "q_mm2": 94}
        pp.create_std_type(net, line_data, name="94-AL1/15-ST1A 10.0", element='line')

        df_line = pd.read_excel('networks/ieee123_linedata.xlsx')
        line_no = len(df_line)
        lines = []
        for i in range(line_no):
            #length: feet->km
            line = pp.create_line(net, buses[df_line['Node 1'][i]-1], buses[df_line['Node 2'][i]-1],
                                length_km=df_line['Length'][i]*0.0003048,  std_type="94-AL1/15-ST1A 10.0", name='Line'+str(i+1))
            lines.append(line)
            
        pp.create_ext_grid(net, bus0, vm_pu=1.0, va_degree=0.,
                        s_sc_max_mva=5000, s_sc_min_mva=5000, rx_max=0.1, rx_min=0.1)

        # Trafos
        pp.create_transformer_from_parameters(net, hv_bus=bus0, lv_bus=buses[114], sn_mva=5.000, vn_hv_kv=115, vn_lv_kv=4.16, vkr_percent=1, vk_percent=8.06225774, pfe_kw=0, i0_percent=0,name='Trafo1')

        pp.create_transformer_from_parameters(net, hv_bus=bus0, lv_bus=buses[26], sn_mva=5.000, vn_hv_kv=115, vn_lv_kv=4.16, vkr_percent=1,
                                            vk_percent=8.06225774, pfe_kw=0, i0_percent=0, name='Trafo2')

        # Switches
        pp.create_switch(net, buses[12], lines[112], 'l', closed=True, type='LBS', name='S01', index=None)
        pp.create_switch(net, buses[17], lines[110], 'l', closed=True, type='LBS', name='S02', index=None)
        pp.create_switch(net, buses[53], lines[115], 'l', closed=False, type='LBS', name='S03', index=None)
        pp.create_switch(net, buses[59], lines[113], 'l', closed=True, type='LBS', name='S04', index=None)
        pp.create_switch(net, buses[50], lines[49],  'l', closed=False, type='LBS', name='S05', index=None)
        pp.create_switch(net, buses[96], lines[114],'l', closed=True, type='LBS', name='S06', index=None)
        
        pp.create_switch(net, buses[36], lines[116],'l', closed=False, type='LBS', name='S07', index=None)
        pp.create_switch(net, buses[55], lines[117],'l', closed=False, type='LBS', name='S08', index=None)
        pp.create_switch(net, buses[70], lines[118],'l', closed=False, type='LBS', name='S09', index=None)
        pp.create_switch(net, buses[45], lines[119],'l', closed=False, type='LBS', name='S10', index=None)

        pp.create_switch(net, buses[16], lines[120], 'l', closed=False, type='LBS', name='S11', index=None)
        pp.create_switch(net, buses[29], lines[121], 'l', closed=False, type='LBS', name='S12', index=None)
        #pp.create_switch(net, buses[70], lines[122], 'l', closed=False, type='LBS', name='S13', index=None)
        pp.create_switch(net, buses[38], lines[122], 'l', closed=False, type='LBS', name='S13', index=None)
        pp.create_switch(net, buses[12], lines[12], 'l', closed=False, type='LBS', name='S14', index=None)


        pp.create_switch(net, buses[22], lines[23], 'l', closed=True, type='LBS', name='S15', index=None)
        #pp.create_switch(net, buses[41], lines[41], 'l', closed=True, type='LBS', name='S17', index=None)
        pp.create_switch(net, buses[48], lines[47], 'l', closed=True, type='LBS', name='S16', index=None)
        pp.create_switch(net, buses[71], lines[71], 'l', closed=True, type='LBS', name='S17', index=None)
        #pp.create_switch(net, buses[79], lines[79], 'l', closed=True, type='LBS', name='S20', index=None)
        #pp.create_switch(net, buses[88], lines[88], 'l', closed=True, type='LBS', name='S21', index=None)

        # Shunt
        #pp.create_shunt_as_capacitor(net, buses[82], q_mvar=-0.200, loss_factor=0) #capacitor at bus 83
        #pp.create_shunt_as_capacitor(net, buses[87], q_mvar=-0.50, loss_factor=0) #capacitor at bus 88
        #pp.create_shunt_as_capacitor(net, buses[89], 50, 0) #capacitor at bus 90
        #pp.create_shunt_as_capacitor(net, buses[91], 50, 0) #capacitor at bus 92

        # Loads
        df_load = pd.read_excel('networks/ieee123_loaddata.xlsx')
        load_no = len(df_load)
        for i in range(load_no):
            if df_load['Load'][i] == 'Y-PQ' or df_load['Load'][i] == 'D-PQ':
                const_z_percent = 0
                const_i_percent = 0
            elif df_load['Load'][i] == 'Y-I' or df_load['Load'][i] == 'D-I':
                const_z_percent = 0
                const_i_percent = 100
            elif df_load['Load'][i] == 'Y-Z' or df_load['Load'][i] == 'D-Z':
                const_z_percent = 100
                const_i_percent = 0
            else:
                print(df_load['Load'][i], " ERROR!")
            pp.create_load(
                net=net, 
                bus=df_load['Node'][i], 
                p_mw=df_load['kW'][i]/2000,  # 3phase->1phase 및 kW->mW 고려
                q_mvar=df_load['kVAr'][i]/2000,  # 3phase->1phase 및 kVAr->mVAr 고려
                const_z_percent=const_z_percent,
                const_i_percent=const_i_percent,
                scaling=1., 
                in_service=True, 
                name='Load'+str(i+1))

        load_rate=1
        net.load['p_mw']/=load_rate
        net.load['q_mvar']/=load_rate

        # Optional distributed energy recources
        if with_der in ['pv_wind', 'all']:
            dres_rate = 1
            pp.create_sgen(net, buses[3], p_mw=0.400, q_mvar=0, scaling=1., name='WT1', type='WT')
            pp.create_sgen(net, buses[26], p_mw=0.400, q_mvar=0, scaling=1., name='WT2', type='WT')
            pp.create_sgen(net, buses[41], p_mw=0.400, q_mvar=0, scaling=1., name='WT3', type='WT')
            pp.create_sgen(net, buses[56], p_mw=0.400, q_mvar=0, scaling=1., name='PV1', type='PV')
            pp.create_sgen(net, buses[63], p_mw=0.400, q_mvar=0, scaling=1., name='PV2', type='PV')
            pp.create_sgen(net, buses[69], p_mw=0.400, q_mvar=0, scaling=1., name='PV3', type='PV')
            pp.create_sgen(net, buses[86], p_mw=0.400, q_mvar=0, scaling=1., name='PV4', type='PV')
            pp.create_sgen(net, buses[96], p_mw=0.400, q_mvar=0, scaling=1., name='PV5', type='PV')

            pp.create_sgen(net, buses[16], p_mw=0.400, q_mvar=0, scaling=1., name='WT4', type='WT')
            pp.create_sgen(net, buses[19], p_mw=0.400, q_mvar=0, scaling=1., name='WT5', type='WT')
            pp.create_sgen(net, buses[29], p_mw=0.400, q_mvar=0, scaling=1., name='WT6', type='WT')
            pp.create_sgen(net, buses[49], p_mw=0.400, q_mvar=0, scaling=1., name='WT7', type='WT')

            pp.create_sgen(net, buses[94], p_mw=0.400, q_mvar=0, scaling=1., name='PV6', type='PV')
            pp.create_sgen(net, buses[78], p_mw=0.400, q_mvar=0, scaling=1., name='PV7', type='PV')
            pp.create_sgen(net, buses[113], p_mw=0.400, q_mvar=0, scaling=1., name='PV8', type='PV')
            pp.create_sgen(net, buses[38], p_mw=0.400, q_mvar=0, scaling=1., name='PV9', type='PV')

            if with_der in ['all']:
                # p_mw는 PCS Capacity, max_e_mwh는 Battery Capacity, soc_percent는 [0,1]로 정의, scaling으로 출력 조절
                # utils/pp_ess_simulator.py 참고
                pp.create_storage(net, buses[12], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS1', type='BESS')
                pp.create_storage(net, buses[20], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS2', type='BESS')
                pp.create_storage(net, buses[40], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS3', type='BESS')
                pp.create_storage(net, buses[50], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS4', type='BESS')
                pp.create_storage(net, buses[53], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS5', type='BESS')
                pp.create_storage(net, buses[100], p_mw=-0.200,max_e_mwh=0.600,soc_percent=0.9, scaling=1., name='ESS6', type='BESS')
                pp.create_storage(net, buses[86], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS7', type='BESS')
                pp.create_storage(net, buses[77], p_mw=-0.200, max_e_mwh=0.600, soc_percent=0.9, scaling=1., name='ESS8', type='BESS')

            net.sgen['p_mw']/=dres_rate
        return net
    
    
# just for testing
if __name__ == "__main__":
    import numpy as np
    
    network_name= 'ieee123'
    der_opt = 'pv_wind'    
    network = create_network(network_name, der_opt)
    net = network.net
    net.sgen.loc[net.sgen.type=='WT','scaling']=1
    net.sgen.loc[net.sgen.type=='PV','scaling']=1
    net.load['scaling']=1
    
    print(net)
    if der_opt=='all': print(net.storage)
    net.storage['scaling']=0
    #print(net.switch)
    net.switch['closed']=True
    #print(net.switch)
    net.switch['closed']=np.bool_([1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1])
    #print(net.switch)

    pp.runpp(net)
    if der_opt=='all': 
        net.storage['scaling']=0.45
        print(net.storage)
        print(net.res_storage)
        #idx=net.storage[net.storage['name']=='ESS2'].index.values[0]
        #print(idx)
        net.storage.at[2,'scaling']=0.1
        print(net.storage.loc[1])
        print(net.storage)

    #print(list(net.res_bus['vm_pu']-1))
    #print(list(net.res_line['loading_percent']/100))
    #print(list((net.switch['closed']*1.)))
    #print(net.name)
    print(len(net.line))
    print(len(net.bus))
    print(len(net.switch))
    print(len(net.sgen))
    print(len(net.load))
