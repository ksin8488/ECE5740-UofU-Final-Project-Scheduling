
import sys
import argparse
import networkx as nx
import glpk
import subprocess

#To run the program: python3 src/test_auto.py -l=5 -a=20 -g=test/test1.edgelist

#Defining functions for pre-processing the graph representation and design specifications
def read_edgelist(file_path):
    G = nx.read_weighted_edgelist(file_path, create_using=nx.DiGraph, nodetype=int)
    return G

def preprocess_graph(G):
    #implement any required pre-processing here
    rootNode = -1 #Topmost node created before getting into the actual graph (represented as a -1)
    G.add_node(rootNode)
    return G, rootNode

def preprocess_design_specification(latency, memory):
    #implement any required pre-processing here
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
    print(asap)
    print(alap)
    slackMob = compute_slack_mobility(asap, alap)
    print(slackMob)
            
    for n in G:
        connectedNodes = sorted(list(G.adj[n]))
        #print(n, connectedNodes)
        #print(n, list(G.predecessors(n)))
    
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
            #print(n, G.nodes[n]["TotalWeight"])
                
    #---ILP File Creation---  TODO: MOVE THIS INTO ITS OWN METHOD
    ilp_file = "pred.ilp"
    with open(ilp_file, 'w') as f: #'w' lets you write (overwrite) a file while 'a' lets you append/add to a file
        constraintNum = 0
        constraint = "c"
        var = "x"
        
        f.write("Minimize\n")
        TotalWeight = "TotalWeight"
        obj_terms = [f"{G.nodes[n][TotalWeight]}x{n}" for n in G.nodes() if n != rootNode]
        f.write("obj: " + " + ".join(obj_terms) + "\n")
            
        f.write("\nSubject To\n")
    
        #TODO: PUT IN MINIMIZATION HERE AFTER WEIGHTS ARE CALCULATED
        min_Mem = minimize_memory_under_latency(G, latency)
        print("Min Mem under latency Output: ", min_Mem)
        
        min_Lat = minimize_latency_under_memory(G, memory, latency)
        print("Min Latency Output: ", min_Lat)
        
        #Each node constraint
        for n in G:
            if(n == -1):
                continue
            else:
                f.write(f"{constraint}{str(constraintNum)}: ")
                f.write(f"{var}{n} = 1\n")
                constraintNum += 1

        f.write("\n")
        
        # Add dependency constraints
        for n in G.nodes():
            if n != rootNode:
                predecessors = list(G.predecessors(n))
                for p in predecessors:
                    f.write(f"{constraint}{str(constraintNum)}: {var}{n} - {var}{p} >= 1\n")
                    constraintNum += 1
            
        f.write("\n") 
        
        # Add resource constraints (Based on memory?)
        resources = memory
        for t in range(1, resources + 1):
            f.write(f"{constraint}{str(constraintNum)}: ")
            terms = [f"{var}{n}" for n in G.nodes() if n != rootNode]
            f.write(" + ".join(terms))
            f.write(f" <= {resources}\n")
            constraintNum += 1
             
        f.write("\n")
             
        #Integer Constraints
        integerNum = 0
        integerStr = "i"
        for n in G.nodes():
            if n==-1:
                continue
            else:
                f.write(f"{integerStr}{str(integerNum)}: {var}{n} >= 0\n")
                integerNum += 1

        f.write("\nBounds\n")
        for n in G.nodes():
            if n != rootNode:
                f.write(f"0 <= {var}{n} <= {resources}\n")
            
        f.write("\nInteger\n")
        for n in G.nodes():
            if(n==-1):
                continue
            else:
                f.write(f"{var}{n} ")
            
        f.write("\n\nEnd")
        
    return ilp_file

def solve_ilp_formulation(ilp_formulation_file):
    #implement ILP solution extraction using GLPK solver here
    output_file = "output.sol"
    result = subprocess.run(["glpsol", "--lp", ilp_formulation_file, "-o", output_file])
    return output_file, result.returncode

#Defining functions for handling the scheduling objectives
# def minimize_memory_under_latency(G, L): 
#     #implement memory minimization under latency L here
#     asapRes = calculate_asap(G, L)
#     alapRes = calculate_alap(G, L)
#     slackRes = compute_slack_mobility(asapRes, alapRes)
    
#     #Start with ASAP scheduling and check the total memory of each level (which is the TotalMemory attribute of each node on that level added together)
#     #Then by using the slackRes, move around the nodes on the graph so each level has the minimum amount per level as possible
#     pass

# def minimize_latency_under_memory(G, M, L):
#     #impliment latency minimization under memory M here
#     asapRes = calculate_asap(G, L)
#     alapRes = calculate_alap(G, L)
#     slackRes = compute_slack_mobility(asapRes, alapRes)
    
#     #Start with ASAP scheduling and check the total memory of each level (which is the TotalMemory attribute of each node on that level added together)
#     #Then by using SlackRes levels, move around the nodes and their dependents so each level is less or equal to M but also at the least level possible
#     #If no version has the total memory of each level <= M then you get a warning message instead
#     pass

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
    
def latency_memory_pareto_analysis(G, L, M):
    #implement Pareto-optimal analysis here
    pass

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
    solution_file, return_code = solve_ilp_formulation(ilp_formulation)

    if return_code == 0:
        print(f"Solution file: {solution_file}")
    else:
        print("Infeasible solution.")

if __name__ == "__main__":
    main() 