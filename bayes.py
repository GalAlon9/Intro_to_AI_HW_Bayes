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
        bayes_network.nodes["B("+str(node)+")"]["probabilities"]["B("+str(node)+")=1"] = {"mild": xi, 'stormy': 2*xi, 'extreme': 3*xi}
        bayes_network.nodes["B("+str(node)+")"]["probabilities"]["B("+str(node)+")=0"] = {"mild": 1-xi, "stormy": 1-2*xi, "extreme": 1-3*xi}
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
        if bayes_network.nodes["B("+str(node)+")"]["probabilities"]["B("+str(node)+")=1"]['mild'] > 0:
            relevant_nodes.append("B("+str(node)+")")
        for neighbor in graph.neighbors(node):
            #print(bayes_network.nodes["B("+str(neighbor)+")"]["probabilities"])
            # if bayes_network.nodes["B("+str(neighbor)+")"]["probabilities"]["B("+str(neighbor)+")=1"]['mild'] > 0:
            #     relevant_nodes.append("B("+str(neighbor)+")")
            relevant_nodes.append("B("+str(neighbor)+")")
            

        #each node has 2 states: true or false, so we will have 2^len(relevant_nodes) possible states
        states = [bin(i)[2:].zfill(len(relevant_nodes)) for i in range(2**len(relevant_nodes))]
        if len(relevant_nodes) == 1:
            if relevant_nodes[0] == "B("+str(node)+")":
                probabilities_false[str(list(states[0]))] = p2
                probabilities_false[str(list(states[1]))] = 1
            else:
                curr  = int(relevant_nodes[0][2:-1])
                probabilities_false[str(list(states[0]))] = min(1,p1*graph[node][curr]["weight"])
                probabilities_false[str(list(states[1]))] = 1
        else:    
            for state in states:
                #for loop to add base cases probabilities to the table

                #if the breakage of the node is true and all the breakage of the neighbors is false, the probability is p2 and the probability of the node to be broken is greater than 0
                if state[0] == '1' and state[1:] == '0'*(len(relevant_nodes)-1):
                    # if bayes_network.nodes["B("+str(node)+")"]["probabilities"]["true"]["mild"] > 0:
                    probabilities_false[str(list(state))] = p2
                    # else :
                    #     probabilities_false[tuple(state)] = 1
                    
                #if the breakage of the node is false and only one neighbor is true, the probability is min(1,p1*w(i,j))
                elif state[0] == '0' and state[1:].count('1') == 1:
                    
                    #get the weight of the edge between the node and the neighbor that is true
                    for i in range(len(state)):
                        if state[i] == '1':
                            #check if the B(i) node is not 0
                            # if bayes_network.nodes[relevant_nodes[i]]["probabilities"]["true"]["mild"] > 0:
                            w = graph.edges[node, int(relevant_nodes[i][2:-1])]["weight"]
                            # else:
                            #     w = 0
                    # if w == 0: probabilities_false[tuple(state)] = 1
                    # else: 
                    probabilities_false[str(list(state))] = min(1, p1*w)

            
                
            
        for state in states:
            #for loop to add the rest of the probabilities to the table
            if str(list(state)) not in probabilities_false:
                #multiply the probabilities of each base case that is true in the state
                prob = 1
                for i in range(len(state)):
                    if state[i] == '1':
                        base_case=['0']*len(state)
                        base_case[i] = '1'
                        base_case = ''.join(base_case)

                    
                        prob *= probabilities_false[str(list(base_case))]

                probabilities_false[str(list(state))] = prob


        
        #we want the probabilities to be in the format of B(i)=0, B(j)=1, B(k)=1, B(l)=1 etc.
        #so we will change the keys of the dictionary to be in this format
        # print(probabilities_false)
        new_probabilities_false = {}
        for state in probabilities_false:
            new_state = []
            #state is in the format of ['0', '1', '1', '1'] we want to run over 0,1,1,1
            
            curr_state = state[1:-1].split(', ')
            
            for i in range(len(curr_state)):
                val = curr_state[i]
                new_state.append(relevant_nodes[i]+"="+val)
            new_state = ', '.join(new_state)
            new_probabilities_false[new_state] = probabilities_false[state]
        
            
        # print("TEST")
        

        probabilities_false = new_probabilities_false
        
        #add the probabilities to the node
        bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["Ev("+str(node)+")=0"] = probabilities_false
        probabilities_true = {}
        for state in probabilities_false:
            probabilities_true[state] = 1-probabilities_false[state]
        bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["Ev("+str(node)+")=1"] = probabilities_true
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

def create_password(total: int):
    #create a password that its ascii value is total
    #use for the password ascii values between 32 and 127
    password = ""
    while total > 0:
        if total >= 127:
            password += chr(127)
            total -= 127
        else:
            password += chr(total)
            total -= total
    return password 
    
    
