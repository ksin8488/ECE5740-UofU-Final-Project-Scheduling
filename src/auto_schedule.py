import sys
import argparse
import networkx as nx
import glpk
import subprocess

#To run the program: python3 src/auto_schedule.py -l=5 -a=20 -g=test/test1.edgelist

#Defining functions for pre-processing the graph representation and design specifications
def read_edgelist(file_path):
    G = nx.read_weighted_edgelist(file_path, create_using=nx.DiGraph, nodetype=int)
    return G

def preprocess_graph(G):
    #implement any required pre-processing here
    rootNode = -1 #Topmost node created before getting into the actual graph (represented as a -1)
    G.add_node(rootNode)
    return G, rootNode

def critical_path(G, latency):
    #For ever latency over the longest node path, you add 1 to each 
    pass
    
#Defining functions for generating ILP formulations and solving them using the GLPK solver
def generate_ilp_formulation(G, latency, memory):
    #implement ILP formulation generation here
    
    #print(0, nx.dag_longest_path(G)) #Get's the longest path in the graph
    rootNode = -1
    #---THIS IS FOR GETTING NODE LEVELS WITHOUT ALAP OR ASAP OPTIMINIZATION---      
    # Perform topological sort
    topo_order = list(nx.topological_sort(G))
    # Initialize node levels dictionary
    node_levels = {n: 1 for n in G.nodes()}

    # Calculate node levels
    for node in topo_order:
        for successor in G.successors(node):
            node_levels[successor] = max(node_levels[successor], node_levels[node] + 1)
            if(node_levels[successor] > latency):
                raise Exception("The current node depth is ", node_levels[successor], "while the latency constraint is ", latency)
        
    #---Calculate Slack for Nodes---
    asap = calculate_asap(G, latency)
    alap = calculate_alap(G, latency)
    print("ASAP scheudle:", asap)
    print("ALAP schedule:", alap)
    slackMob = compute_slack_mobility(asap, alap)
    print("Slack Mobility:", slackMob)
            
    for n in G:
        connectedNodes = sorted(list(G.adj[n]))
    
    #---ADDING TOTAL WEIGHT TO EACH NODE---
    TotalNodeWeight = [0]
    nx.set_node_attributes(G, TotalNodeWeight, "TotalWeight")
    
    for n in G:
        nodePred = list(G.predecessors(n))
        if len(nodePred) == 0: # In case the node has no predecessors (top level)
            G.nodes[n]["TotalWeight"] = 0 # Top level nodes have a weight/memory of 0
        else:
            total_weight = 0
            for np in nodePred:
                edge_weight = G[np][n]["weight"]
                total_weight += edge_weight
            G.nodes[n]["TotalWeight"] = int(total_weight)
            
    #TODO: PUT IN MINIMIZATION HERE AFTER WEIGHTS ARE CALCULATED
    min_Mem = minimize_memory_under_latency(G, latency)
    print("Min Mem under latency Output: ", min_Mem)
        
    min_Lat = minimize_latency_under_memory(G, memory, latency)
    print("Min Latency Output: ", min_Lat)
    
    filesMade = []
    # filesMade.append(create_ilp_file(G, min_Mem, True, memory))
    # filesMade.append(create_ilp_file(G, min_Lat, False, memory))
    
    #TODO: Version without minimization and gives latency instead
    filesMade.append(create_ilp_file(G, latency, True, memory))
    filesMade.append(create_ilp_file(G, latency, False, memory))
    
    return filesMade
            
def create_ilp_file(G, latency, memoryMinTrue, memory):
    #---ILP File Creation---
    if(memoryMinTrue == True):
        ilp_file = "memoryMin.ilp"
    else:
        ilp_file = "latencyMin.ilp"
    
    rootNode = -1
    for n in G:
        nodePred = list(G.predecessors(n))
        if len(nodePred) == 0: # In case the node has no predecessors (top level)
            G.nodes[n]["TotalWeight"] = 0 # Top level nodes have a weight/memory of 0
        else:
            total_weight = 0
            for np in nodePred:
                edge_weight = G[np][n]["weight"]
                total_weight += edge_weight
            G.nodes[n]["TotalWeight"] = int(total_weight)
    
    with open(ilp_file, 'w') as f: #'w' lets you write (overwrite) a file while 'a' lets you append/add to a file
        constraintNum = 0
        constraint = "c"
        var = "x"
        integerList = {} #Dictionary of integers to keep track for ILP formatting
        
        asapSchedule = calculate_asap(G, latency)
        alapSchedule = calculate_alap(G, latency)
        slackRange = compute_slack_mobility(asapSchedule, alapSchedule)
        
        f.write("Minimize\n")
        
        TotalWeight = "TotalWeight"
        obj_terms = [f"{G.nodes[n][TotalWeight]}x{n}" for n in G.nodes() if n != rootNode]
        f.write("obj: " + " + ".join(obj_terms) + "\n")
            
        f.write("\nSubject To\n")
        
        #Each node constraint
        for n in G:
            if(n == -1):
                continue
            else:
                f.write(f"{constraint}{str(constraintNum)}: ")
                
                #for slack in slackRange:
                if slackRange[n] > 0:
                    terms = []
                    for rangeNum in range(0,slackRange[n]+1):
                        terms.append(f"{var}{n}{asapSchedule[n]+rangeNum}")
                        integerList[n] = terms #Adds the new integer to the list to be used later
                    
                    f.write(" + ".join(terms))
                    f.write(" = 1\n")
                else:
                    f.write(f"{var}{n}{asapSchedule[n]} = 1\n")
                    integerList[n] =  f"{var}{n}{asapSchedule[n]}"
                
                constraintNum += 1

        f.write("\n")
        print("Full Dict:", integerList)
        
        # Add dependency constraints
        for n in G.nodes():
            if n != rootNode:
                predecessors = list(G.predecessors(n))
                for p in predecessors:
                    f.write(f"{constraint}{str(constraintNum)}: ")
                    terms1 = []
                    terms2 = []
                    if (type(integerList[n]) == list) | (type(integerList[p]) == list):
                        rangeNum = 0
                        if type(integerList[n]) == list:
                            for termIndex in integerList[n]:
                                terms1.append(f"{asapSchedule[n]+rangeNum}{integerList[n][rangeNum]}")
                                rangeNum = rangeNum + 1
                        else: 
                            terms1.append(f"{asapSchedule[n]+rangeNum}{integerList[n]}")
                            rangeNum = rangeNum + 1
                        
                        f.write(" + ".join(terms1))
                        f.write(" - ")
                        
                        rangeNum = 0
                        if type(integerList[p]) == list:
                            for termIndex in integerList[p]:
                                terms2.append(f"{asapSchedule[p]+rangeNum}{integerList[p][rangeNum]}")
                                rangeNum = rangeNum + 1
                        else: 
                            terms2.append(f"{asapSchedule[p]+rangeNum}{integerList[p]}")
                            rangeNum = rangeNum + 1
                           
                        f.write(" - ".join(terms2))
                        f.write(" >= 1\n")
                        
                    else:
                        f.write(f"{asapSchedule[n]}{integerList[n]} - {asapSchedule[p]}{integerList[p]} >= 1\n")
            
                    constraintNum += 1
            
        #f.write("\n") 
        
        # Add resource constraints (Based on memory?)
        resources = memory
        # for t in range(1, resources + 1):
        #     f.write(f"{constraint}{str(constraintNum)}: ")
        #     terms = [f"{var}{n}" for n in G.nodes() if n != rootNode]
        #     f.write(" + ".join(terms))
        #     f.write(f" <= {resources}\n")
        #     constraintNum += 1
             
        f.write("\n")
             
        #Integer Constraints
        integerNum = 0
        integerStr = "i"
        for n in G.nodes():
            if n==-1:
                continue
            else:
                if type(integerList[n]) != list:
                    f.write(f"{integerStr}{str(integerNum)}: ")
                    f.write(f"{integerList[n]} >= 0\n")
                    integerNum += 1
                else:
                    rangeNum = 0
                    for termIndex in integerList[n]:
                        f.write(f"{integerStr}{str(integerNum)}: ")
                        f.write(f"{integerList[n][rangeNum]} >= 0\n")
                        integerNum +=1
                        rangeNum = rangeNum + 1
        f.write("\n")
        
        #Resource Constraints
        resourceStr = "r"
        resourceNum = 0
        for n in G.nodes():
            if n==-1:
                continue
            else:
                rangeNum = 0
                if type(integerList[n]) != list:
                    f.write(f"{resourceStr}{str(resourceNum)}: ")
                    f.write(f"{integerList[n]} - {var}{n} <= 0\n") 
                    resourceNum += 1
                        
                else:
                    terms = []
                    for termIndex in integerList[n]:
                        terms.append(f"{integerList[n][rangeNum]}")
                        rangeNum += 1
                        
                    f.write(f"{resourceStr}{str(resourceNum)}: ")
                    f.write(" + ".join(terms))
                    f.write(f" - {var}{n} <= 0\n")
                    resourceNum += 1
                
        # f.write("\nBounds\n")
        # for n in G.nodes():
        #     if n != rootNode:
        #         f.write(f"0 <= {var}{n} <= {resources}\n")
            
        f.write("\nInteger\n")
        for n in G.nodes():
            if(n==-1):
                continue
            else:
                if type(integerList[n]) != list:
                    f.write(f"{integerList[n]} ")
                else:
                    rangeNum = 0
                    for termIndex in integerList[n]:
                        f.write(f"{integerList[n][rangeNum]} ")
                        rangeNum = rangeNum + 1
                    
            
        f.write("\n\nEnd")
        
    return ilp_file

