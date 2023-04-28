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

#Constraints
#i## is "wiggle room" so like x22 >=0, x23 >=0 means X2 can be on timing 2 and 3
#


var = "x"
tempEq = ""
nodeNum = []
constrNum = 0

with open('pred.ilp', 'a') as f:
    for n in Graph:
        adjList = Graph.adj[n]
        print(n, adjList)
        if n in nodeNum:
            print(n, "already exists")
            continue
        else:
            print(adjList.keys())
        nodeNum = nodeNum + [n]
        #example of dependency constraint: x4 <= x0 + 1

        #---Other group (3?) presentation steps---
        #used add with their own lables, what it was, and attributes, which feeds an output to an ILP
        #Generate min function by....(missed how)
        #ASAP and ALAP times are used to determine slack for a node ASAP times with DFS traversal recursive (keep track of level)
        #ALAP similar start from sink and perform asap in a reverse fashion
        #Generate execution constraints by determining the slack and comparing start and ednd times
        #Resource constraints by specify where each resource can exist in certain time and take into account the slack
        #Generate dependency by looking at all the nodes, parents, and possible slack
        #Generate closing by something with variables
        #os.system used to send the ilp to glpk

        #other group read the list like we did with readedgelist and used digraph
        #Used DFS to get path for ASAP, ALAP, and paths generated from DFS
        #Nodes have weights based on the edges (I think they transfered the info into a diGraph)

        #TONS OF CODE USED regardless. Can't get this done by Friday