def print_blockage(bayes_network: DiGraph, node: str):
    # print("BREAKAGE OF", node[2:-1], ":")
    #print in the format of P(blocked|stormy) = 0.4
    for state in bayes_network.nodes["B("+str(node)+")"]["probabilities"]["B("+str(node)+")=1"]:
        print("P(blocked|"+state+") = ", bayes_network.nodes["B("+str(node)+")"]["probabilities"]["B("+str(node)+")=1"][state])    
    print()

def print_evacuees(bayes_network: DiGraph, node: str):
    # print("PEOPLE IN", node[3:-1], ":")
    for state in bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["Ev("+str(node)+")=1"]:
        #convert the state from tuple to string in this format:('0', '1')
        temp = str(state)
        print("P(people|"+temp+") = ", bayes_network.nodes["Ev("+str(node)+")"]["probabilities"]["Ev("+str(node)+")=1"][state])
    print()

def print_network(bayes_network, graph):
    print_weather(bayes_network)
    for node in graph.nodes:
        print("VERTEX:", node)
        print_blockage(bayes_network, node)
        print_evacuees(bayes_network, node)
    
def print_probabalistic_reasoning(bayes_network, evidence,graph):
    '''print the following probabilities, according to the given evidence:
    What is the probability that each of the vertices contains evacuees?
    What is the probability that each of the vertices is blocked?
    What is the distribution of the weather variable?
    What is the probability that a certain path (set of edges) is free from blockages? (Note that the distributions of blockages in vertices are NOT necessarily independent.)'''
    query1 = []
    for node in graph.nodes:
        query1.append("Ev("+str(node)+")")

    query2 = []
    for node in graph.nodes:
        query2.append("B("+str(node)+")")

    query3 = ["W"]

    #get path from user
    #path = input("Enter path: ")
    path = [ 2, 3, 4]
    # path = path.split(" ")
    path = [int(i) for i in path]

    query4 = []
    for i in range(len(path)-1):
        query4.append("B("+str(path[i])+")")
    
    print("What is the probability that each of the vertices contains evacuees?")
    for node in graph.nodes:
        print("P(Ev("+str(node)+") |", evidence, ") = ", enumeration_ask(["Ev("+str(node)+")"], evidence, bayes_network)["['Ev("+str(node)+")=1']"])
    print()

    print("What is the probability that each of the vertices is blocked?")
    for node in graph.nodes:
        print("P(B("+str(node)+") |", evidence, ") = ", enumeration_ask(["B("+str(node)+")"], evidence, bayes_network)["['B("+str(node)+")=1']"])
    print()

    print("What is the distribution of the weather variable?")
    if "W" in evidence:
        print("P(W |", evidence, ") = ", {w : 1 if evidence['W']==w else 0 for w in ["mild","stormy","extreme"]})
    else:
        print("P(W |", evidence, ") = ", enumeration_ask(["W"], evidence, bayes_network))
    print()

    print("What is the probability that a certain path (set of edges) is free from blockages?")
    query4_total = 1
    extended_evidence = evidence.copy()
    for query in query4:
        distribution=enumeration_ask([query], evidence, bayes_network)
        #print("P(", [query], "|", evidence, ") = ", distribution)
        #multiply by the probability of the node not being blocked
        query4_total *= distribution.get(str([query+"=0"]))
        #add the query to the evidence
        extended_evidence[query] = "0"
    print("P(",path," is free from blockages |", evidence, ") = ", query4_total)
    print()
    