def solve_ilp_formulation(ilp_formulation_file, minMemTrue):
    #implement ILP solution extraction using GLPK solver here
    if minMemTrue == True:
        output_file = "memOutput.sol"
    else:
        output_file = "latOutput.sol"
        
    result = subprocess.run(["glpsol", "--lp", ilp_formulation_file, "-o", output_file])
    return output_file, result.returncode

#TODO: Fix issue IN BOTH FUNCTIONS? where successors/predecesors are appearing on the same level
#TODO: Realized this is NOT to get the best schedule but just all possible schedules that fit. Then all those 
#possibilities will be put into GLPK and the best one outputted
def minimize_memory_under_latency(G, L):
    #Get the ASAP, ALAP and the Slack = ALAP-ASAP scheduling for different node "levels"
    asap_schedule = calculate_asap(G, L)
    alap_schedule = calculate_alap(G, L)
    slack_mobility = compute_slack_mobility(asap_schedule, alap_schedule)

    #Initialize a dictionary of total memory values for each level of the graph
    memory_usage = {level: 0 for level in range(1, L+1)}

    #Gets the level of the node and adds together the total memory for each level in an ASAP schedule
    for node in asap_schedule:
        level = asap_schedule[node]
        memory_usage[level] += G.nodes[node]["TotalWeight"]

    #Goes through node slack values
    for node, slack in slack_mobility.items():
        #Goes through the node's slack range
        for i in range(1, slack+1):
            #Uses slack range to add a new level then check if memory usage is less and updates Asap_schedule if so
            new_level = asap_schedule[node] + i
            if memory_usage[new_level] + G.nodes[node]["TotalWeight"] < memory_usage[asap_schedule[node]]:
                memory_usage[asap_schedule[node]] -= G.nodes[node]["TotalWeight"]
                memory_usage[new_level] += G.nodes[node]["TotalWeight"]
                asap_schedule[node] = new_level

    return asap_schedule

