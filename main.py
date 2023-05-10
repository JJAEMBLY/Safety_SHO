import pandapower as pp
import pandapower.networks as pn
from Code_for_SWO_copy import action_modifier

net_simple_open_ring = pn.simple_mv_open_ring_net()
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(1)
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(3)
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(5)
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(7)
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(9)
net_simple_open_ring.switch = net_simple_open_ring.switch.drop(11)

net_simple_open_ring.switch = net_simple_open_ring.switch.reset_index(drop=True)


pp.create_line(net_simple_open_ring, 2,5, length_km= 1.0, std_type="NA2XS2Y 1x185 RM/25 12/20 kV", name="line 6")
#print(net_simple_open_ring.line)

#print(net_simple_open_ring.bus)
#print(net_simple_open_ring.switch)
Graph = action_modifier(net_simple_open_ring)

modified_action = Graph.Output_Modify([0.9, 0.8, 0.7, 0.6, 0.5, 1])

#print(modified_action)

#Graph.print_information()