import configparser as cp
import os
import sys


class config:
    def __init__(self):
        self.run_name = "mobius_run"
        # Anand: ISSUE #2. Patch
        # self.use_user_bandwidth = False

        #package
        self.conv_number_of_chiplet= 5
        self.sa_number_of_chiplet = 5
        self.nop_bw = 63

        #chiplet(CNPU)
        self.cnpu_number_of_layer = 4
        self.cnpu_global_buffer_size = 2560
        self.cnpu_router_per_global_buffer = 3
        #chiplet(SAPU)
        self.sapu_number_of_layer = 4
        self.sapu_global_buffer_size = 2560
        self.sapu_router_per_global_buffer = 3

        #CNPU
        self.cn_array_rows = 256
        self.cn_array_cols = 256
        self.cn_ifmap_sz_kb = 512
        self.cn_filter_sz_kb = 512
        self.cn_ofmap_sz_kb = 256
        self.cnpu_noc_bw = 38
        self.cn_ifmap_offset = 0
        self.cn_filter_offset = 10000000
        self.cn_ofmap_offset = 20000000
        self.cn_bandwidths = []
        self.cn_dataflow = 'ws'  
        #SAPU
        self.sa_array_rows = 256
        self.sa_array_cols = 256
        self.sa_ifmap_sz_kb = 512
        self.sa_filter_sz_kb = 512
        self.sa_ofmap_sz_kb = 256
        self.sapu_noc_bw = 38
        self.sa_ifmap_offset = 0
        self.sa_filter_offset = 10000000
        self.sa_ofmap_offset = 20000000
        self.sa_bandwidths = []
        self.sa_dataflow = 'ws'
        #Parallelism
        self.parallelism = 'COL'

        self.topofile = ""
        self.valid_conf_flag = False
        self.valid_df_list = ['os', 'ws', 'is']
        self.valid_paral_list = ['COL','ROW']
    #
    def read_mobius_config(self, conf_file_in):
        #log
        if not os.path.exists(conf_file_in):
            print("ERROR:Config file not found") 
            print("Input file:" + conf_file_in)
            print('Exiting')
            exit()
        else: 
            print("\n")
            print("Config file found") 
            print("Input file:" + conf_file_in)
            print('Loading')
        #load operation
        config = cp.ConfigParser()
        config.read(conf_file_in)
        # print(config.has_section('Package')) 

        section = 'general'
        self.run_name = config.get(section, 'run_name')

        section = 'Package'
        self.conv_number_of_chiplet = int(config.get(section, 'Number_of_Conv_Chiplet'))
        self.sa_number_of_chiplet = int(config.get(section, 'Number_of_Self-attention_Chiplet'))
        self.nop_bw = int(config.get(section, 'nop_bandwidth'))

        section = 'Chiplet_Conv'
        self.cnpu_number_of_layer = int(config.get(section, 'Number_of_LAYER'))
        self.cnpu_global_buffer_size = int(config.get(section, 'Global_Buffer_Size'))
        self.cnpu_router_per_global_buffer = int(config.get(section, 'Routers_per_Global_Buffer'))
        self.cnpu_noc_bw = int(config.get(section, 'noc_bandwidth'))

        section = 'Chiplet_SA'
        self.sapu_number_of_layer = int(config.get(section, 'Number_of_LAYER'))
        self.sapu_global_buffer_size = int(config.get(section, 'Global_Buffer_Size'))
        self.sapu_router_per_global_buffer = int(config.get(section, 'Routers_per_Global_Buffer'))
        self.sapu_noc_bw = int(config.get(section, 'noc_bandwidth'))

        section = 'CNPU'
        self.cn_array_rows = int(config.get(section, 'ArrayHeight'))
        self.cn_array_cols = int(config.get(section, 'ArrayWidth'))
        self.cn_ifmap_sz_kb = int(config.get(section, 'ifmapsramszkB'))
        self.cn_filter_sz_kb = int(config.get(section, 'filtersramszkB'))
        self.cn_ofmap_sz_kb = int(config.get(section, 'ofmapsramszkB'))
        self.cn_ifmap_offset = int(config.get(section, 'IfmapOffset'))
        self.cn_filter_offset = int(config.get(section, 'FilterOffset'))
        self.cn_ofmap_offset = int(config.get(section, 'OfmapOffset'))
        self.cn_df = config.get(section, 'Dataflow')
        self.cn_bandwidths = int(config.get(section, 'Bandwidth'))

        section = 'SAPU'
        self.sa_array_rows = int(config.get(section, 'ArrayHeight'))
        self.sa_array_cols = int(config.get(section, 'ArrayWidth'))
        self.sa_ifmap_sz_kb = int(config.get(section, 'ifmapsramszkB'))
        self.sa_filter_sz_kb = int(config.get(section, 'filtersramszkB'))
        self.sa_ofmap_sz_kb = int(config.get(section, 'ofmapsramszkB'))
        self.sa_ifmap_offset = int(config.get(section, 'IfmapOffset'))
        self.sa_filter_offset = int(config.get(section, 'FilterOffset'))
        self.sa_ofmap_offset = int(config.get(section, 'OfmapOffset'))
        self.sa_df = config.get(section, 'Dataflow')
        self.sa_bandwidths = int(config.get(section, 'Bandwidth'))

        #load bandwidth
        section = 'run_presets'
        CN_bw_mode_string = config.get(section, 'CN_InterfaceBandwidth')
        self.cn_bw_mode = config.get(section, 'CN_InterfaceBandwidth')
        SA_bw_mode_string = config.get(section, 'SA_InterfaceBandwidth')
        self.sa_bw_mode = config.get(section, 'SA_InterfaceBandwidth')

        self.parallelism = config.get(section, 'Parallelism')

        if CN_bw_mode_string == 'USER':
            self.cn_use_user_bandwidth = True
        elif CN_bw_mode_string == 'CALC':
            self.cn_use_user_bandwidth = False
        else:
            message = 'Use either USER or CALC in CN_InterfaceBandwidth feild. Aborting!'
            return
       
        if SA_bw_mode_string == 'USER':
            self.sa_use_user_bandwidth = True
        elif SA_bw_mode_string == 'CALC':
            self.sa_use_user_bandwidth = False
        else:
            message = 'Use either USER or CALC in SA_InterfaceBandwidth feild. Aborting!'
            return

        # if self.cn_use_user_bandwidth:
        #     self.cn_bandwidths = [int(x.strip())
        #                        for x in config.get('CNPU', 'Bandwidth').strip().split(',')]

        # if self.sa_use_user_bandwidth:
        #     self.sa_bandwidths = [int(x.strip())
        #                        for x in config.get('SAPU', 'Bandwidth').strip().split(',')]

        if self.cn_dataflow not in self.valid_df_list:
            print("ERROR: Invalid CNPU dataflow.  Dataflow: ws/os/is")

        if self.sa_dataflow not in self.valid_df_list:
            print("ERROR: Invalid SAPU dataflow.  Dataflow: ws/os/is")

        if self.parallelism not in self.valid_paral_list:
            print("ERROR: Invalid Parallelism.  COL/ROW")

        # if config.has_section('network_presets'):  # Read network_presets
        #     self.topofile = config.get(section, 'TopologyCsvLoc').split('"')[1]
        self.valid_conf_flag = True

    def print_mobius_config(self):
        print("\n")
        print("====================================================")
        print("******************* HEX SIM *********************")
        print("====================================================")
        print("Parallelism:\t"+ str(self.parallelism))
        print("==================   Package  ======================")
        print("Number_of_CPU: 1")
        print("Number_of_Conv_Chiplet: \t"+ str(self.conv_number_of_chiplet))
        print("Number_of_SA_Chiplet: \t"+ str(self.sa_number_of_chiplet))
        print("Number_of_HBM : 1")
        print("Interconnect : GRS")
        print("NOP_Bandwidth (Byte/s/Chiplet):\t" + str(self.nop_bw) )

        print("==================Chiplet_Conv======================")
        print("Number_of_LAYER: \t"+ str(self.cnpu_number_of_layer))
        print("Global_Buffer_Size (KB): \t"+ str(self.cnpu_global_buffer_size))
        print("Routers_per_Global_Buffer : \t"+ str(self.cnpu_router_per_global_buffer))
        print("NOC_Bandwidth (Byte/s/PU):\t" + str(self.cnpu_noc_bw))
        print("Core : RISC-V")

        print("==================Chiplet_SA======================")
        print("Number_of_LAYER: \t"+ str(self.sapu_number_of_layer))
        print("Global_Buffer_Size (KB): \t"+ str(self.sapu_global_buffer_size))
        print("Routers_per_Global_Buffer: \t"+ str(self.sapu_router_per_global_buffer))
        print("NOC_Bandwidth (Byte/s/PU):\t" + str(self.sapu_noc_bw))
        print("Core : RISC-V")

        print("==================   CNPU   ======================")
        print("Array Size: \t"+ str(self.cn_array_rows) + "x" + str(self.cn_array_cols))
        print("SRAM IFMAP (KB): \t"+ str(self.cn_ifmap_sz_kb))
        print("SRAM Filter (KB): \t"+ str(self.cn_filter_sz_kb))
        print("SRAM OFMAP (KB): \t"+ str(self.cn_ofmap_sz_kb))
        print("Dataflow: \t" + str(self.cn_df))
        
        if self.cn_use_user_bandwidth:
            print("Bandwidth: \t" + str(self.cn_bandwidths))
            print('Working in USE USER BANDWIDTH mode.')
        else:
            print('Working in ESTIMATE BANDWIDTH mode.')

        print("==================   SAPU   ======================")
        print("Array Size: \t"+ str(self.sa_array_rows) + "x" + str(self.sa_array_cols))
        print("SRAM IFMAP (KB): \t"+ str(self.sa_ifmap_sz_kb))
        print("SRAM Filter (KB): \t"+ str(self.sa_filter_sz_kb))
        print("SRAM OFMAP (KB): \t"+ str(self.sa_ofmap_sz_kb))
        print("Dataflow: \t" + str(self.sa_df))
        
        if self.sa_use_user_bandwidth:
            print("Bandwidth: \t" + str(self.sa_bandwidths))
            print('Working in USE USER BANDWIDTH mode.')
        else:
            print('Working in ESTIMATE BANDWIDTH mode.')


        print("====================================================")
    
    def write_cnpu_conf(self, conf_file_out):
        if not self.valid_conf_flag:
            print('ERROR: config.write_pu_conf: No valid config loaded')
            return

        config = cp.ConfigParser()

        section = 'general'
        config.add_section(section)
        config.set(section, 'run_name', str(self.run_name))

        section = 'architecture_presets'
        config.add_section(section)
        config.set(section, 'ArrayHeight', str(self.cn_array_rows))
        config.set(section, 'ArrayWidth', str(self.cn_array_cols))

        config.set(section, 'ifmapsramszkB', str(self.cn_ifmap_sz_kb))
        config.set(section, 'filtersramszkB', str(self.cn_filter_sz_kb))
        config.set(section, 'ofmapsramszkB', str(self.cn_ofmap_sz_kb))

        config.set(section, 'IfmapOffset', str(self.cn_ifmap_offset))
        config.set(section, 'FilterOffset', str(self.cn_filter_offset))
        config.set(section, 'OfmapOffset', str(self.cn_ofmap_offset))

        config.set(section, 'Dataflow', str(self.cn_df))
        config.set(section, 'Bandwidth',str(self.cn_bandwidths))

        section = 'run_presets'
        config.add_section(section)
        config.set(section, 'InterfaceBandwidth', str(self.cn_bw_mode))
        # section = 'network_presets'
        # config.add_section(section)
        # topofile = '"' + self.topofile + '"'
        # config.set(section, 'TopologyCsvLoc', str(topofile))

        with open(conf_file_out, 'w') as configfile:
            config.write(configfile)

    def write_sapu_conf(self, conf_file_out):
        if not self.valid_conf_flag:
            print('ERROR: config.write_sa_conf: No valid config loaded')
            return

        config = cp.ConfigParser()

        section = 'general'
        config.add_section(section)
        config.set(section, 'run_name', str(self.run_name))

        section = 'architecture_presets'
        config.add_section(section)
        config.set(section, 'ArrayHeight', str(self.sa_array_rows))
        config.set(section, 'ArrayWidth', str(self.sa_array_cols))

        config.set(section, 'ifmapsramszkB', str(self.sa_ifmap_sz_kb))
        config.set(section, 'filtersramszkB', str(self.sa_filter_sz_kb))
        config.set(section, 'ofmapsramszkB', str(self.sa_ofmap_sz_kb))

        config.set(section, 'IfmapOffset', str(self.sa_ifmap_offset))
        config.set(section, 'FilterOffset', str(self.sa_filter_offset))
        config.set(section, 'OfmapOffset', str(self.sa_ofmap_offset))

        config.set(section, 'Dataflow', str(self.sa_df))
        config.set(section, 'Bandwidth',str(self.sa_bandwidths))

        section = 'run_presets'
        config.add_section(section)
        config.set(section, 'InterfaceBandwidth', str(self.sa_bw_mode))
        # section = 'network_presets'
        # config.add_section(section)
        # topofile = '"' + self.topofile + '"'
        # config.set(section, 'TopologyCsvLoc', str(topofile))

        with open(conf_file_out, 'w') as configfile:
            config.write(configfile)

    def change_decoder_chiplet_scale(self,top_config_pace,scale):
        encoder_chiplet_number = 10-scale
        decoder_chiplet_number = scale

        config = cp.ConfigParser()
        config.read(top_config_pace,encoding="utf-8")
        section = 'Package'
        # print(config.has_section('Package')) 
        config.set(section, 'Number_of_Conv_Chiplet', str(encoder_chiplet_number))
        config.set(section, 'Number_of_Self-attention_Chiplet', str(scale))
        with open(top_config_pace, 'w') as configfile:
            config.write(configfile)

    def change_chiplet_layer(self,top_config_pace,layer):
        config = cp.ConfigParser()
        config.read(top_config_pace,encoding="utf-8")
        config.set('Chiplet_Conv', 'number_of_layer', str(layer))
        config.set('Chiplet_SA', 'number_of_layer', str(layer))
        with open(top_config_pace, 'w') as configfile:
            config.write(configfile)

    def change_gb_size(self,top_config_pace,gb_size):
        config = cp.ConfigParser()
        config.read(top_config_pace,encoding="utf-8")
        config.set('Chiplet_Conv', 'global_buffer_size', str(gb_size))
        config.set('Chiplet_SA', 'global_buffer_size', str(gb_size))
        with open(top_config_pace, 'w') as configfile:
            config.write(configfile)

    def change_nop_bw(self,top_config_pace,nop_bw):
        config = cp.ConfigParser()
        config.read(top_config_pace,encoding="utf-8")
        config.set('Package', 'nop_bandwidth', str(nop_bw))       
        with open(top_config_pace, 'w') as configfile:
            config.write(configfile)

    def change_noc_bw(self,top_config_pace,noc_bw):
        config = cp.ConfigParser()
        config.read(top_config_pace,encoding="utf-8")
        config.set('Chiplet_Conv', 'noc_bandwidth', str(noc_bw))
        config.set('Chiplet_SA', 'noc_bandwidth', str(noc_bw))
        with open(top_config_pace, 'w') as configfile:
            config.write(configfile)