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
    
    def merge_cycle_componenet(self, main_list, target_switch):
        self.lists_to_merge = list()
        self.initial_main_list = main_list.copy()

        for sub_list in main_list:
            if target_switch in sub_list:
                print(sub_list)
                self.lists_to_merge.append(sub_list)
                if len(self.lists_to_merge) == 2:
                    break
        
        print(self.lists_to_merge)

        if not self.lists_to_merge:
            return main_list
        
        merged_list = []
        for item in self.lists_to_merge[0] + self.lists_to_merge[1]:
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
    
    def Output_Modify(self, action_list):
        assert len(action_list) == self.switch_number, f"(action_modifer) Action number {len(action_list)} != switch number {self.switch_number}"

        #branch_component_hard_copy
        self.branch_component_save = self.branch_component.copy()
        print(self.branch_component_save)

        # action에 index 부여를 위해 DataFrame으로 변환 후 ordering
        self.action_data = pd.DataFrame(action_list,columns=['value'])
        self.action_data['switch_line_element'] = self.net_information.switch.element
        self.action_data_ordering = self.action_data.sort_values(by=['value'], ascending=False)
        #print(self.action_data_ordering)
        # 각 Cycle마다의 index 부여를 위해 따로 list 생성
        self.cycle_number = len(self.branch_component_save)
        self.cycle_index = list(range(len(self.branch_component_save)))
        #print(self.cycle_index)
        # 함수 출력을 위한 empty list
        self.result_action = [1 for i in range(self.switch_number)]
        #print("cycle_index :", self.cycle_index)

        for j in range(len(self.action_data_ordering)):
            if not self.cycle_index:
                    #self.result_action.append(1)
                    continue
            #print("switch_element :", self.action_data_ordering['switch_line_element'].iloc[j])
            for cycle_components in self.branch_component_save:
                #print("component_list : ", self.branch_component_save[k])
                self.double_break = False
                # 해당 switch가 loop에 포함되는 상황을 찾으면 
                if self.action_data_ordering['switch_line_element'].iloc[j] in cycle_components:
                    self.branch_component_save = self.merge_cycle_componenet(self.branch_component_save, self.action_data_ordering['switch_line_element'].iloc[j])
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
            #print("result : ", self.result_action)

        #k번째 branch_component에서 index 즉, 해당 branch 삭제
        #print(self.result_action)
        # 차례대로 loop component에 비교해서 숫자를 없애가면 됨 component list에도 indexing을 해서 하나 없애면 그 cycle은 뺄 수 있도록 만들어야 함..
        return self.result_action #binary list
        
    def print_information(self):
        print("switch_number : "+str(self.switch_number))
        print("line_component_of_each_cycle : ", self.branch_component)