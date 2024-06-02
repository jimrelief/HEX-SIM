import argparse
from config import config
from topology import topologies
from topo_gen import topo_gen
from scalesim.scale_sim import scalesim
from mem import mem
#保留运行文件地址文件夹
top = "./test"
#总的上层config
#col
top_conf_pace = "../configs/test_col.cfg"
#row
# top_conf_pace = "../configs/test_row.cfg"
# 上层的topo rt1
top_cnpu_topo_path = "../topologies/topo_rt1/rt1_efficientnet.csv "
top_sapu_topo_path = "../topologies/topo_rt1/rt1_decoder.csv "
#上层的topo rf1
# top_cnpu_topo_path = "../topologies/topo_rf/rf_vit_l14.csv "
# top_sapu_topo_path = "../topologies/topo_rf/rf_gpt2.csv "
#上层的topo gr1
# top_cnpu_topo_path = "../topologies/topo_gr1/gr1_vit_b16.csv "
# top_sapu_topo_path = "../topologies/topo_gr1/gr1_gpt2.csv "

#拆分后的cnpu、sapu config
cnpu_conf_pace = "../configs/cnpu.cfg"
sapu_conf_pace = "../configs/sapu.cfg"

#处理后的topo
cnpu_topo_pace = "../topologies/cnpu.csv "
sapu_topo_pace = "../topologies/sapu.csv "

#config
conf = config()
conf.read_mobius_config(top_conf_pace)
conf.print_mobius_config()
#生成对应pu的配置信息
conf.write_cnpu_conf(cnpu_conf_pace)
conf.write_sapu_conf(sapu_conf_pace)

#topo
topo_gen = topo_gen()

#进行pu级别仿真
#生成分割后的topo
topo_gen.pu_topo_gen(top_conf_pace,top_cnpu_topo_path,cnpu_topo_pace,"conv","encoding")
print("===================ENCODING SIMULATION BEGIN===================")
cnpu_scale = scalesim(save_disk_space=True, verbose=True,
             config=cnpu_conf_pace,
             topology=cnpu_topo_pace
             )
cnpu_scale.run_scale(top_path=top,
			top_topo_pace=top_cnpu_topo_path,
			top_conf_pace=top_conf_pace,
			config_type="encoding"
			)
print("=================== ENCODING SIMULATION END ===================")

Global_Buffer_Size = conf.cnpu_global_buffer_size
PU_Number = (conf.cnpu_router_per_global_buffer+ 1) * conf.cnpu_number_of_layer

# chiplet_utization = topo_gen.get_chiplet_utization()
print("PARALLELISM:",conf.parallelism)
print('Average Chiplet utilization: ' + "{:.2f}".format(topo_gen.chiplet_utization) +'%')
print('Average PU utilization: ' + "{:.2f}".format(topo_gen.pu_utization) +'%')

print("CONV Chiplet Number:",conf.conv_number_of_chiplet)
print("SA Chiplet Number:",conf.sa_number_of_chiplet)
print("CNPU Number Per Chiplet:",PU_Number)
print("Global Buffer Size:",Global_Buffer_Size,"kB")
      	

#生成分割后的topo
topo_gen.pu_topo_gen(top_conf_pace,top_sapu_topo_path,sapu_topo_pace,"sa","decoding")
print("===================DECODING SIMULATION BEGIN===================")
sapu_scale = scalesim(save_disk_space=True, verbose=True,
             config=sapu_conf_pace,
             topology=sapu_topo_pace
             )
sapu_scale.run_scale(top_path=top,
			top_topo_pace=top_sapu_topo_path,
			top_conf_pace=top_conf_pace,
			config_type="decoding"
			)
print("=================== DECODING SIMULATION END ===================")

Global_Buffer_Size = conf.sapu_global_buffer_size
PU_Number = (conf.sapu_router_per_global_buffer+ 1) * conf.sapu_number_of_layer

# chiplet_utization = topo_gen.get_chiplet_utization()
print("PARALLELISM:",conf.parallelism)
print('Average Chiplet utilization: ' + "{:.2f}".format(topo_gen.chiplet_utization) +'%')
print('Average PU utilization: ' + "{:.2f}".format(topo_gen.pu_utization) +'%')

print("CONV Chiplet Number:",conf.conv_number_of_chiplet)
print("SA Chiplet Number:",conf.sa_number_of_chiplet)
print("SAPU Number Per Chiplet:",PU_Number)
print("Global Buffer Size:",Global_Buffer_Size,"kB")


