import pandapower as pp
import networkx as nx
import pandas as pd

class action_modifier:
    def __init__(self, net):
        # network 정보용 변수
        self.net_information = net
        #print(self.net_information.line)

        self.switch_number = len(net.switch)
        #모든 network switch 닫기
        net.switch.closed = True

        self.networkx_net = nx.Graph(pp.topology.create_nxgraph(net))
        #print(self.networkx_net.nodes)
        #print(self.networkx_net.edges)
        #self.loops = list(nx.algorithms.cycles.simple_cycles(self.networkx_net))
        self.loop_component = nx.minimum_cycle_basis(self.networkx_net)
        #Search branch Component of cycles
        self.branch_component = list()
        for k in range(len(self.loop_component)):
            self.branch_list_of_each_cycle = list()
            for i in range(len(net.line)):
                if (net.line.from_bus.iloc[i] in self.loop_component[k]) and (net.line.to_bus.iloc[i] in self.loop_component[k]):
                    self.branch_list_of_each_cycle.append(i)
                    #print(self.branch_list_of_each_cycle)
                else:
                    continue
            self.branch_component.append(self.branch_list_of_each_cycle)
        
        self.branch_component_save = self.branch_component.copy()
    
    def merge_cycle_componenet(self, main_list, target_switch):
        self.lists_to_merge = list()
        self.initial_main_list = main_list.copy()
        print("compnents : ", self.initial_main_list)

        for sub_list in main_list:
            if target_switch in sub_list:
                #print(sub_list)
                self.lists_to_merge.append(sub_list)
                #print(self.lists_to_merge)
                if len(self.lists_to_merge) == 2:
                    break
        
        #print(self.lists_to_merge)

        if len(self.lists_to_merge)<2:
            return self.initial_main_list
        
        merged_list = []
        for item in set(self.lists_to_merge[0] + self.lists_to_merge[1]):
            break_sign = False
            if self.lists_to_merge[0].count(item) == 1 and self.lists_to_merge[1].count(item) == 1:
                continue
            else:
                merged_list.append(item)

        main_list.remove(self.lists_to_merge[0])
        main_list.remove(self.lists_to_merge[1])

        if not merged_list:
            return self.initial_main_list
        else:
            pass

        return main_list
    
    def remove_sublist(self, main_list, sublist_to_remove):
        if sublist_to_remove in main_list:
            return [sublist for sublist in main_list if sublist != sublist_to_remove]
        else:
            return
    
    def Output_Modify(self, action_list):
        assert len(action_list) == self.switch_number, f"(action_modifer) Action number {len(action_list)} != switch number {self.switch_number}"

        # action에 index 부여를 위해 DataFrame으로 변환 후 ordering
        self.action_data = pd.DataFrame(action_list,columns=['value'])
        self.action_data['switch_line_element'] = self.net_information.switch.element
        self.action_data_ordering = self.action_data.sort_values(by=['value'], ascending=False)
        #print(self.action_data_ordering)
        # 각 Cycle마다의 index 부여를 위해 따로 list 생성
        #self.cycle_number = len(self.branch_component_save)
        #self.cycle_index = list(range(len(self.branch_component_save)))
        #print(self.cycle_index)
        # 함수 출력을 위한 empty list
        self.result_action = [1 for i in range(self.switch_number)]
        #print("cycle_index :", self.cycle_index)

        for j in range(len(self.action_data_ordering)):
            print("switch_element :", self.action_data_ordering['switch_line_element'].iloc[j])
            for cycle_components in self.branch_component_save:
                print("component_list : ", cycle_components)
                self.double_break = False
                # 해당 switch가 loop에 포함되는 상황을 찾으면 
                if self.action_data_ordering['switch_line_element'].iloc[j] in cycle_components:

                    #print(self.branch_component_save)
                    self.branch_component_save = self.merge_cycle_componenet(self.branch_component_save, self.action_data_ordering['switch_line_element'].iloc[j])
       
                    self.branch_component_save = self.remove_sublist(self.branch_component_save, cycle_components)
                    self.result_action[self.action_data_ordering.index[j]] = 0
                    print("result : ", self.result_action)
                    # 더이상 해당 cycle을 방문하지 않기위해 cylce index를 제거하고, 모든 해당 branch를 삭제
                    #self.cycle_index.remove(k)
                    self.double_break = True
                    break

                else:
                    #self.result_action.append(1)
                    #print("result : ", self.result_action)
                    continue
            
            if self.double_break == True:
                continue

            #self.result_action.append(1)
            print("result : ", self.result_action)

        #k번째 branch_component에서 index 즉, 해당 branch 삭제
        #print(self.result_action)
        # 차례대로 loop component에 비교해서 숫자를 없애가면 됨 component list에도 indexing을 해서 하나 없애면 그 cycle은 뺄 수 있도록 만들어야 함..
        print("result : ", self.result_action)
        return self.result_action #binary list
        
    def print_information(self):
        print("switch_number : "+str(self.switch_number))
        print("line_component_of_each_cycle : ", self.branch_component)
        
        
        
