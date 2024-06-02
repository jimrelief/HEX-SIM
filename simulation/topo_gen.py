from topology import topologies
from config import config
import os
import sys

class topo_gen:
    def __init__(self):
        self.chiplet_utization = 0
        self.pu_utization = 0

    def pu_topo_gen(self,top_conf_pace,topo_pace_in,topo_pace_out,topo_type,config_type):
        conf = config()
        conf.read_mobius_config(top_conf_pace)
        if config_type == "encoding":
            number_pu = conf.cnpu_number_of_layer * (conf.cnpu_router_per_global_buffer + 1)
        elif config_type == "decoding":
            number_pu = conf.sapu_number_of_layer * (conf.sapu_router_per_global_buffer + 1)
        else :
            print("ERROR TOPO TYPE")

        topo = topologies()
        topo.load_arrays_conv(topo_pace_in)
        layer_number = topo.get_num_layers()

        all_chiplet_utization = 0
        all_pu_utization = 0

        for i in range(layer_number):
            layer_name = topo.get_layer_name(i)
            mac_number = topo.get_layer_num_operation(i)
            ifmap_rows, ifmap_cols = topo.get_layer_ifmap_dims(i)
            filter_rows, filter_cols = topo.get_layer_filter_dims(i)
            num_input_channels = topo.get_layer_num_channels(i)
            num_filters = topo.get_layer_num_filters(i)
            # filter_data =  filter_rows * filter_cols * num_input_channels
            # row_stride, col_stride = topo.get_layer_strides(i)
            print("==========================================================")
            print("Layer Number = \t",i)
            print("Layer Name = \t",layer_name)
            print("=================")
            # print(number) 
            # print(ifmap_rows,ifmap_cols) 
            # print(filter_rows,filter_cols) 
            # print(num_input_channels) 
            # print(num_filters) 
            # print(row_stride,col_stride) 

            # print(topo.topo_arrays[0][6])
            # topo.topo_arrays[0][6] = 1
            # print(topo.topo_arrays[0][6])

            #权重矩阵按列分割
    
            if conf.parallelism == "COL":
                #先分割到chiplet一层
                if num_filters >= conf.conv_number_of_chiplet :
                    chip_filters_seg = conf.conv_number_of_chiplet
                else:
                    chip_filters_seg = num_filters
                chip_filters = int(num_filters/chip_filters_seg)
                print("chip_filters_seg = \t",chip_filters_seg)
                print("chip_filters = \t",chip_filters)
            
                #再分割到pu一层
                if chip_filters >= number_pu :
                    pu_filters_seg = number_pu
                else:
                    pu_filters_seg = chip_filters
                pu_filters = int(chip_filters/pu_filters_seg)
                print("pu_filters_seg = \t",pu_filters_seg)
                print("pu_filters = \t",pu_filters)
                #生成分割后的topo
                topo.topo_arrays[i][6] = pu_filters

                layer_chiplet_utization = (num_filters/conf.conv_number_of_chiplet)*100
                layer_pu_utization = (chip_filters/number_pu)*100

                if layer_chiplet_utization > 100:
                    layer_chiplet_utization = 100
                if layer_pu_utization > 100:
                    layer_pu_utization = 100

            #权重矩阵按行分割   
            if conf.parallelism == "ROW":
                if topo_type == "conv":                
                    #计算修正通道数 全部变成gemm的形式
                    # channels = filter_rows * filter_cols * num_input_channels
                    correction_channels = filter_rows * filter_cols * num_input_channels

                    # #先分割到chiplet一层
                    if correction_channels >= conf.conv_number_of_chiplet :
                        chip_channels_seg = conf.conv_number_of_chiplet
                    else:
                        chip_channels_seg = correction_channels
                    chip_channels = int(correction_channels/chip_channels_seg)
                    print("chip_channels_seg = \t",chip_channels_seg)
                    print("chip_channels = \t",chip_channels)
                
                    # #再分割到pu一层
                    if chip_channels >= number_pu :
                        pu_channels_seg = number_pu
                    else:
                        pu_channels_seg = chip_channels
                    pu_channels = int(chip_channels/pu_channels_seg)
                    print("pu_channels_seg = \t",pu_channels_seg)
                    print("pu_channels = \t",pu_channels)
                    #生成行分割后的topo gemm表示
                    #将卷积核修正为1*1，通道数修正为计算得出的channels
                    topo.topo_arrays[i][1] = mac_number
                    topo.topo_arrays[i][2] = pu_channels
                    topo.topo_arrays[i][3] = 1
                    topo.topo_arrays[i][4] = pu_channels
                    topo.topo_arrays[i][5] = 1
                    topo.topo_arrays[i][6] = num_filters
                    topo.topo_arrays[i][7] = 1
                    topo.topo_arrays[i][8] = 1

                    layer_chiplet_utization = (correction_channels/conf.conv_number_of_chiplet)*100
                    layer_pu_utization = (chip_channels/number_pu)*100

                    if layer_chiplet_utization > 100:
                        layer_chiplet_utization = 100
                    if layer_pu_utization > 100:
                        layer_pu_utization = 100

                if topo_type == "sa":
                    # Entries: layer name, Ifmap h, ifmap w, filter h, filter w, num_ch, num_filt, stride h, stride w
                    #entries = [layer_name, m, k, 1, k, 1, n, 1, 1]
                    #先分割到chiplet一层
                    if ifmap_cols >= conf.conv_number_of_chiplet :
                        chip_channels_seg = conf.conv_number_of_chiplet
                    else:
                        chip_channels_seg = ifmap_cols
                    chip_channels = int(ifmap_cols/chip_channels_seg)
                    print("chip_channels_seg = \t",chip_channels_seg)
                    print("chip_channels = \t",chip_channels)
                
                    #再分割到pu一层
                    if chip_channels >= number_pu :
                        pu_channels_seg = number_pu
                    else:
                        pu_channels_seg = chip_channels
                    pu_channels = int(chip_channels/pu_channels_seg)
                    print("pu_channels_seg = \t",pu_channels_seg)
                    print("pu_channels = \t",pu_channels)
                    #生成行分割后的topo
                    #修改k的值
                    topo.topo_arrays[i][2] = pu_channels
                    topo.topo_arrays[i][4] = pu_channels

                    layer_chiplet_utization = (ifmap_cols/conf.conv_number_of_chiplet)*100
                    layer_pu_utization = (chip_channels/number_pu)*100

                    if layer_chiplet_utization > 100:
                        layer_chiplet_utization = 100
                    if layer_pu_utization > 100:
                        layer_pu_utization = 100

            print("chiplet_utization: \t","{:.2f}".format(layer_chiplet_utization) +'%')
            print("pu_utization: = \t","{:.2f}".format(layer_pu_utization) +'%')


            all_chiplet_utization = all_chiplet_utization + layer_chiplet_utization
            all_pu_utization = all_pu_utization + layer_pu_utization

            print("==========================================================")
            topo.write_topo_file(topo_pace_out)

        self.chiplet_utization = all_chiplet_utization/layer_number
        self.pu_utization = all_pu_utization/layer_number

        # print(all_chiplet_utization,self.chiplet_utization)


    def get_chiplet_utization(self):
        return self.chiplet_utization

    