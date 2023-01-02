from networkx import DiGraph, Graph

def create_bayes_network(graph: Graph,weather:dict,broken_given_weather:dict) -> DiGraph:
    """Create a bayes network from a graph.
    Args:
        graph (Graph): A graph representing a bayes network.
        input (str): The input file name.

    Returns:
        DiGraph: A directed graph representing a bayes network.
    """
    #query the user for parameters p1 and p2:
    p1 = float(input("Enter p1: "))
    p2 = float(input("Enter p2: "))

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
    bayes_network.add_node("W", states=["mild", "stormy", "extreme"])
    #add to the weather node the probabilities of each state from the dictionary
    for state in weather:
        bayes_network.nodes["W"]["probabilities"][state] = weather[state]

        
    #add the breakage nodes to the graph
    for node in graph.nodes:
        bayes_network.add_node("B("+node+")", states=["true", "false"])
        #add to the breakage node the probabilities of each state from the dictionary this way: dictionary["node"] = x(i)
        xi = broken_given_weather[node]
        bayes_network.nodes["B("+node+")"]["probabilities"]["true"] = {"mild": xi, "stormy": 2*xi, "extreme": 3*xi}
        bayes_network.nodes["B("+node+")"]["probabilities"]["false"] = {"mild": 1-xi, "stormy": 1-2*xi, "extreme": 1-3*xi}
        #add an edge between the weather node and the breakage node
        bayes_network.add_edge("W", "B("+node+")")

    #add the people nodes to the graph
    for node in graph.nodes:
        bayes_network.add_node("Ev("+node+")", states=["true", "false"])
        # add qs the probability to not contain people given the breakage of the node itself 
        bayes_network.nodes["Ev("+node+")"]["probabilities"]["false"] = {"true": p2, "false": 1-p2}
    
        

