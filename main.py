import networkx as nx
import matplotlib.pyplot as plt
from networkx import DiGraph, Graph
from typing import List, Dict
from bayes import *
from pirsur import *


def get_evidence(graph: Graph,evidence: dict):
    print("Choose the evidence type:")
    print("1. Weather")
    print("2. Blockage")
    print("3. People")
    
    option = int(input())
    if option == 1:
        print("Choose the weather:")
        print("1. mild")
        print("2. stormy")
        print("3. extreme")
        weather = int(input())
        #add evidence to the dictionary
        evidence["W"] = "1" if weather == 1 else "2" if weather == 2 else "3"
    elif option == 2:
        print("Choose the node:")
        for node in graph.nodes:
            print(node)
        node = int(input())
        print("Choose the evidence:")
        print("1. blocked")
        print("2. not blocked")
        evidence["B("+str(node)+")"] = "1" if int(input()) == 1 else "0"
    elif option == 3:
        print("Choose the node:")
        for node in graph.nodes:
            print(node)
        node = int(input())
        print("Choose the evidence:")
        print("1. people")
        print("2. no people")
        evidence["Ev("+str(node)+")"] = "1" if int(input()) == 1 else "0"
        
    return evidence
                
    
def get_action(evidence: dict):
    print("Choose the action:")
    print("1. Add evidence")
    print("2. Reset evidence")
    print("3. Probabilistic reasoning")
    print("4. Exit")
    option = int(input())
    if option == 1:
        evidence=get_evidence(graph, evidence)
    elif option == 2:
        evidence = {}
    elif option == 3:
        print_probabalistic_reasoning(bayes_network, evidence)
    elif option == 4:
        return -1
    return evidence

if __name__ == "__main__":
    global graph
    global bayes_network
    graph, weather, blocked_nodes = parse("input.txt")
    bayes_network = create_bayes_network(graph, weather, blocked_nodes)
    evidence = {"W": "mild"}
    # evidence = {}
    # while(True):
    #     evidence=get_action(evidence=evidence)
    #     sorted_evidence={}
    #     #topological sort of the evidence
    #     for key, value in evidence.items():
    #         if key=='W':
    #             sorted_evidence[key]=value
    #     for key, value in evidence.items():
    #         if key[0]=='B':
    #             sorted_evidence[key]=value
    #     for key, value in evidence.items():
    #         if key[0]=='E':
    #             sorted_evidence[key]=value        
    #     evidence=sorted_evidence
        
    #     print(evidence)
    #     if evidence == -1:
    #         break
       
    print_network(bayes_network,graph=graph)
    print_probabalistic_reasoning(bayes_network, evidence, graph=graph)