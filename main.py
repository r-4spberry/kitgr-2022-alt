import sys
import threading
it = 0
from tkinter import *
from tkinter import messagebox
import pygame
import networkx as nx
from planarity import find_planarity
pygame.init()

class Node:
    id = 0
    def __init__(self, x, y, color = (200, 0, 0)):
        self.x = x
        self.y = y
        self.color = color
        self.id = Node.id
        Node.id += 1
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 10, 0)
        
class Edge:
    def __init__(self, node1, node2, color = (0, 0, 0)):
        self.node1 = node1
        self.node2 = node2
        self.color = color
    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.node1.x, self.node1.y), (self.node2.x, self.node2.y), 4)
    def __eq__(self, other):
        return (self.node1 == other.node1 and self.node2 == other.node2) or (self.node1 == other.node2 and self.node2 == other.node1)
    def distance_to_point(self, x, y):
        return abs((self.node2.y - self.node1.y) * x - (self.node2.x - self.node1.x) * y + self.node2.x * self.node1.y - self.node2.y * self.node1.x) / ((self.node2.y - self.node1.y) ** 2 + (self.node2.x - self.node1.x) ** 2) ** 0.5

def pygame_graph_to_networkx_graph(nodes, edges):
    networkx_graph = nx.Graph()
    for node in nodes:
        networkx_graph.add_node(node.id)
    for edge in edges:
        networkx_graph.add_edge(edge.node1.id, edge.node2.id)
    return networkx_graph

