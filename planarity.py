import networkx as nx
import itertools

it = 0


def is_connected(G):
    def _DFS_node_count(G, start):
        visited = set()
        stack = [start]
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                stack.extend(set(G[vertex]) - visited)
        return len(visited)
    
    return _DFS_node_count(G) == len(G.nodes())

def is_k33(G):
    if len(G.nodes()) != 6 or len(G.edges()) != 9:
        return False
    else:
        if nx.bipartite.is_bipartite(G):
            if len(nx.bipartite.sets(G)[0]) == 3:
                return True
        return False

def is_k5(G):
    if len(G.nodes()) != 5:
        return False
    else:
        for n in G.nodes():
            if len(G[n]) != 4:
                return False
        return True
    
def find_planarity(G):
    global it
    
    planar = True
    offending_subgraph = None

    # Optimization step:
    # Remove nodes from graph with edge count > 1 and assign to new graph (don't alter original)
    outdeg = list(G.degree())
    #print(outdeg)
    #print(G.edges())
    to_keep = []
    for n in outdeg:
        if n[1] > 1:
            to_keep.append(n[0])
    graph = G.subgraph(to_keep)

    num_nodes = len(graph.nodes())
    num_edges = len(graph.edges())

    it = 0
    
    for n in range(5, num_nodes + 1):
        for subgraph_nodes in itertools.combinations(graph.nodes(), n):
            if nx.connected.is_connected(graph.subgraph(subgraph_nodes)):
                subgraph = graph.subgraph(subgraph_nodes)
                for k in range(9, len(subgraph.edges()) + 1):
                    for subgraph_edges in itertools.combinations(subgraph.edges(), k):
                        subsubgraph = nx.Graph(subgraph_edges)
                        # nx.draw(subsubgraph)
                        # plt.show()
                        if nx.connected.is_connected(subsubgraph):
                            rr = smooth(subsubgraph)
                            if rr != None:
                                planar = False
                                offending_subgraph = subsubgraph
                                print("Iterations (actual):", it)
                                return planar, offending_subgraph, rr[1]
    
    return planar, offending_subgraph, it



def node_smoothing(G: nx.Graph, n: int):
    if n not in G.nodes():
        raise ValueError("n is not in G")
    
    if len(G[n]) != 2:
        return G
    else:
        l = list(G[n])
        G.remove_edge(n, l[0])
        G.remove_edge(n, l[1])
        G.add_edge(l[0], l[1])
        G.remove_node(n)
    return G

def smooth(G: nx.Graph):
    while True:
        if len(G.nodes()) <= 4:
            return None
        for n in G.nodes():
            t = node_smoothing(G.copy(), n)
            if not nx.is_isomorphic(t, G):
                G = t
                break
        else:
            break
        
    if len(G.nodes()) == 5:
        return (G.nodes(), 0) if is_k5(G) else None
    if len(G.nodes()) == 6:
        if is_k33(G):
            # nx.draw(G)
            # plt.show()
            return (G.nodes(), 1)
    return None

def rec_smooth(G: nx.Graph):
    global it
    #print(len(G.nodes()))
    if len(G.nodes()) <= 4:
        return None
    if len(G.nodes()) == 5:
        return (G.nodes(), 0) if is_k5(G) else None
    if len(G.nodes()) == 6:
        if is_k33(G):
            # nx.draw(G)
            # plt.show()
            return (G.nodes(), 1)
    #print(1)
    for n in G.nodes():
        # nx.draw(node_smoothing(G.copy(), n))
        # plt.show()
        if not nx.is_isomorphic(node_smoothing(G.copy(), n), G):
            t = rec_smooth(node_smoothing(G.copy(), n))
            if t != None:
                return t

