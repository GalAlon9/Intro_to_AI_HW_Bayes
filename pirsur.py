import networkx as nx
import matplotlib.pyplot as plt


def parse(file:str):
    graph = nx.Graph()
    #open file
    f = open(file, 'r')
    #remove empty lines
    lines = [line for line in f if line.strip()]
    
    #first line after "#N" is the number of nodes
    num_nodes = int(lines[0].split(' ')[1])
    
    #next num_nodes lines are the nodes
    blocked_nodes_probabilities = {}
    for i in range(num_nodes):
        line = lines[1+i].split()
        blocked_nodes_probabilities[i+1] = line[3] if 'F'in line else 0
        graph.add_node(i+1)
    #rest of the file is the edges
    lineNum=1+num_nodes
    #skip to rows which start with #E
    while(lineNum < len(lines) and lines[lineNum][1] != 'E'):
        lineNum += 1

    while(lineNum < len(lines) and lines[lineNum][1] != 'W'):
        line = lines[lineNum].split(' ')
        graph.add_edge(int(line[1]), int(line[2]), weight=float(line[3][1:]))
        lineNum += 1

    #read weather probabilities
    line = lines[lineNum].split(' ')
    weather_probabilities = {'mild': float(line[1]), 'stormy': float(line[2]), 'extreme': float(line[3])}
    
    return graph, weather_probabilities, blocked_nodes_probabilities