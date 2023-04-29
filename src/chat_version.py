import sys
import argparse
import networkx as nx
import subprocess

# To run the program: python3 src/chat_version.py -l=5 -a=20 -g=test/test1.edgelist

def read_edgelist(file_path):
    G = nx.read_weighted_edgelist(file_path, create_using=nx.DiGraph, nodetype=int)
    return G

def preprocess_graph(G):
    rootNode = -1
    G.add_node(rootNode)
    
    return G, rootNode

def preprocess_design_specification(latency, memory):
    pass

def generate_ilp_formulation(G, latency, memory):
    rootNode = -1
    ilp_file = "pred.ilp"

    with open(ilp_file, "w") as f:
        # Objective function
        f.write("Minimize\n")
        obj_terms = [f"x{n}" for n in G.nodes() if n != rootNode]
        f.write("obj: " + " + ".join(obj_terms) + "\n")

        # Constraints
        f.write("Subject To\n")
        constraintNum = 0
        constraint = "c"
        var = "x"
        
        # Dependency constraints
        for n in G.nodes():
            if n != rootNode:
                predecessors = list(G.predecessors(n))
                for p in predecessors:
                    f.write(f"{constraint}{constraintNum}: {var}{n} - {var}{p} >= 1\n")
                    constraintNum += 1
        
        # Resource constraints
        resources = memory
        for t in range(1, resources + 1):
            f.write(f"{constraint}{constraintNum}: ")
            terms = [f"{var}{n}" for n in G.nodes() if n != rootNode]
            f.write(" + ".join(terms))
            f.write(f" <= {resources}\n")
            constraintNum += 1
        
        # Bounds
        f.write("Bounds\n")
        for n in G.nodes():
            if n != rootNode:
                f.write(f"0 <= {var}{n} <= {resources}\n")

        # Integer variables
        f.write("Generals\n")
        for n in G.nodes():
            if(n < 0):
                break
            else:
                f.write(f"{var}{n}\n")

        f.write("End\n")

    return ilp_file

def solve_ilp_formulation(ilp_formulation_file):
    output_file = "output.sol"
    subprocess.run(["glpsol", "--lp", ilp_formulation_file, "-o", output_file])
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Automated ILP Scheduling Tool')
    parser.add_argument('-l', type=int, help='Latency L')
    parser.add_argument('-a', type=int, help='Memory M')
    parser.add_argument('-g', type=str, help='Path to the edgelist file')

    args = parser.parse_args()

    G = read_edgelist(args.g)
    G, rootNode = preprocess_graph(G)
    ilp_formulation = generate_ilp_formulation(G, args.l, args.a)
    solution_file = solve_ilp_formulation(ilp_formulation)

    print(f"Solution file: {solution_file}")

if __name__ == "__main__":
    main()