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

Graph = nx.read_edgelist(path, nodetype=int, data=(("memory", int),))

# print(Graph, "\n")
# prin

# print(nx.dfs_predecessors(Graph))
# print(nx.dfs_successors(Graph))

# print(dict(nx.bfs_predecessors(Graph, 0)))
# print(dict(nx.bfs_successors(Graph, 0)))

# print(nx.descendants(Graph,5))

for n in Graph:
    graphDict = nx.neighbors(Graph, n)
    print(str(n), Graph.adj[n])

# var = "x"
# tempEq = ""
# with open('pred.ilp', 'a+') as f:
#     for n in Graph:

