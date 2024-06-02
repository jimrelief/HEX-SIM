import os
import sys
# 将父目录放入系统路径中
sys.path.append("..")

from scalesim.scale_config import scale_config as cfg
from scalesim.topology_utils import topologies as topo
from scalesim.single_layer_sim import single_layer_sim as layer_sim
from mem import mem
from config import config
from topo_gen import topo_gen

class simulator:
    def __init__(self):
        self.mem_gen = mem()
        self.config = config()
        self.topo_gen = topo_gen()

        self.conf = cfg()
        self.topo = topo()

        self.top_path = "./"
        self.verbose = True
        self.save_trace = True

        self.num_layers = 0

        self.single_layer_sim_object_list = []

        self.params_set_flag = False
        self.all_layer_run_done = False

        self.layers_pu_computer_cycle = 0
        self.layers_pu_satll_cycle = 0
        self.layer_sa_utilization = 0

        self.run_clk = 0
        self.stall_clk = 0
        self.topo_run_clk = 0
        self.topo_stall_clk = 0
        self.topo_sa_utilization = 0

        self.bw_write_gb_input = 0
        self.bw_write_gb_filter = 0
        self.bw_write_lb_input =0
        self.bw_write_lb_filter = 0
        self.bw_write_sa_input = 0
        self.bw_write_sa_filter = 0
        self.bw_read_sa = 0
        self.bw_read_lb = 0
        self.bw_read_gb = 0

        self.topo_bw_write_gb_input = 0
        self.topo_bw_write_gb_filter = 0
        self.topo_bw_write_lb_input =0
        self.topo_bw_write_lb_filter = 0
        self.topo_bw_write_sa_input = 0
        self.topo_bw_write_sa_filter = 0
        self.topo_bw_read_sa = 0
        self.topo_bw_read_lb = 0
        self.topo_bw_read_gb = 0

        # self.bw_input = 0
        # self.bw_filter = 0
        self.bw_input_list = []
        self.bw_filter_list = []
        self.bw_output_list = []

    #
    def set_params(self,
                   config_obj=cfg(),
                   topo_obj=topo(),

                   top_topo_pace="",
                   top_conf_pace="",
                   config_type="",

                   top_path="./",
                   verbosity=True,
                   save_trace=True
                   ):

        self.conf = config_obj
        self.topo = topo_obj

        self.top_path = top_path
        self.verbose = verbosity
        self.save_trace = save_trace

        self.top_topo_pace = top_topo_pace
        self.top_conf_pace = top_conf_pace
        self.config_type = config_type

       
        # Calculate inferrable parameters here
        self.num_layers = self.topo.get_num_layers()

        self.params_set_flag = True

    #
    def run(self):
        assert self.params_set_flag, 'Simulator parameters are not set'

        #生成gb、lb数据
        self.mem_gen.mem_data_gen(self.top_conf_pace,self.top_topo_pace,self.config_type)
        self.topo_sa_utilization = 0
        # 1. Create the layer runners for each layer
        for i in range(self.num_layers):
            this_layer_sim = layer_sim()
            this_layer_sim.set_params(layer_id=i,
                                 config_obj=self.conf,
                                 topology_obj=self.topo,
                                 verbose=self.verbose)

            self.single_layer_sim_object_list.append(this_layer_sim)

        if not os.path.isdir(self.top_path):
            cmd = 'mkdir ' + self.top_path
            os.system(cmd)

        report_path = self.top_path + '/' + self.conf.get_run_name()

        if not os.path.isdir(report_path):
            cmd = 'mkdir ' + report_path
            os.system(cmd)

        self.top_path = report_path

        self.topo_run_clk = 0
        self.topo_stall_clk = 0

        self.topo_bw_write_gb_input = 0
        self.topo_bw_write_gb_filter = 0
        self.topo_bw_write_lb_input =0
        self.topo_bw_write_lb_filter = 0
        self.topo_bw_write_sa_input = 0
        self.topo_bw_write_sa_filter = 0
        self.topo_bw_read_sa = 0
        self.topo_bw_read_lb = 0
        self.topo_bw_read_gb = 0
        # 2. Run each layer
        # TODO: This is parallelizable
        for single_layer_obj in self.single_layer_sim_object_list:

            if self.verbose:
                layer_id = single_layer_obj.get_layer_id()
                print('\nRunning Layer ' + str(layer_id))

            single_layer_obj.run()
            
            if self.verbose:
                comp_items = single_layer_obj.get_compute_report_items()
                comp_cycles = comp_items[0]
                stall_cycles = comp_items[1]
                util = comp_items[2]
                mapping_eff = comp_items[3]
                # print('PU Compute cycles: ' + str(comp_cycles))
                # print('PU Stall cycles: ' + str(stall_cycles))
                self.layers_pu_computer_cycle = comp_cycles
                self.layers_pu_stall_cycle = stall_cycles
                self.layer_sa_utilization = mapping_eff

                # print('Overall utilization: ' + "{:.2f}".format(util) +'%')
                # print('Mapping efficiency: ' + "{:.2f}".format(mapping_eff) +'%')

                avg_bw_items = single_layer_obj.get_bandwidth_report_items()
                avg_ifmap_bw = avg_bw_items[3]
                avg_filter_bw = avg_bw_items[4]
                avg_ofmap_bw = avg_bw_items[5]
                # print('Average IFMAP DRAM BW: ' + "{:.3f}".format(avg_ifmap_bw) + ' words/cycle')
                # print('Average Filter DRAM BW: ' + "{:.3f}".format(avg_filter_bw) + ' words/cycle')
                # print('Average OFMAP DRAM BW: ' + "{:.3f}".format(avg_ofmap_bw) + ' words/cycle')

                #gb、lb仿真
                bw_input = round(avg_ifmap_bw,3)*4
                bw_filter = round(avg_filter_bw,3)*4
                bw_output = round(avg_ofmap_bw,3)*4

                self.bw_input_list.append(bw_input)
                self.bw_filter_list.append(bw_filter)
                self.bw_output_list.append(bw_output) 
                #分层mem仿真
                self.layer_mem_sim(layer_id)

                #累加run clk 和stall clk和utization
                self.topo_run_clk = self.topo_run_clk + self.run_clk
                self.topo_stall_clk = self.topo_stall_clk + self.stall_clk
                self.topo_sa_utilization = self.topo_sa_utilization + self.layer_sa_utilization
                #计算平均带宽
                self.topo_bw_write_gb_input = self.topo_bw_write_gb_input + self.bw_write_gb_input
                self.topo_bw_write_gb_filter = self.topo_bw_write_gb_filter + self.bw_write_gb_filter
                self.topo_bw_write_lb_input = self.topo_bw_write_lb_input + self.bw_write_lb_input
                self.topo_bw_write_lb_filter = self.topo_bw_write_lb_filter + self.bw_write_lb_filter
                self.topo_bw_write_sa_input = self.topo_bw_write_sa_input + self.bw_write_sa_input
                self.topo_bw_write_sa_filter = self.topo_bw_write_sa_filter + self.bw_write_sa_filter
                self.topo_bw_read_sa = self.topo_bw_read_sa + self.bw_read_sa
                self.topo_bw_read_lb = self.topo_bw_read_lb + self.bw_read_lb
                self.topo_bw_read_gb = self.topo_bw_read_gb + self.bw_read_gb

            if self.save_trace:
                if self.verbose:
                    print('Saving traces: ', end='')
                single_layer_obj.save_traces(self.top_path)
                if self.verbose:
                    print('Done!')

        self.all_layer_run_done = True

        sa_utilization = self.topo_sa_utilization / self.num_layers
        avg_bw_write_gb_input = round(self.topo_bw_write_gb_input / self.num_layers,3)
        avg_bw_write_gb_filter = round(self.topo_bw_write_gb_filter / self.num_layers,3)
        avg_bw_write_lb_input = round(self.topo_bw_write_lb_input / self.num_layers,3)
        avg_bw_write_lb_filter = round(self.topo_bw_write_lb_filter / self.num_layers,3)
        avg_bw_write_sa_input = round(self.topo_bw_write_sa_input / self.num_layers,3)
        avg_bw_write_sa_filter = round(self.topo_bw_write_sa_filter / self.num_layers,3)
        avg_bw_read_sa = round(self.topo_bw_read_sa / self.num_layers,3)
        avg_bw_read_lb = round(self.topo_bw_read_lb / self.num_layers,3)
        avg_bw_read_gb = round(self.topo_bw_read_gb / self.num_layers,3)
        ###################################################################
        print("=========================================================")
        print("Calculation Completed!!!")
        print('Overall SA utilization: ' + "{:.2f}".format(sa_utilization) +'%')
        print("ALL RUN CLK:",self.topo_run_clk)
        print("ALL STALL CLK:",self.topo_stall_clk)

        print("Avg Write gb bw(input):",avg_bw_write_gb_input,"bytes/cycle","Avg Write gb bw(filter):",avg_bw_write_gb_filter,"bytes/cycle")
        print("Avg Write lb bw(input):",avg_bw_write_lb_input,"bytes/cycle","Avg Write lb bw(filter):",avg_bw_write_lb_filter,"bytes/cycle")
        print("Avg Write sa bw(input):",avg_bw_write_sa_input,"bytes/cycle","Avg Write sa bw(filter):",avg_bw_write_sa_filter,"bytes/cycle")
        print("Avg Read sa bw:",avg_bw_read_sa,"bytes/cycle")
        print("Avg Read lb bw:",avg_bw_read_lb,"bytes/cycle")
        print("Avg Read gb bw:",avg_bw_read_gb,"bytes/cycle")
        print("=========================================================")
        self.generate_reports()

    #
    def generate_reports(self):
        assert self.all_layer_run_done, 'Layer runs are not done yet'

        compute_report_name = self.top_path + '/COMPUTE_REPORT.csv'
        compute_report = open(compute_report_name, 'w')
        header = 'LayerID, Total Cycles, Stall Cycles, Overall Util %, Mapping Efficiency %, Compute Util %,\n'
        compute_report.write(header)

        bandwidth_report_name = self.top_path + '/BANDWIDTH_REPORT.csv'
        bandwidth_report = open(bandwidth_report_name, 'w')
        header = 'LayerID, Avg IFMAP SRAM BW, Avg FILTER SRAM BW, Avg OFMAP SRAM BW, '
        header += 'Avg IFMAP DRAM BW, Avg FILTER DRAM BW, Avg OFMAP DRAM BW,\n'
        bandwidth_report.write(header)

        detail_report_name = self.top_path + '/DETAILED_ACCESS_REPORT.csv'
        detail_report = open(detail_report_name, 'w')
        header = 'LayerID, '
        header += 'SRAM IFMAP Start Cycle, SRAM IFMAP Stop Cycle, SRAM IFMAP Reads, '
        header += 'SRAM Filter Start Cycle, SRAM Filter Stop Cycle, SRAM Filter Reads, '
        header += 'SRAM OFMAP Start Cycle, SRAM OFMAP Stop Cycle, SRAM OFMAP Writes, '
        header += 'DRAM IFMAP Start Cycle, DRAM IFMAP Stop Cycle, DRAM IFMAP Reads, '
        header += 'DRAM Filter Start Cycle, DRAM Filter Stop Cycle, DRAM Filter Reads, '
        header += 'DRAM OFMAP Start Cycle, DRAM OFMAP Stop Cycle, DRAM OFMAP Writes,\n'
        detail_report.write(header)

        for lid in range(len(self.single_layer_sim_object_list)):
            single_layer_obj = self.single_layer_sim_object_list[lid]
            compute_report_items_this_layer = single_layer_obj.get_compute_report_items()
            log = str(lid) +', '
            log += ', '.join([str(x) for x in compute_report_items_this_layer])
            log += ',\n'
            compute_report.write(log)

            bandwidth_report_items_this_layer = single_layer_obj.get_bandwidth_report_items()
            log = str(lid) + ', '
            log += ', '.join([str(x) for x in bandwidth_report_items_this_layer])
            log += ',\n'
            bandwidth_report.write(log)

            detail_report_items_this_layer = single_layer_obj.get_detail_report_items()
            log = str(lid) + ', '
            log += ', '.join([str(x) for x in detail_report_items_this_layer])
            log += ',\n'
            detail_report.write(log)

        compute_report.close()
        bandwidth_report.close()
        detail_report.close()

    #
    def get_total_cycles(self):
        assert self.all_layer_run_done, 'Layer runs are not done yet'

        total_cycles = 0
        for layer_obj in self.single_layer_sim_object_list:
            cycles_this_layer = int(layer_obj.get_compute_report_items[0])
            total_cycles += cycles_this_layer

        return total_cycles

    def layer_mem_sim(self,i):
        if self.config_type == "encoding":

                bw_input_write_lb=self.mem_gen.cn_bw_write_lb(self.bw_input_list[i])
                bw_filter_write_lb=self.mem_gen.cn_bw_write_lb(self.bw_filter_list[i])
                bw_read_lb=self.mem_gen.cn_bw_read_lb(self.bw_output_list[i])

                bw_input_write_gb=self.mem_gen.cn_bw_write_gb(bw_input_write_lb)                                                   
                bw_filter_write_gb=self.mem_gen.cn_bw_write_gb(bw_filter_write_lb)                                 
                bw_read_gb=self.mem_gen.cn_bw_read_gb(bw_read_lb)
                                                    
                ############################################################################
                lb_input_stall_clk, lb_input_clk=self.mem_gen.cn_write_local_buffer(
                                                   self.mem_gen.lb_feature_in_list[i],
                                                   "input",
                                                   self.bw_input_list[i])
                lb_filter_stall_clk, lb_filter_clk=self.mem_gen.cn_write_local_buffer(
                                                   self.mem_gen.lb_weight_in_list[i],
                                                   "filter",
                                                   self.bw_filter_list[i])

                write_lb_stall_clk = lb_input_stall_clk + lb_filter_stall_clk
                write_lb_clk = lb_input_clk + lb_filter_clk

                read_lb_stall_clk,read_lb_clk=self.mem_gen.cn_read_local_buffer(
                                                   self.mem_gen.lb_feature_out_list[i],                                                 
                                                   self.bw_output_list[i])    
                ############################################################################
                # print(write_lb_clk)
                gb_input_stall_clk,gb_input_clk=self.mem_gen.cn_write_global_buffer(
                                                    self.mem_gen.gb_feature_in_list[i],
                                                    bw_input_write_lb,
                                                    bw_input_write_gb
                                                    )
                # print(gb_input_stall_clk,gb_input_clk)
                gb_filter_stall_clk,gb_filter_clk=self.mem_gen.cn_write_global_buffer(
                                                    self.mem_gen.gb_weight_in_list[i],
                                                    bw_filter_write_lb,
                                                    bw_filter_write_gb
                                                    )

                # print(gb_filter_stall_clk,gb_filter_clk)
                write_gb_stall_clk = gb_input_stall_clk + gb_filter_stall_clk
                write_gb_clk = gb_input_clk + gb_filter_clk

                read_gb_stall_clk,read_gb_clk = self.mem_gen.cn_read_global_buffer(
                                                    self.mem_gen.gb_feature_out_list[i],
                                                    bw_read_lb,
                                                    bw_read_gb
                                                    )
                ############################################################################
                self.stall_clk = self.layers_pu_stall_cycle + write_lb_stall_clk + read_lb_stall_clk + write_gb_stall_clk + read_gb_stall_clk
                self.run_clk = self.layers_pu_computer_cycle + write_lb_clk + read_lb_clk + write_gb_clk + read_gb_clk

                self.bw_write_gb_input = bw_input_write_gb
                self.bw_write_gb_filter = bw_filter_write_gb
                self.bw_write_lb_input = bw_input_write_lb
                self.bw_write_lb_filter = bw_filter_write_lb
                self.bw_write_sa_input = self.bw_input_list[i]
                self.bw_write_sa_filter = self.bw_filter_list[i]
                self.bw_read_sa = self.bw_output_list[i]
                self.bw_read_lb = bw_read_lb
                self.bw_read_gb = bw_read_gb

                ############################################################################
                print("Layer Parameters",i)
                print("====================CLK====================")
                print("Layer SA Utilization","{:.2f}".format(self.layer_sa_utilization) +'%' )
                print("Write gb stall clk:",write_gb_stall_clk,"Write gb clk:",write_gb_clk)
                print("Write lb stall clk:",write_lb_stall_clk,"Write lb clk:",write_lb_clk)
                print("PU stall clk:",self.layers_pu_stall_cycle,"PU computer clk:",self.layers_pu_computer_cycle)
                print("Read lb stall clk:",read_lb_stall_clk,"Read lb clk:",read_lb_clk)
                print("Read gb stall clk:",read_gb_stall_clk,"Read gb clk:",read_gb_clk)

                print("Stall clk:",self.stall_clk,"Run clk:",self.run_clk)
                print("====================BW====================")
                print("Write gb bw(input):",round(bw_input_write_gb,3),"bytes/cycle","Write gb bw(filter):",round(bw_filter_write_gb,3),"bytes/cycle")
                print("Write lb bw(input):",bw_input_write_lb,"bytes/cycle","Write lb bw(filter):",bw_filter_write_lb,"bytes/cycle")
                print("Write sa bw(input):",self.bw_input_list[i],"bytes/cycle","Write sa bw(filter):",self.bw_filter_list[i],"bytes/cycle")
                print("Read sa bw:",self.bw_output_list[i],"bytes/cycle")
                print("Read lb bw:",bw_read_lb,"bytes/cycle")
                print("Read gb bw:",round(bw_read_gb,3),"bytes/cycle")
               

        if self.config_type == "decoding":

                bw_input_write_lb=self.mem_gen.sa_bw_write_lb(self.bw_input_list[i])
                bw_filter_write_lb=self.mem_gen.sa_bw_write_lb(self.bw_filter_list[i])
                bw_read_lb=self.mem_gen.sa_bw_read_lb(self.bw_output_list[i])

                bw_input_write_gb=self.mem_gen.sa_bw_write_gb(bw_input_write_lb)                                                   
                bw_filter_write_gb=self.mem_gen.sa_bw_write_gb(bw_filter_write_lb)                                 
                bw_read_gb=self.mem_gen.sa_bw_read_gb(bw_read_lb)
                ############################################################################ 
               
                lb_input_stall_clk, lb_input_clk=self.mem_gen.sa_write_local_buffer(
                                                   self.mem_gen.lb_feature_in_list[i],
                                                   "input",
                                                   self.bw_input_list[i])
                lb_filter_stall_clk, lb_filter_clk=self.mem_gen.sa_write_local_buffer(
                                                   self.mem_gen.lb_weight_in_list[i],
                                                   "filter",
                                                   self.bw_filter_list[i])

                write_lb_stall_clk = lb_input_stall_clk + lb_filter_stall_clk
                write_lb_clk = lb_input_clk + lb_filter_clk

                read_lb_stall_clk,read_lb_clk=self.mem_gen.sa_read_local_buffer(
                                                   self.mem_gen.lb_feature_out_list[i],                                                 
                                                   self.bw_output_list[i])    
                ############################################################################
                # print(write_lb_clk)
                gb_input_stall_clk,gb_input_clk=self.mem_gen.sa_write_global_buffer(
                                                    self.mem_gen.gb_feature_in_list[i],
                                                    bw_input_write_lb,
                                                    bw_input_write_gb
                                                    )
                # print(gb_input_stall_clk,gb_input_clk)
                gb_filter_stall_clk,gb_filter_clk=self.mem_gen.sa_write_global_buffer(
                                                    self.mem_gen.gb_weight_in_list[i],
                                                    bw_filter_write_lb,
                                                    bw_filter_write_gb
                                                    )

                # print(gb_filter_stall_clk,gb_filter_clk)
                write_gb_stall_clk = gb_input_stall_clk + gb_filter_stall_clk
                write_gb_clk = gb_input_clk + gb_filter_clk

                read_gb_stall_clk,read_gb_clk = self.mem_gen.sa_read_global_buffer(
                                                    self.mem_gen.gb_feature_out_list[i],
                                                    bw_read_lb,
                                                    bw_read_gb
                                                    )

                ############################################################################
                self.stall_clk = self.layers_pu_stall_cycle + write_lb_stall_clk + read_lb_stall_clk + write_gb_stall_clk + read_gb_stall_clk
                
                self.run_clk = self.layers_pu_computer_cycle + write_lb_clk + read_lb_clk + write_gb_clk + read_gb_clk

                self.bw_write_gb_input = bw_input_write_gb
                self.bw_write_gb_filter = bw_filter_write_gb
                self.bw_write_lb_input = bw_input_write_lb
                self.bw_write_lb_filter = bw_filter_write_lb
                self.bw_write_sa_input = self.bw_input_list[i]
                self.bw_write_sa_filter = self.bw_filter_list[i]
                self.bw_read_sa = self.bw_output_list[i]
                self.bw_read_lb = bw_read_lb
                self.bw_read_gb = bw_read_gb
                ############################################################################
                print("Layer Parameters",i)
                print("====================CLK====================")
                print("Layer SA Utilization","{:.2f}".format(self.layer_sa_utilization) +'%' )
                print("Write gb stall clk:",write_gb_stall_clk,"Write gb clk:",write_gb_clk)
                print("Write lb stall clk:",write_lb_stall_clk,"Write lb clk:",write_lb_clk)
                print("PU stall clk:",self.layers_pu_stall_cycle,"PU computer clk:",self.layers_pu_computer_cycle)
                print("Read lb stall clk:",read_lb_stall_clk,"Read lb clk:",read_lb_clk)
                print("Read gb stall clk:",read_gb_stall_clk,"Read gb clk:",read_gb_clk)

                print("Stall clk:",self.stall_clk,"Run clk:",self.run_clk)
                print("====================BW====================")
                print("Write gb bw(input):",round(bw_input_write_gb,3),"bytes/cycle","Write gb bw(filter):",round(bw_filter_write_gb,3),"bytes/cycle")
                print("Write lb bw(input):",bw_input_write_lb,"bytes/cycle","Write lb bw(filter):",bw_filter_write_lb,"bytes/cycle")
                print("Write sa bw(input):",self.bw_input_list[i],"bytes/cycle","Write sa bw(filter):",self.bw_filter_list[i],"bytes/cycle")
                print("Read sa bw:",self.bw_output_list[i],"bytes/cycle")
                print("Read lb bw:",bw_read_lb,"bytes/cycle")
                print("Read gb bw:",round(bw_read_gb,3),"bytes/cycle")