def enumeration_all(vars,evidence,bayes_network):
    if len(vars) == 0:
        return 1
    Y = vars[0]
    parents = ""
    for parent in bayes_network.predecessors(Y):
        #evidence[parent] =  EV(1) = 1, EV(2) = 0, W = "stormy"
        val = evidence[parent]
        temp = val
        if Y == "B":
            temp = "W=" + val
        if Y[0:2] == "Ev": #val is true or false, we want temp to be in this format: "B(1)='1'" or "B(1)='0'" based on val, the number is the parent = B(1)
            if val == "1":
                temp = "B("+str(parent)[2]+")='1'"
            else:
                temp = "B("+str(parent)[2]+")='0'"
                
                
        #print("temp:", temp)

        parents += temp + ", "
    parents = parents[:-2]
        
    if Y in evidence.keys():
        # print("in evidence")
        # print("Y:", Y)
        # print('EVIDENCE:', evidence)
        # print('EVIDENCE[Y]:', evidence[Y])
        # print('PARENTS:', parents)
        # print("table: ",bayes_network.nodes[Y]["probabilities"])
        
        if parents == "":
            #print("P(y): ",bayes_network.nodes[Y]["probabilities"][evidence[Y]])
            return bayes_network.nodes[Y]["probabilities"][evidence[Y]] * enumeration_all(vars[1:],evidence,bayes_network)
        else:
            # print('P1: ',bayes_network.nodes[Y]["probabilities"][Y+'='+evidence[Y]])
            # print('P2: ',str(parents))
            # print("P(y|Pa(Y)): ",bayes_network.nodes[Y]["probabilities"][Y+'='+evidence[Y]][str(parents)])
            return bayes_network.nodes[Y]["probabilities"][Y+'='+evidence[Y]][str(parents)] * enumeration_all(vars[1:],evidence,bayes_network)
    else:
        sum = 0
        for state in bayes_network.nodes[Y]["probabilities"]:
            #add the state to a copy of the evidence
            extended_evidence = evidence.copy()
            if len(state.split('='))>1:
                #state is in format e.x B(1)=1, so we will retrieve the 1
                extended_evidence[Y] = state.split('=')[1]
            else:
                extended_evidence[Y] = state
            # print("Y:", Y)
            # print('STATE:', state)
            # print('PARENTS:', parents)
            # print("table: ",bayes_network.nodes[Y]["probabilities"])
            # print('Ext_EVIDENCE[Y]:', extended_evidence[Y])
            if parents == [] or parents == "":
                #print("P(y|Pa(Y)): ",bayes_network.nodes[Y]["probabilities"][extended_evidence[Y]])
                sum += bayes_network.nodes[Y]["probabilities"][state] * enumeration_all(vars[1:],extended_evidence,bayes_network)
            else:
                #print("P(y|Pa(Y)): ",bayes_network.nodes[Y]["probabilities"][extended_evidence[Y]])
                #print("P(y|Pa(Y)): ",bayes_network.nodes[Y]["probabilities"][extended_evidence[Y]][str(parents)])
                sum += bayes_network.nodes[Y]["probabilities"][state][str(parents)] * enumeration_all(vars[1:],extended_evidence,bayes_network)
        return sum


def enumeration_ask(query, evidence, bayes_network):
    '''
    input:
    query: a list of strings, each string is a query variable
    evidence: a dictionary of strings, each string is an evidence variable
    bayes_network: a DiGraph object
    output:
    a distribution of the query variables
    '''

    distribution = {}

    # query = {B(1), B(2), B(3)}
    # xi = {B(1)=0, B(2)=1, B(3)=1}
    #check if the evidence includes the query than the probability is 1 or 0
    #distribution is in this format {"['B(1)=0']": 0.6, "['B(1)=1']": 0.4000000000000001}
    for q in query:
        #q is str int the format of "key" : "value"
        if q in evidence.keys():
            
            if evidence[q] == "1":
                distribution["['"+q+"=1']"] = 1
                distribution["['"+q+"=0']"] = 0
            else:
                distribution["['"+q+"=1']"] = 0
                distribution["['"+q+"=0']"] = 1

            
                

                
    
    if distribution != {}:
        print ("distribution:", distribution)
        return distribution
        
    
    
    #iterate over all possible states of the query variables
    for state in all_possible_states(query, bayes_network):
        #if state is not list, make it a list
        if not isinstance(state, list):
            state = [state]
        #print ("state:", state)
        extended_evidence = evidence.copy()
        #add the state to the evidence
        #print("query:", query)
        for i in range(len(query)):
            extended_evidence[state[i].split('=')[0]] = state[i].split('=')[1]
        #we need to topological sort the evidence
        #TODO:
        #extended_evidence = topological_sort(extended_evidence, bayes_network)
        #create vars : all the variables in the bayes network 
        vars = []
        for node in bayes_network.nodes:
            if node.startswith("W"):
                vars.append(node)
        for node in bayes_network.nodes:
            if node.startswith("B"):
                vars.append(node)
        for node in bayes_network.nodes:
            if node.startswith("Ev"):
                vars.append(node)
        # print("vars:", vars)
        # print("extended_evidence:", extended_evidence)
        distribution[str(state)] = enumeration_all(vars,extended_evidence,bayes_network)

    #normalize the distribution
    sum = 0
    for state in distribution:
        sum += distribution[str(state)]
    for state in distribution:
        distribution[str(state)] /= sum
    
    return distribution

def all_possible_states(query, bayes_network):
    '''
    input:
    query: a list of strings, each string is a query variable
    evidence: a dictionary of strings, each string is an evidence variable
    bayes_network: a DiGraph object
    output:
    a list of all possible states of the query variables
    '''
    if len(query) == 0:
        return []

    
    if query[0] == "W":
        return [["W=mild"],["W=stormy"], ["W=extreme"]]

    if query[0][0] == "E":
        return [["Ev("+query[0][3:-1]+")=0"],["Ev("+query[0][3:-1]+")=1"]]

    # query is the type of {B(1), B(2), B(3)}
    # than we need to return all the possible states of the query variables
    # like [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]
    if query[0][0] == "B":
        states = [bin(i)[2:].zfill(len(query)) for i in range(2**len(query))]
        for i in range(len(states)):
            states[i] = "B("+query[0][2:-1]+")="+states[i]
        return states
    
        

       