if __name__ == "__main__":
    import pandapower as pp
    import pandapower.networks as pn
    
    #network information: https://pandapower.readthedocs.io/en/stable/networks/test.html
    net_simple_open_ring = pn.simple_mv_open_ring_net()
    print(net_simple_open_ring.switch)
    # line 각 끝에 2개씩 물려있는 스위치 중 1개씩 드랍
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(1)
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(3)
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(5)
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(7)
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(9)
    net_simple_open_ring.switch = net_simple_open_ring.switch.drop(11)

    net_simple_open_ring.switch = net_simple_open_ring.switch.reset_index(drop=True)

    pp.create_line(net_simple_open_ring, 2,5, length_km= 1.0, std_type="NA2XS2Y 1x185 RM/25 12/20 kV", name="line 6")
    #print(net_simple_open_ring.line)

    print(net_simple_open_ring.switch)
    Graph = action_modifier(net_simple_open_ring)

    modified_action = Graph.Output_Modify([0.9, 0.8, 0.7, 0.6, 0.5, 0.4])

    print(modified_action)

    Graph.print_information()
    
    
    print("\n\n")
    
    
    #modified ieee123에 대해서도 test
    from networks import create_network
    import numpy as np
    network_name= 'ieee123'
    der_opt = 'pv_wind'    
    network = create_network(network_name, der_opt).net
    safe_layer_DNR = action_modifier(network)
    print(network.line)
    print(network.switch)
    safe_layer_DNR.print_information()
    #logits = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.9, 0.8, 0.7, 0.6, 0.5]
    logits = np.random.rand(17)
    
    original_action_indices = np.argsort(logits)[-10:]
    original_action = np.ones(len(logits))
    for index in original_action_indices: original_action[index]=0
    
    modified_action = safe_layer_DNR.Output_Modify(logits)
    print("logits", logits.round(3))
    print("original_aciton",original_action)
    print("modified_aciton", modified_action)
    
    
    # 결과적으로 열린(=0) 스위치 수가 loop 수와 같은지 검증 필요
    # 현재 swtich_line_element와 
    
    from utils.check_radiality import Graph as check
    
    network.switch['closed']=np.bool_(modified_action)
    print(network.switch)
    
    def is_radial(net):
        net_graph=check(len(net.bus))

        for i in range(len(net.trafo)):
            net_graph.addEdge(net.trafo['hv_bus'][i],net.trafo['lv_bus'][i]) #변압기는 연결된 line 취급

        for i in range(len(net.line)):
            if False in list(net.switch[net.switch['element']==i]['closed']): #line element에 closed==False인 switch 하나라도 있으면
                pass #edge 생성하지 않음
            else : net_graph.addEdge(net.line['from_bus'][i],net.line['to_bus'][i]) #모두 True일 경우 생성함

        return net_graph.isTree()
    
    print(is_radial(network))