def minimize_latency_under_memory(G, M, L):
    asap_schedule = calculate_asap(G, L)
    alap_schedule = calculate_alap(G, L)
    slack_mobility = compute_slack_mobility(asap_schedule, alap_schedule)

    memory_usage = {level: 0 for level in range(1, L+1)}

    for node in asap_schedule:
        level = asap_schedule[node]
        memory_usage[level] += G.nodes[node]["TotalWeight"]

    for level in range(1, L+1):
        for node, slack in slack_mobility.items():
            if asap_schedule[node] == level:
                for i in range(1, slack+1):
                    new_level = asap_schedule[node] - i
                    #Checks if new level for the node does not exceed M constraint, if not then adds node to that level
                    if new_level >= 1 and memory_usage[new_level] + G.nodes[node]["TotalWeight"] <= M:
                        memory_usage[asap_schedule[node]] -= G.nodes[node]["TotalWeight"]
                        memory_usage[new_level] += G.nodes[node]["TotalWeight"]
                        asap_schedule[node] = new_level

    return asap_schedule
  
#TODO: GO OVER THIS AND CHECK IT'S OUTPUTS  
def latency_memory_pareto_analysis(G, max_latency, max_memory):
    pareto_results = {}
    for latency in range(1, max_latency + 1):
        for memory in range(1, max_memory + 1):
            try:
                mem_min_schedule = minimize_memory_under_latency(G, latency)
                lat_min_schedule = minimize_latency_under_memory(G, memory, latency)
                pareto_results[(latency, memory)] = (mem_min_schedule, lat_min_schedule)
            except Exception:
                pass

    # Extract Pareto-optimal solutions
    pareto_optimal_solutions = []
    for latency_memory, schedules in pareto_results.items():
        mem_min_schedule, lat_min_schedule = schedules
        is_pareto_optimal = True

        for other_latency_memory, other_schedules in pareto_results.items():
            other_mem_min_schedule, other_lat_min_schedule = other_schedules
            if (other_latency_memory != latency_memory and
                    max(other_mem_min_schedule.values()) <= max(mem_min_schedule.values()) and
                    max(other_lat_min_schedule.values()) <= max(lat_min_schedule.values())):
                is_pareto_optimal = False
                break

        if is_pareto_optimal:
            pareto_optimal_solutions.append((latency_memory, schedules))

    return pareto_optimal_solutions

def calculate_asap(G, latency):
    topo_order = list(nx.topological_sort(G))
    node_levels = {n: 1 for n in G.nodes()}

    for node in topo_order:
        for successor in G.successors(node):
            node_levels[successor] = max(node_levels[successor], node_levels[node] + 1)

    asap_schedule = {n: node_levels[n] for n in G.nodes() if n != -1}
    return asap_schedule

def calculate_alap(G, latency):
    topo_order = list(nx.topological_sort(G))[::-1]
    node_levels = {n: latency for n in G.nodes()}

    for node in topo_order:
        for predecessor in G.predecessors(node):
            if node != -1:
                node_levels[predecessor] = min(node_levels[predecessor], node_levels[node] - 1)

    alap_schedule = {n: node_levels[n] for n in G.nodes() if n != -1}
    return alap_schedule

def compute_slack_mobility(asap_schedule, alap_schedule):
    slack_mobility = {}
    for node in asap_schedule:
        slack_mobility[node] = alap_schedule[node] - asap_schedule[node]
    return slack_mobility

#Main function to parse input arguments and execute the tool
def main():
    parser = argparse.ArgumentParser(description='Automated ILP Scheduling Tool')
    parser.add_argument('-l', type=int, help='Latency L')
    parser.add_argument('-a', type=int, help='Memory M')
    parser.add_argument('-g', type=str, help='Path to the edgelist file')

    args = parser.parse_args()

    G = read_edgelist(args.g)
    G, rootNode = preprocess_graph(G)
    
    ilp_formulation = generate_ilp_formulation(G, args.l, args.a)
    
    memSolution_file, return_code = solve_ilp_formulation(ilp_formulation[0], True)
    latSolution_file, return_code = solve_ilp_formulation(ilp_formulation[1], False)
    
    if return_code == 0:
        print(f"memSolution file: {memSolution_file}")
        print(f"latSolution file: {latSolution_file}")
    else:
        print("Infeasible solution.")
        
    # paretoA = latency_memory_pareto_analysis(G, args.l, args.a)
    # print("Pareto Analysis Results:",paretoA)

if __name__ == "__main__":
    main()
