import argparse

from scalesim.scale_sim import scalesim

config = "configs/scale.cfg"
# config = "configs/scale_is.cfg"
# config = "./configs/tpu_ws_test1.cfg"
# topo = "./topologies/transformer/transformer_fwd.csv"
topo = "./topologies/transformer/vit_decoder.csv"
top = "./test"

s = scalesim(save_disk_space=True, verbose=True,
             config=config,
             topology=topo
             )
s.run_scale(top_path=top)
