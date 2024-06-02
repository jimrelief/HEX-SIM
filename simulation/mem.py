from config import config
from topology import topologies
# from scalesim.simulator import simulator 
import math
import os
import sys

class mem:
    def __init__(self):
        self.config = config()
        self.topo = topologies()
        # self.simulator = simulator()

        self.gb_feature_in_list = []
        self.gb_weight_in_list = []
        self.gb_feature_out_list = []

        self.lb_feature_in_list = []
        self.lb_weight_in_list = []
        self.lb_feature_out_list = []

        self.gb_feature_in = 0
        self.gb_weight_in = 0
        self.gb_feature_out = 0

        self.lb_feature_in = 0
        self.lb_weight_in = 0
        self.lb_feature_out = 0

        self.bw_input = 0
        self.bw_filter = 0
        # self.bw_output = 0

        self.write_gb_bw = 0
        self.read_gb_bw = 0
        self.write_lb_bw = 0
        self.read_lb_bw = 0

        self.write_lb_clk = 0
        self.write_lb_stall_clk = 0
        self.write_gb_clk = 0
        self.write_gb_stall_clk = 0

        self.read_lb_clk = 0
        self.read_lb_stall_clk = 0
        self.read_gb_clk = 0
        self.read_gb_stall_clk = 0
    
    #top_conf_pace 顶层conf
    #top_topo_pace 没处理前topo
    #config_type "conv"、"sa"
    def mem_data_gen(self,top_conf_pace,top_topo_pace,config_type):
        # self.mem_data_params = []
        # config = config()
        self.config.read_mobius_config(top_conf_pace)
        #config params
        cn_chiplet = self.config.conv_number_of_chiplet
        cn_layer =  self.config.cnpu_number_of_layer
        cn_router =  self.config.cnpu_router_per_global_buffer
        cnpu_number = cn_layer * (cn_router + 1)

        sa_chiplet =  self.config.sa_number_of_chiplet
        sa_layer = self.config.sapu_number_of_layer
        sa_router =  self.config.sapu_router_per_global_buffer
        sapu_number = sa_layer * (sa_router + 1)

        # topo = topologies()
        self.topo.load_arrays_conv(top_topo_pace)
        layer_number = self.topo.get_num_layers()

        for i in range(layer_number):
            # ifmap_rows, ifmap_cols = topo.get_layer_ifmap_dims(i)
            mac_number = self.topo.get_layer_num_operation(i)
            filter_rows, filter_cols = self.topo.get_layer_filter_dims(i)
            num_input_channels = self.topo.get_layer_num_channels(i)
            num_filters = self.topo.get_layer_num_filters(i)
            filter_data =  filter_rows * filter_cols * num_input_channels

            if self.config.parallelism == "COL" :
                if config_type == "encoding" :
                    self.gb_feature_in =  mac_number * filter_data * 4
                    self.gb_weight_in = filter_data * math.ceil(num_filters/cn_chiplet) * 4
                    self.gb_feature_out = mac_number * math.ceil(num_filters/cn_chiplet) * 4
                    
                    self.lb_feature_in =  mac_number * filter_data * 4
                    self.lb_weight_in = filter_data * math.ceil(num_filters/cn_chiplet/cnpu_number) * 4
                    self.lb_feature_out = mac_number * math.ceil(num_filters/cn_chiplet/cnpu_number) * 4
                elif config_type == "decoding" :
                    self.gb_feature_in =  mac_number * filter_data * 4
                    self.gb_weight_in = filter_data * math.ceil(num_filters/sa_chiplet) * 4
                    self.gb_feature_out = mac_number * math.ceil(num_filters/sa_chiplet) * 4
                    
                    self.lb_feature_in =  mac_number * filter_data * 4
                    self.lb_weight_in = filter_data * math.ceil(num_filters/sa_chiplet/sapu_number) * 4
                    self.lb_feature_out = mac_number * math.ceil(num_filters/sa_chiplet/sapu_number) * 4
                else :
                    print("ERROR: mem_data_gen.Invalid topo type")

            if  self.config.parallelism == "ROW":
                if config_type == "encoding" :
                    self.gb_feature_in =  mac_number * math.ceil(filter_data/cn_chiplet) * 4
                    self.gb_weight_in = math.ceil(filter_data/cn_chiplet) * num_filters * 4
                    self.gb_feature_out = mac_number * num_filters * 4
                    
                    self.lb_feature_in =  mac_number * math.ceil(filter_data/cn_chiplet/cnpu_number) * 4
                    self.lb_weight_in = math.ceil(filter_data/cn_chiplet/cnpu_number) * num_filters * 4
                    self.lb_feature_out = mac_number * num_filters * 4
                elif config_type == "decoding" :
                    self.gb_feature_in =  mac_number * math.ceil(filter_data/sa_chiplet) * 4
                    self.gb_weight_in = math.ceil(filter_data/sa_chiplet) * num_filters * 4
                    self.gb_feature_out = mac_number * num_filters * 4
                    
                    self.lb_feature_in =  mac_number * math.ceil(filter_data/sa_chiplet/sapu_number) * 4
                    self.lb_weight_in = math.ceil(filter_data/sa_chiplet/sapu_number) * num_filters * 4
                    self.lb_feature_out = mac_number * num_filters * 4
                else :
                    print("ERROR: mem_data_gen.Invalid topo type")

            self.gb_feature_in_list.append(self.gb_feature_in)
            self.gb_weight_in_list.append(self.gb_weight_in)
            self.gb_feature_out_list.append(self.gb_feature_out)

            self.lb_feature_in_list.append(self.lb_feature_in)
            self.lb_weight_in_list.append(self.lb_weight_in)
            self.lb_feature_out_list.append(self.lb_feature_out)
        # print("gb_feature_in")
        # for element in self.gb_feature_in_list:
        #     print(element) 
        # print("gb_weight_in")   
        # for element in self.gb_weight_in_list:
        #     print(element)
        # print("gb_feature_out")
        # for element in self.gb_feature_out_list:
        #     print(element) 

        # print("lb_feature_in")
        # for element in self.lb_feature_in_list:
        #     print(element) 
        # print("lb_weight_in")   
        # for element in self.lb_weight_in_list:
        #     print(element)
        # print("lb_feature_out")
        # for element in self.lb_feature_out_list:
        #     print(element) 

     # input/filter
    def cn_write_global_buffer(self,gb_data_in,bw_write_lb,bw_write_gb):
        global_buffer_size = self.config.cnpu_global_buffer_size
        gb_doublebuffer_size = int((global_buffer_size*1024)/3/2)
        gb_fill_time = math.ceil( gb_data_in / gb_doublebuffer_size) -1
        last_mem = int(gb_data_in % gb_doublebuffer_size)
        number_router = self.config.cnpu_router_per_global_buffer
        print(gb_fill_time)

        user_mode =self.config.cn_use_user_bandwidth
        if user_mode :
            noc_bw = self.config.cnpu_noc_bw*number_router
            nop_bw = self.config.nop_bw
        else:
            noc_bw = bw_write_lb*number_router
            nop_bw = bw_write_gb

        if gb_fill_time == 0:
            self.write_gb_stall_clk = max(0,(int(last_mem/nop_bw - last_mem/noc_bw)))
            # if noc_bw > nop_bw:
            #     self.write_gb_clk = int(last_mem/nop_bw + self.write_gb_stall_clk)
            # else:
            #     self.write_gb_clk = int(last_mem/noc_bw + self.write_gb_stall_clk)
            self.write_gb_clk = int(last_mem/nop_bw + self.write_gb_stall_clk)
        else:
            self.write_gb_stall_clk = max(0,(int((gb_doublebuffer_size/nop_bw-gb_doublebuffer_size/noc_bw) * gb_fill_time ))) + max(0,(int(last_mem/nop_bw - last_mem/noc_bw)))
            # if noc_bw > nop_bw:
            #     self.write_gb_clk = int( gb_doublebuffer_size/nop_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)
            # else:
            #     self.write_gb_clk = int( gb_doublebuffer_size/noc_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)   
            self.write_gb_clk = int( gb_doublebuffer_size/nop_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)     
        return self.write_gb_stall_clk,self.write_gb_clk

    def sa_write_global_buffer(self,gb_data_in,bw_write_lb,bw_write_gb):
        global_buffer_size = self.config.sapu_global_buffer_size
        gb_doublebuffer_size = int((global_buffer_size*1024)/3/2)
        gb_fill_time = math.ceil( gb_data_in / gb_doublebuffer_size) -1
        last_mem = int(gb_data_in % gb_doublebuffer_size)
        number_router = self.config.sapu_router_per_global_buffer
        print(gb_fill_time)


        user_mode =self.config.sa_use_user_bandwidth
        if user_mode :
            noc_bw = self.config.sapu_noc_bw*number_router
            nop_bw = self.config.nop_bw
        else:
            noc_bw = bw_write_lb*number_router
            nop_bw = bw_write_gb

        if gb_fill_time == 0:
            self.write_gb_stall_clk = max(0,(int(last_mem/nop_bw - last_mem/noc_bw)))
            # if noc_bw > nop_bw:
            #     self.write_gb_clk = int(last_mem/nop_bw + self.write_gb_stall_clk)
            # else:
            #     self.write_gb_clk = int(last_mem/noc_bw + self.write_gb_stall_clk)
            self.write_gb_clk = int(last_mem/nop_bw + self.write_gb_stall_clk)
        else:
            self.write_gb_stall_clk = max(0,(int((gb_doublebuffer_size/nop_bw-gb_doublebuffer_size/noc_bw) * gb_fill_time ))) + max(0,(int(last_mem/nop_bw - last_mem/noc_bw)))
            # if noc_bw > nop_bw:
            #     self.write_gb_clk = int( gb_doublebuffer_size/nop_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)
            # else:
            #     self.write_gb_clk = int( gb_doublebuffer_size/noc_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)   
            self.write_gb_clk = int( gb_doublebuffer_size/nop_bw * gb_fill_time + last_mem/nop_bw + self.write_gb_stall_clk)     
        return self.write_gb_stall_clk,self.write_gb_clk

    # input/filter
    def cn_write_local_buffer(self,lb_data_in,lb_type,bw):
        # self.bw_input =  self.simulator.bw_input_list[layer]
        # self.bw_filter = self.simulator.bw_filter_list[layer]
        if lb_type == "input":
            loacl_buffer_size = self.config.cn_ifmap_sz_kb
        elif lb_type == "filter":
            loacl_buffer_size = self.config.cn_filter_sz_kb
        else:
            print("ERROR LBTYPE")

        lb_doublebuffer_size = int((loacl_buffer_size*1024)/2)
        lb_fill_time = math.ceil( lb_data_in / lb_doublebuffer_size) -1
        last_mem = int(lb_data_in % lb_doublebuffer_size)
        print(lb_fill_time)


        user_mode =self.config.cn_use_user_bandwidth
        if user_mode :
            noc_bw = self.config.cnpu_noc_bw
        else:
            noc_bw = bw

        if lb_fill_time == 0:
            self.write_lb_stall_clk = max(0,(int(last_mem/noc_bw - last_mem/bw)))
            # if bw > noc_bw:
            #     self.write_lb_clk = int(last_mem/noc_bw+ self.write_lb_stall_clk);
            # else:
            #     self.write_lb_clk = int(last_mem/bw+ self.write_lb_stall_clk);
            self.write_lb_clk = int(last_mem/noc_bw+ self.write_lb_stall_clk);    
        else:
            self.write_lb_stall_clk = max(0,(int((lb_doublebuffer_size/noc_bw - lb_doublebuffer_size/bw )* lb_fill_time))) + max(0,(int(last_mem/noc_bw - last_mem/bw)))
            # if bw > noc_bw:
            #     self.write_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_fill_time +last_mem/noc_bw+ self.write_lb_stall_clk);  
            # else:
            #     self.write_lb_clk = int(lb_doublebuffer_size/bw * lb_fill_time +last_mem/bw+ self.write_lb_stall_clk);
            self.write_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_fill_time +last_mem/noc_bw+ self.write_lb_stall_clk);            
        # print(self.write_lb_stall_clk,self.write_lb_clk )
        return self.write_lb_stall_clk,self.write_lb_clk

    def sa_write_local_buffer(self,lb_data_in,lb_type,bw):
        # self.bw_input =  self.simulator.bw_input_list[layer]
        # self.bw_filter = self.simulator.bw_filter_list[layer]
        if lb_type == "input":
            loacl_buffer_size = self.config.sa_ifmap_sz_kb
        elif lb_type == "filter":
            loacl_buffer_size = self.config.sa_filter_sz_kb
        else:
            print("ERROR LBTYPE")

        lb_doublebuffer_size = int((loacl_buffer_size*1024)/2)
        lb_fill_time = math.ceil( lb_data_in / lb_doublebuffer_size) -1
        last_mem = int(lb_data_in % lb_doublebuffer_size)
        print(lb_fill_time)

        user_mode =self.config.sa_use_user_bandwidth
        if user_mode :
            noc_bw = self.config.sapu_noc_bw
        else:
            noc_bw = bw

        if lb_fill_time == 0:
            self.write_lb_stall_clk = max(0,(int(last_mem/noc_bw - last_mem/bw)))
            # if bw > noc_bw:
            #     self.write_lb_clk = int(last_mem/noc_bw+ self.write_lb_stall_clk);
            # else:
            #     self.write_lb_clk = int(last_mem/bw+ self.write_lb_stall_clk);
            self.write_lb_clk = int(last_mem/noc_bw+ self.write_lb_stall_clk);    
        else:
            self.write_lb_stall_clk = max(0,(int((lb_doublebuffer_size/noc_bw - lb_doublebuffer_size/bw )* lb_fill_time))) + max(0,(int(last_mem/noc_bw - last_mem/bw)))
            # if bw > noc_bw:
            #     self.write_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_fill_time +last_mem/noc_bw+ self.write_lb_stall_clk);  
            # else:
            #     self.write_lb_clk = int(lb_doublebuffer_size/bw * lb_fill_time +last_mem/bw+ self.write_lb_stall_clk);
            self.write_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_fill_time +last_mem/noc_bw+ self.write_lb_stall_clk);           
        # print(self.write_lb_stall_clk,self.write_lb_clk )
        return self.write_lb_stall_clk,self.write_lb_clk

    def cn_read_global_buffer(self,gb_data_out,bw_read_lb,bw_read_gb):
        global_buffer_size = self.config.cnpu_global_buffer_size
        gb_doublebuffer_size = (global_buffer_size*1024)/3/2
        gb_read_time = math.ceil( gb_data_out / gb_doublebuffer_size) -1
        last_mem = int(gb_data_out % gb_doublebuffer_size)
        number_router = self.config.cnpu_router_per_global_buffer
        chiplet_number = self.config.conv_number_of_chiplet
        print(gb_read_time)
        # nop_bw = 512/chiplet_number
        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            noc_bw = self.config.cnpu_noc_bw*number_router
            nop_bw = self.config.nop_bw
        else:
            noc_bw = bw_read_lb*number_router
            nop_bw = bw_read_gb
        
        if gb_read_time==0:
            self.read_gb_stall_clk = max(0,(int(last_mem/noc_bw - last_mem/nop_bw)))
            # if noc_bw > nop_bw:
            #     self.read_gb_clk = int(last_mem/nop_bw) + self.read_gb_stall_clk
            # else:
            #     self.read_gb_clk = int(last_mem/noc_bw) + self.read_gb_stall_clk
            self.read_gb_clk = int(last_mem/nop_bw) + self.read_gb_stall_clk 
        else:
            self.read_gb_stall_clk = max(0,(int((gb_doublebuffer_size/noc_bw-gb_doublebuffer_size/nop_bw)*gb_read_time)) )+ max(0,(int(last_mem/noc_bw - last_mem/nop_bw)))
            # if noc_bw > nop_bw:
            #     self.read_gb_clk = int(gb_doublebuffer_size/nop_bw) * gb_read_time + int(last_mem/nop_bw) + self.read_gb_stall_clk
            # else:
            #     self.read_gb_clk = int(gb_doublebuffer_size/noc_bw) * gb_read_time + int(last_mem/noc_bw) + self.read_gb_stall_clk 
            self.read_gb_clk = int(gb_doublebuffer_size/nop_bw) * gb_read_time + int(last_mem/nop_bw) + self.read_gb_stall_clk
        return self.read_gb_stall_clk,self.read_gb_clk

    def sa_read_global_buffer(self,gb_data_out,bw_read_lb,bw_read_gb):
        global_buffer_size = self.config.sapu_global_buffer_size
        gb_doublebuffer_size = (global_buffer_size*1024)/3/2
        gb_read_time = math.ceil( gb_data_out / gb_doublebuffer_size) -1
        last_mem = int(gb_data_out % gb_doublebuffer_size)
        number_router = self.config.sapu_router_per_global_buffer
        chiplet_number = self.config.sa_number_of_chiplet
        print(gb_read_time)
        # nop_bw = 512/chiplet_number
         # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            noc_bw = self.config.sapu_noc_bw*number_router
            nop_bw = self.config.nop_bw
        else:
            noc_bw = bw_read_lb*number_router
            nop_bw = bw_read_gb
        
        if gb_read_time==0:
            self.read_gb_stall_clk = max(0,(int(last_mem/noc_bw - last_mem/nop_bw)))
            # if noc_bw > nop_bw:
            #     self.read_gb_clk = int(last_mem/nop_bw) + self.read_gb_stall_clk
            # else:
            #     self.read_gb_clk = int(last_mem/noc_bw) + self.read_gb_stall_clk
            self.read_gb_clk = int(last_mem/nop_bw) + self.read_gb_stall_clk 
        else:
            self.read_gb_stall_clk = max(0,(int((gb_doublebuffer_size/noc_bw-gb_doublebuffer_size/nop_bw)*gb_read_time)) )+ max(0,(int(last_mem/noc_bw - last_mem/nop_bw)))
            # if noc_bw > nop_bw:
            #     self.read_gb_clk = int(gb_doublebuffer_size/nop_bw) * gb_read_time + int(last_mem/nop_bw) + self.read_gb_stall_clk
            # else:
            #     self.read_gb_clk = int(gb_doublebuffer_size/noc_bw) * gb_read_time + int(last_mem/noc_bw) + self.read_gb_stall_clk 
            self.read_gb_clk = int(gb_doublebuffer_size/nop_bw) * gb_read_time + int(last_mem/nop_bw) + self.read_gb_stall_clk
        return self.read_gb_stall_clk,self.read_gb_clk

    #output
    def cn_read_local_buffer(self,lb_data_out,bw):
        loacl_buffer_size = self.config.cn_ofmap_sz_kb        
        lb_doublebuffer_size = (loacl_buffer_size*1024)/2
        lb_read_time = math.ceil( lb_data_out / lb_doublebuffer_size) -1 
        last_mem_lb = int(lb_data_out % lb_doublebuffer_size)
        print(lb_read_time)

        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            noc_bw = self.config.cnpu_noc_bw
        else:
            noc_bw = bw

        if lb_read_time==0:
            self.read_lb_stall_clk = max(0,(int(last_mem_lb/bw - last_mem_lb/noc_bw)))
        else:
            self.read_lb_stall_clk =max(0,(int((lb_doublebuffer_size/bw-lb_doublebuffer_size/noc_bw)*lb_read_time))) + max(0,(int(last_mem_lb/bw - last_mem_lb/noc_bw)))

        # if bw > noc_bw:
        #     self.read_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_read_time + last_mem_lb/noc_bw + self.read_lb_stall_clk)
        # else:
        #     self.read_lb_clk = int(lb_doublebuffer_size/bw * lb_read_time + last_mem_lb/bw + self.read_lb_stall_clk)
        self.read_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_read_time + last_mem_lb/noc_bw + self.read_lb_stall_clk)
        return self.read_lb_stall_clk,self.read_lb_clk

    def sa_read_local_buffer(self,lb_data_out,bw):
        loacl_buffer_size = self.config.sa_ofmap_sz_kb        
        lb_doublebuffer_size = (loacl_buffer_size*1024)/2
        lb_read_time = math.ceil( lb_data_out / lb_doublebuffer_size) -1 
        last_mem_lb = int(lb_data_out % lb_doublebuffer_size)
        print(lb_read_time)

        # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            noc_bw = self.config.sapu_noc_bw
        else:
            noc_bw = bw

        if lb_read_time==0:
            self.read_lb_stall_clk = max(0,(int(last_mem_lb/bw - last_mem_lb/noc_bw)))
        else:
            self.read_lb_stall_clk =max(0,(int((lb_doublebuffer_size/bw-lb_doublebuffer_size/noc_bw)*lb_read_time))) + max(0,(int(last_mem_lb/bw - last_mem_lb/noc_bw)))

        # if bw > noc_bw:
        #     self.read_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_read_time + last_mem_lb/noc_bw + self.read_lb_stall_clk)
        # else:
        #     self.read_lb_clk = int(lb_doublebuffer_size/bw * lb_read_time + last_mem_lb/bw + self.read_lb_stall_clk)
        self.read_lb_clk = int(lb_doublebuffer_size/noc_bw * lb_read_time + last_mem_lb/noc_bw + self.read_lb_stall_clk)

        return self.read_lb_stall_clk,self.read_lb_clk

    def print_mem_data(self):
        print("gb_feature_in")
        for element in self.gb_feature_in_list:
            print(element) 
        print("gb_weight_in")   
        for element in self.gb_weight_in_list:
            print(element)
        print("gb_feature_out")
        for element in self.gb_feature_out_list:
            print(element) 

        print("lb_feature_in")
        for element in self.lb_feature_in_list:
            print(element) 
        print("lb_weight_in")   
        for element in self.lb_weight_in_list:
            print(element)
        print("lb_feature_out")
        for element in self.lb_feature_out_list:
            print(element) 

    #最大的不停数据传输带宽
    def cn_bw_write_lb(self,sa_bw):
        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            self.write_lb_bw = self.config.cnpu_noc_bw
        else:
            self.write_lb_bw = sa_bw
        return self.write_lb_bw

    def sa_bw_write_lb(self,sa_bw):
        # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            self.write_lb_bw = self.config.sapu_noc_bw
        else:
            self.write_lb_bw = sa_bw
        return self.write_lb_bw

    def cn_bw_write_gb(self,noc_bw):
        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            self.write_gb_bw = self.config.nop_bw
        else:
            self.write_gb_bw = noc_bw * self.config.cnpu_router_per_global_buffer
        return self.write_gb_bw

    def sa_bw_write_gb(self,noc_bw):
        # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            self.write_gb_bw = self.config.nop_bw
        else:
            self.write_gb_bw = noc_bw * self.config.sapu_router_per_global_buffer
        return self.write_gb_bw

    def cn_bw_read_lb(self,sa_bw):
        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            self.read_lb_bw = self.config.cnpu_noc_bw
        else:
            self.read_lb_bw = sa_bw
        return self.read_lb_bw

    def sa_bw_read_lb(self,sa_bw):
        # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            self.read_lb_bw = self.config.sapu_noc_bw
        else:
            self.read_lb_bw = sa_bw
        return self.read_lb_bw

    def cn_bw_read_gb(self,noc_bw):
        # user_mode =self.config.cn_use_user_bandwidth
        if self.config.cn_use_user_bandwidth :
            self.read_gb_bw = self.config.nop_bw
        else:
            self.read_gb_bw = noc_bw * self.config.cnpu_router_per_global_buffer
        return self.read_gb_bw

    def sa_bw_read_gb(self,noc_bw):
        # user_mode =self.config.sa_use_user_bandwidth
        if self.config.sa_use_user_bandwidth :
            self.read_gb_bw = self.config.nop_bw
        else:
            self.read_gb_bw = noc_bw * self.config.sapu_router_per_global_buffer
        return self.read_gb_bw
    # def cn_bw_read_lb(self,lb_data_out,gb_data_out):
    #     loacl_buffer_size = self.config.cn_ofmap_sz_kb
    #     global_buffer_size = self.config.cnpu_global_buffer_size
    #     lb_doublebuffer_size = (loacl_buffer_size*1024)/2
    #     gb_doublebuffer_size = (global_buffer_size*1024)/3/2

    #     number_router = self.config.cnpu_router_per_global_buffer

    #     lb_read_time = math.ceil( lb_data_out / lb_doublebuffer_size) -1 
    #     gb_read_time = math.ceil( gb_data_out / gb_doublebuffer_size) -1    
    #     last_mem_gb = int(gb_data_out % gb_doublebuffer_size)
    #     last_mem_lb = int(lb_data_out % lb_doublebuffer_size)
        
    #     self.read_lb_bw = round(63/number_router,3)
    #     return self.read_lb_bw

    # def sa_bw_read_lb(self,lb_data_out,gb_data_out):
    #     loacl_buffer_size = self.config.sa_ofmap_sz_kb
    #     global_buffer_size = self.config.sapu_global_buffer_size
    #     lb_doublebuffer_size = (loacl_buffer_size*1024)/2
    #     gb_doublebuffer_size = (global_buffer_size*1024)/3/2

    #     number_router = self.config.sapu_router_per_global_buffer

    #     lb_read_time = math.ceil( lb_data_out / lb_doublebuffer_size) -1 
    #     gb_read_time = math.ceil( gb_data_out / gb_doublebuffer_size) -1  
    #     last_mem_gb = int(gb_data_out % gb_doublebuffer_size)
    #     last_mem_lb = int(lb_data_out % lb_doublebuffer_size)

    #     self.read_lb_bw = round(63/number_router,3)
    #     return self.read_lb_bw