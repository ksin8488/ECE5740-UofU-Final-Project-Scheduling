import sys
import argparse
import networkx as nx
import glpk
import os
#NOTE: Final Project MUST use edgelist graph!

#G represents a networkx graph

#Creates an example edgelist that is NOT saved as a file
# textline = "1 2 3"
# fh = open("test_test.edgelist", "w")
# d = fh.write(textline)
# fh.close()

#Test_graph = nx.read_edgelist("test.edgelist", nodetype=int, data=(("weight", float),))
path = os.path.join(sys.path[0], "test1.edgelist")
fh = open(os.path.join(sys.path[0], "test1.edgelist"), "r")
fh.close()

Graph = nx.read_edgelist(path, nodetype=str, data=(("operation", str),("time",int),))
print(Graph, "\n")
print(Graph.edges(data=True))

# G = nx.path_graph(4)

# G = nx.write_edgelist(G, "test.edgelist")
# G = nx.path(4)
# fh = open("test.edgelist", "wb")

# nx.write_edgelist(G, fh)

# nx.write_edgelist(G, "test.edgelist.gz")

# nx.write_edgelist(G, "test.edgelist.gz", data=False)

# G = nx.Graph()

# G.add_edge(1, 2, weight=7, color="red")

# nx.write_edgelist(G, "test.edgelist", data=False)

# nx.write_edgelist(G, "test.edgelist", data=["color"])

# nx.write_edgelist(G, "test.edgelist", data=["color", "weight"])

# print(G.nodes())

# #nx.DiGraph represents a directed graph (A DFG is a Data Flow Graph which is a directed graph)
# dfg = nx.DiGraph()

# #Create edges which creates the nodes between the edges
# dfg.add_edges_from([("root", "a"), ("a", "b"), ("a", "e"), ("b", "c")
# ,("b", "d"), ("d", "e")])

# #Can add attributes to graphs, nodes, and edges that can be checked
# dfg.add_node("n1", operation="+")

# #show the attributes ("\n" is just a new line)
# print(dfg.nodes["n1"], "\n")

# #Prints out the nodes created
# print(dfg.nodes()) 

# print(1 in dfg) #Checks if node 1 is in graph
# print(len(dfg)) #number of nodes in graph