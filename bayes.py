from networkx import DiGraph, Graph
import networkx as nx
import matplotlib.pyplot as plt


def print_graph(graph: nx.Graph):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, nodelist=[node for node in graph.nodes], node_color='r')
    nx.draw_networkx_labels(graph, pos, labels={node: f"{node}" for node in graph.nodes})
    #add the weights to the edges and draw the edges with the weights
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edges(graph, pos, edgelist=[edge for edge in graph.edges], width=1.0, alpha=0.5)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.show()


def create_bayes_network(graph: Graph,weather:dict,broken_given_weather:dict) -> DiGraph:
    """Create a bayes network from a graph.
    Args:
        graph (Graph): A graph representing a bayes network.
        input (str): The input file name.

    Returns:
        DiGraph: A directed graph representing a bayes network.
    """
    #query the user for parameters p1 and p2:
    # p1 = float(input("Enter p1: "))
    # p2 = float(input("Enter p2: "))
    p1=0.2
    p2=0.3
    """Create a directed graph with:
            1. a weather node W with 3 states: mild, stormy, extreme
            2. for each node i in the graph, B(i) is a node representing the breakage of i'th node with 2 states: true, false.
                P(B(i)=true|W=mild) =x(i)  , P(B(i)=true|W=stormy) = 2x(i), P(B(i)=true|W=extreme) = 3x(i)
            
            W is connected to all B(i) nodes.
            x(i) is given in the input file.

            3. for each node i in the graph, Ev(i) is a node representing the probability of i'th node to contain people with 2 states: true, false.
                
                P(Ev(i)=false|B(i)=true, all other neighbors of i are false B(j)=false for all j!=i) = p2  ( p2 given in the input file)
                P(Ev(i)=false|B(i)=false, and only one neighbor of i is true B(j)=true for exactly one j!=i) = min(1,p1*w(i,j)) (p1 is given in the input file and w(i,j) is the weight of the edge between i and j)
             
            Ev(i) is connected to B(i) and all other B(j) nodes that are neighbors of i.
    """  
    #create a directed graph
    bayes_network = DiGraph()
    #add nodes to the graph
    bayes_network.add_node("W", states=["mild", "stormy", "extreme"], probabilities={})
    #add to the weather node the probabilities of each state from the dictionary
    for state in weather:
        bayes_network.nodes["W"]["probabilities"][state] = weather[state]

        
    #add the breakage nodes to the graph
    for node in graph.nodes:
        bayes_network.add_node("B("+str(node)+")", states=["true", "false"], probabilities={})
        #add to the breakage node the probabilities of each state from the dictionary this way: dictionary["node"] = x(i)
        xi = float(broken_given_weather[node])
        bayes_network.nodes["B("+str(node)+")"]["probabilities"]["true"] = {"mild": xi, "stormy": 2*xi, "extreme": 3*xi}
        bayes_network.nodes["B("+str(node)+")"]["probabilities"]["false"] = {"mild": 1-xi, "stormy": 1-2*xi, "extreme": 1-3*xi}
        #add an edge between the weather node and the breakage node
        bayes_network.add_edge("W", "B("+str(node)+")")

    #add the people nodes to the graph
    for node in graph.nodes:
        bayes_network.add_node("Ev("+str(node)+")", states=["true", "false"], probabilities={})
        # we want to add the probabilities given the breakage of the node and the breakage of its neighbors
        # we will use a dictionary to store the probabilities
        # each key in the dictionary will be a tuple of the states of the breakage of the node and its neighbors
        # each value in the dictionary will be the probability of the node not containing people given the states of the breakage of the node and its neighbors
        probabilities_false = {}
        # we will use a list to store the states of the breakage of the node and its neighbors
        relevant_nodes = []
        relevant_nodes.append("B("+str(node)+")")
        for neighbor in graph.neighbors(node):
            relevant_nodes.append("B("+str(neighbor)+")")
            

        #each node has 2 states: true or false, so we will have 2^len(relevant_nodes) possible states
        states = [bin(i)[2:].zfill(len(relevant_nodes)) for i in range(2**len(relevant_nodes))]
        for state in states:
            #for loop to add base cases probabilities to the table

            #if the breakage of the node is true and all the breakage of the neighbors is false, the probability is p2
            if state[0] == '1' and state[1:] == '0'*(len(relevant_nodes)-1):
                probabilities_false[tuple(state)] = p2
                
            #if the breakage of the node is false and only one neighbor is true, the probability is min(1,p1*w(i,j))
            elif state[0] == '0' and state[1:].count('1') == 1:
                #get the weight of the edge between the node and the neighbor that is true
                for i in range(len(state)):
                    if state[i] == '1':
                        w = graph.edges[node, int(relevant_nodes[i][2:-1])]["weight"]
                probabilities_false[tuple(state)] = min(1, p1*w)
            
        for state in states:
            #for loop to add the rest of the probabilities to the table
            if tuple(state) not in probabilities_false:
                #multiply the probabilities of each base case that is true in the state
                prob = 1
                for i in range(len(state)):
                    if state[i] == '1':
                        base_case=['0']*len(state)
                        base_case[i] = '1'
                        prob *= probabilities_false[tuple(base_case)]

                probabilities_false[tuple(state)] = prob



        #we want the probabilities to be in the format of B(i)=0, B(j)=1, B(k)=1, B(l)=1 etc.
        #so we will change the keys of the dictionary to be in this format
        # print(probabilities_false)
        new_probabilities_false = {}
        for state in probabilities_false:
            new_state = ""
            for i in range(len(state)):
                new_state += relevant_nodes[i]+"="+state[i]+", "
            new_state = new_state[:-2]
            new_probabilities_false[new_state] = probabilities_false[state]
        # print("TEST")
        # print(new_probabilities_false)

        probabilities_false = new_probabilities_false

        #add the probabilities to the node
        bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["false"] = probabilities_false
        probabilities_true = {}
        for state in probabilities_false:
            probabilities_true[state] = 1-probabilities_false[state]
        bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["true"] = probabilities_true
        #connect the node to the breakage node and all the breakage nodes of its neighbors
        for neighbor in relevant_nodes:
            bayes_network.add_edge(neighbor, "Ev("+str(node)+")")

        

        
    return bayes_network
    

def print_weather(bayes_network: DiGraph):
    print("WEATHER:")
    for state in bayes_network.nodes["W"]["probabilities"]:
        #print P(state) = probability
        print("P("+state+") = ", bayes_network.nodes["W"]["probabilities"][state])
        
    print()
    
    
def print_blockage(bayes_network: DiGraph, node: str):
    # print("BREAKAGE OF", node[2:-1], ":")
    #print in the format of P(blocked|stormy) = 0.4
    for state in bayes_network.nodes["B("+str(node)+")"]["probabilities"]["true"]:
        print("P(blocked|"+state+") = ", bayes_network.nodes["B("+str(node)+")"]["probabilities"]["true"][state])    
    print()

def print_evacuees(bayes_network: DiGraph, node: str):
    # print("PEOPLE IN", node[3:-1], ":")
    for state in bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["true"]:
        #convert the state from tuple to string in this format:('0', '1')
        temp = str(state)
        print("P(people|"+temp+") = ", bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["true"][state])
    print()

def print_network(bayes_network, graph):
    print_weather(bayes_network)
    for node in graph.nodes:
        print("VERTEX:", node)
        print_blockage(bayes_network, node)
        print_evacuees(bayes_network, node)
    
def print_probabalistic_reasoning(bayes_network, evidence):
    '''print the following probabilities, according to the given evidence:
    What is the probability that each of the vertices contains evacuees?
What is the probability that each of the vertices is blocked?
What is the distribution of the weather variable?
What is the probability that a certain path (set of edges) is free from blockages? (Note that the distributions of blockages in vertices are NOT necessarily independent.)'''
    pass