def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Graph editor")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    clock = pygame.time.Clock()
    nodes = []
    edges = []
    node_selected = False
    node_selected_index = -1
    node_dragged = False
    node_dragged_index = -1
    is_editing = True
    is_looking = False
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if is_editing:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #print(event.button)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if event.button == 1:
                        for i in range(len(nodes)):
                            if (abs(nodes[i].x - mouse_x) < 15 and abs(nodes[i].y - mouse_y) < 15):
                                node_selected = True
                                node_selected_index = i
                                break
                        else:
                            node_selected = False
                            nodes.append(Node(mouse_x, mouse_y))
                    if event.button == 3:
                        for i in range(len(nodes)):
                            if (abs(nodes[i].x - mouse_x) < 15 and abs(nodes[i].y - mouse_y) < 15):
                                node_dragged = True
                                node_dragged_index = i
                                break
                    #print(node_selected)
                    if event.button == 2:
                        for i in range(len(nodes)):
                            if (abs(nodes[i].x - mouse_x) < 15 and abs(nodes[i].y - mouse_y) < 15):
                                j = 0
                                while j < len(edges):
                                    if edges[j].node1 == nodes[i] or edges[j].node2 == nodes[i]:
                                        del edges[j]
                                    else:
                                        j += 1
                                        
                                del nodes[i]
                                break
                        else:
                            for i in range(len(edges)):
                                if edges[i].distance_to_point(mouse_x, mouse_y) < 5:
                                    del edges[i]
                                    break
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    #print(node_selected)
                    if event.button == 1:
                        if node_selected:
                            for i in range(len(nodes)):
                                if (abs(nodes[i].x - mouse_x) < 15 and abs(nodes[i].y - mouse_y) < 15):
                                    #print(node_selected_index, )
                                    if i != node_selected_index:
                                        new_edge = Edge(nodes[node_selected_index], nodes[i])
                                        for edge in edges:
                                            if edge == new_edge:
                                                break
                                        else:
                                            edges.append(new_edge)
                                    break
                            node_selected = False
                    if event.button == 3:
                        node_dragged = False
            
        #draw nodes and edges
        screen.blit(background, (0, 0))
        if node_selected:
            pygame.draw.line(screen, (0, 0, 0), (nodes[node_selected_index].x,
                                                 nodes[node_selected_index].y), pygame.mouse.get_pos(), 4)
        if node_dragged:
            nodes[node_dragged_index].x, nodes[node_dragged_index].y = pygame.mouse.get_pos()
        for i in range(len(edges)):
            edges[i].draw(screen)
        for i in range(len(nodes)):
            nodes[i].draw(screen)
        
        #add text "Press Enter to continue.
        font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
        text = font.render("Press Enter to process graph.", True, (0, 0, 0))
        screen.blit(text, (0, 0))
        
        pygame.display.flip()
        
        #if Enter is pressed, check graph with find_planarity
        if event.type == pygame.KEYDOWN and is_editing:
            if event.key == pygame.K_RETURN:
                
                screen.blit(background, (0, 0))
                if node_selected:
                    pygame.draw.line(screen, (0, 0, 0), (nodes[node_selected_index].x,
                                                        nodes[node_selected_index].y), pygame.mouse.get_pos(), 4)
                if node_dragged:
                    nodes[node_dragged_index].x, nodes[node_dragged_index].y = pygame.mouse.get_pos()
                for i in range(len(edges)):
                    edges[i].draw(screen)
                for i in range(len(nodes)):
                    nodes[i].draw(screen)
                
                #add text "Press Enter to continue.
                text = font.render("Processing...", True, (0, 0, 0))
                screen.blit(text, (0, 0))
                pygame.display.flip()
                
                is_editing = False
                is_looking = True
                G = pygame_graph_to_networkx_graph(nodes, edges)
                is_planar, subgraph, type = find_planarity(G)
                if is_planar:
                    answer = ("Graph is planar.")
                else:
                    answer = ("Graph is not planar.")
                    #print(subgraph)
                    for edge in subgraph.edges:
                        #print(edge[0], edge[1])
                        for i in range(len(edges)):
                            if edges[i].node1.id == edge[0] and edges[i].node2.id == edge[1] or edges[i].node1.id == edge[1] and edges[i].node2.id == edge[0]:
                                edges[i].color = (0, 255, 0)
                    #print(edges)
                screen.blit(background, (0, 0))
                if node_selected:
                    pygame.draw.line(screen, (0, 0, 0), (nodes[node_selected_index].x,
                                                        nodes[node_selected_index].y), pygame.mouse.get_pos(), 4)
                if node_dragged:
                    nodes[node_dragged_index].x, nodes[node_dragged_index].y = pygame.mouse.get_pos()
                for i in range(len(edges)):
                    edges[i].draw(screen)
                for i in range(len(nodes)):
                    nodes[i].draw(screen)
                
                #add text "Press Enter to continue.
                text = font.render(answer+" Press Enter to continue.", True, (0, 0, 0))

                screen.blit(text, (0, 0))
                pygame.display.flip()
                # if not is_planar:
                #     Tk().wm_withdraw() #to hide the main window
                #     messagebox.showinfo("Found!",f"Your subraph is {'K3' if type else 'K5,5'}")
                # make a thread from this:
                if not is_planar:
                    root = Tk()
                    root.withdraw()
                    messagebox.showinfo("Found!",f"Your subraph is {'K3,3' if type else 'K5'}")
                    root.destroy()
                waiting = True
                while waiting:
                    clock.tick(60)
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_RETURN:
                                waiting = False
                                break 
                while is_looking:
                    clock.tick(60)
                    pygame.display.flip()
                    for event in pygame.event.get():
                        #print(2)
                        if event.type == pygame.QUIT:
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                is_looking = False
                                is_editing = True
                                for edge in edges:
                                    edge.color = (0, 0, 0)
                                pygame.display.flip()
                                break
                waiting = True
                while waiting:
                    clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_RETURN:
                                waiting = False
                                break 
            
if __name__ == "__main__":
    main()
    G = nx.Graph([(1, 2), (2, 3), (3, 3), (4, 2), (5, 2), (6, 2), (7, 4), (8, 2), (9, 2), (10, 2), (11, 4), (12, 2)])
    # nx.draw(G)
    # plt.show()
    # is_planar, subgraph, _ = find_planarity(G)
    # print(is_planar)
    