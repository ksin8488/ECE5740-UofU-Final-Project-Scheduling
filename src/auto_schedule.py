import sys
import argparse
import networkx as nx
import glpk

#To run the program: python3 src/auto_schedule.py -l=5 -a=20 -g=test/test1.edgelist

#Defining functions for pre-processing the graph representation and design specifications
def read_edgelist(file_path):
    G = nx.read_weighted_edgelist(file_path, create_using=nx.DiGraph, nodetype=int)
    return G

def preprocess_graph(G):
    #implement any required pre-processing here
    rootNode = -1 #Topmost node created before getting into the actual graph (represented as a -1)
    G.add_node(rootNode)
    lastNode = max(G.nodes()) #Gets the last node in the graph

    #print(0, nx.dag_longest_path(G)) #Get's the longest path in the graph
    
    #---THIS IS FOR GETTING NODE LEVELS WITHOUT ALAP OR ASAP OPTIMINIZATION---      
    # Perform topological sort
    topo_order = list(nx.topological_sort(G))
    # Initialize node levels dictionary
    node_levels = {n: 0 for n in G.nodes()}

    # Calculate node levels
    for node in topo_order:
        for successor in G.successors(node):
            node_levels[successor] = max(node_levels[successor], node_levels[node] + 1)
            
    for nodes in node_levels:
        print(nodes, node_levels[nodes])
        
    for n in G:
        connectedNodes = sorted(list(G.adj[n]))
        print(n, connectedNodes)
        print(n, list(G.predecessors(n)))
        #print(n, G.degree(n))
        #print(n, nx.dfs_predecessors(G,n))
        #print(n, nx.dfs_successors(G,n))
        #print(n, G.edges(n))
    
    #---ADDING TOTAL WEIGHT TO EACH NODE---
    #Testing for getting and setting memory values
    print(G.out_edges())
    print(G.get_edge_data(1,4))
    edgeInt = G[1][4]["weight"]
    TotalNodeWeight = [0.0]
    nx.set_node_attributes(G, TotalNodeWeight, "TotalWeight")
    G.nodes[1]["TotalWeight"] = edgeInt
    print(G.nodes[1]["TotalWeight"])
    
    # for n in G:
    #     nodePred = list(G.predecessors(n))
    #     for np in nodePred:
    #         if(len(nodePred) == 0.0): #In case the node has no predecesors (top level)
    #             G[n]["TotalWeight"] = 0.0 #Top level nodes have a weight/memory of 0
    #         else:
    #             edgeInt = G[np][n]["weight"]
    #             nodeWeight = G.nodes[n]["TotalWeight"]
    #             edgeInt = edgeInt + float(nodeWeight[0])
    #             G.nodes[n]["TotalWeight"] = edgeInt
                
    #             print(np, n, G.nodes[n]["TotalWeight"])
            
    #---ILP File Creation---  
    with open('pred.ilp', 'w') as f: #'w' lets you write (overwrite) a file while 'a' lets you append/add to a file
        constraintNum = 0
        constraint = "c"
        var = "x"
        
        f.write("Minimize\n")
        f.write("Subject To\n")
        
        #Each node constraint
        for n in G:
            if(n == -1):
                continue
            else:
                f.write(f"{constraint}{str(constraintNum)}: ")
                f.write(f"{var}{n} = 1\n")
                constraintNum += 1
          
        #ANOTHER way to get dependency constraints  
        # for edge in G.edges():
        #     if edge[0] != rootNode:
        #         f.write(f"{constraint}{str(constraintNum)}: {var}{edge[1]} - {var}{edge[0]} >= 1\n")
        #         constraintNum += 1

        f.write("\n")
        
        # Add dependency constraints
        for n in G.nodes():
            if n != rootNode:
                predecessors = list(G.predecessors(n))
                for p in predecessors:
                    f.write(f"{constraint}{str(constraintNum)}: {var}{n} - {var}{p} >= 1\n")
                    constraintNum += 1
               
        f.write("\n")
             
        #Integer Constraints
        integerNum = 0
        integerStr = "i"
        for n in G.nodes():
            f.write(f"{integerStr}{str(integerNum)}: {var}{n} >= 0\n")
            integerNum += 1
            
        f.write("\nInteger\n")
        for n in G.nodes():
            if(n==-1):
                continue
            else:
                f.write(f"{var}{n} ")
            
        f.write("\n\nEnd")

def preprocess_design_specification(latency, memory):
    #implement any required pre-processing here
    pass

#Defining functions for generating ILP formulations and solving them using the GLPK solver
def generate_ilp_formulation(G, latency, memory):
    #implement ILP formulation generation here
    if(len(nx.dag_longest_path(G)) > latency):
        raise Exception("The graph's longest path is ", len(nx.dag_longest_path(G)), "while the latency constraint is ", latency)
    
        # Add resource constraints (Based on memory?)
        resources = memory
        for t in range(1, resources + 1):
            f.write(f"{constraint}{str(constraintNum)}: ")
            terms = [f"{var}{n}" for n in G.nodes() if n != rootNode]
            f.write(" + ".join(terms))
            f.write(f" <= {resources}\n")
            constraintNum += 1

        f.write("Bounds\n")
        for n in G.nodes():
            if n != rootNode:
                f.write(f"0 <= {var}{n} <= {resources}\n")

def solve_ilp_formulation(ilp_formulation):
    #implement ILP solution extraction using GLPK solver here
    pass

#Defining functions for handling the scheduling objectives
def minimize_memory_under_latency(G, L):
    #implement memory minimization under latency L here
    pass

def minimize_latency_under_memory(G, M):
    #impliment latency minimization under memory M here
    pass

def latency_memory_pareto_analysis(G, L, M):
    #implement Pareto-optimal analysis here
    pass

#Main function to parse input arguments and execute the tool
def main():
    parser = argparse.ArgumentParser(description='Automated ILP Scheduling Tool')
    parser.add_argument('-l', type=int, help='Latency L')
    parser.add_argument('-a', type=int, help='Memory M')
    parser.add_argument('-g', type=str, help='Path to the edgelist file')

    args = parser.parse_args()

    G = read_edgelist(args.g)
    preprocess_graph(G)
    generate_ilp_formulation(G, args.l, args.a)
    # preprocess_design_specifications(args.l, args.a)

    # minimize_memory_under_latency(G, args.l)
    # minimize_latency_under_memory(G, args.a)
    # latency_memory_pareto_analysis(G, args.l, args.a)

if __name__ == "__main__":
    main()
