import sys
import argparse
import networkx as nx
#import glpk

#G represents a networkx graph
G = nx.path_graph(4)

nx.write_edgelist(G, "test.edgelist")
G = nx.path(4)
fh = open("test.edgelist", "wb")

nx.write_edgelist(G, fh)

nx.write_edgelist(G, "test.edgelist.gz")

nx.write_edgelist(G, "test.edgelist.gz", data=False)

G = nx.Graph()

G.add_edge(1, 2, weight=7, color="red")

nx.write_edgelist(G, "test.edgelist", data=False)

nx.write_edgelist(G, "test.edgelist", data=["color"])

nx.write_edgelist(G, "test.edgelist", data=["color", "weight"])

print(G.nodes())