"""
A* path finding with pygamezero
Find the shortest path from top-left corner to bottom-right corner.
Obstacles are generated randomly each time.
Numbers shown are the fcost (the total path length)

Basically the same as pygame version.
Only add the numbers.

Author: ML Hsieh
2020-2-23
"""

# pylint: disable=missing-module-docstring, invalid-name, missing-function-docstring
import random
import math
import typing
import heapq
import pgzrun

class Node:
    def __init__(
            self, walkable: bool, grid_pos: typing.List[int],
            world_pos: typing.List[float], size: int
    ):
        self.walkable = walkable
        self.position = world_pos
        self.size = size
        self.col = grid_pos[0]
        self.row = grid_pos[1]
        self.gcost = 0
        self.hcost = 0
        self.parent = None

    def fcost(self):
        return self.gcost + self.hcost

    def fill(self, color=(255, 255, 255)):
        """ Draw itself onto screen."""
        screen.draw.filled_rect(
            Rect((self.position[0], self.position[1]), (self.size, self.size)),
            color
        )

    def draw_text(self, text: str, color=(255, 255, 255)):
        screen.draw.text(
            text,
            centerx=self.position[0] + self.size/2,
            centery=self.position[1] + self.size/2,
            fontsize=30,
            color=color
        )

    def dist(self, other: 'Node'):
        dx = abs(self.col-other.col)
        dy = abs(self.row-other.row)
        if dx <= dy:
            return 14*dx + 10*(dy-dx)
        else:
            return 14*dy + 10*(dx-dy)

    def __lt__(self, other: 'Node'):
        """ Return self < other
        This function is called when using heap queue algorithms
        """
        return (self.fcost() < other.fcost() or
                (self.fcost() == other.fcost() and
                 self.hcost < other.hcost
                )
               )

class Grid:
    """ Hold information of all the nodes. """
    def __init__(self, cols, rows, grid_size=55, line_width=3):
        self.nodes = []
        self.grid_size = grid_size
        self.line_width = line_width
        self.cols = cols
        self.rows = rows
        self.screen_w = ((self.grid_size+self.line_width) * self.cols
                         + self.line_width)
        self.screen_h = ((self.grid_size+self.line_width) * self.rows
                         + self.line_width)
        self.create_grid()
        self.generate_obstacles()

    def create_grid(self):
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                self.nodes.append(
                    Node(True, [x, y], [
                        self.line_width*(x+1) + self.grid_size*x,
                        self.line_width*(y+1) + self.grid_size*y
                    ], self.grid_size)
                )

    def generate_obstacles(self):
        for _ in range(math.floor(self.rows*self.cols/2.5)):
            self.nodes[
                math.floor(random.random()*(self.rows*self.cols-2) + 1)
            ].walkable = False

    def find_neighbors(self, node: Node):
        index = self.rows*node.col + node.row
        neighbors_index = [index+self.rows, index-self.rows]
        if node.row != 0:
            neighbors_index.extend(
                [index-self.rows-1, index-1, index+self.rows-1]
            )
        if node.row != self.rows-1:
            neighbors_index.extend(
                [index-self.rows+1, index+1, index+self.rows+1]
            )
        neighbors = []
        for i in neighbors_index:
            if 0 <= i < self.rows*self.cols:
                neighbors.append(self.nodes[i])
        return neighbors

    def draw(self):
        for n in self.nodes:
            if n.walkable:
                n.fill()
            else:
                n.fill((0, 0, 0))

class PathFinding:
    """ A star path finding """
    def __init__(self):
        self.grid = Grid(30, 15, 40, 3)
        self.start = self.grid.nodes[0]
        self.target = self.grid.nodes[self.grid.cols*self.grid.rows-1]
        self.open = [self.start] # Nodes to be evaluated
        self.close = set()  # Nodes already evaluated
        self.path_found = False

    def update(self):
        if self.open and not self.path_found:
            # Start from node in open with the lowest cost
            current_node = heapq.heappop(self.open)
            self.close.add(current_node)

            # Path found
            if current_node == self.target:
                self.path_found = True
                return

            # Update neighbors
            neighbors = self.grid.find_neighbors(current_node)
            for n in neighbors:
                if n not in self.close and n.walkable:
                    new_gcost = current_node.gcost + n.dist(current_node)
                    if n not in self.open or new_gcost < n.gcost:
                        n.gcost = new_gcost
                        n.hcost = n.dist(self.target)
                        n.parent = current_node
                    if n not in self.open:
                        heapq.heappush(self.open, n)

    def draw(self):
        self.grid.draw()
        for n in self.open:
            n.fill((0, 200, 0))
            n.draw_text(str(n.fcost()), (0, 0, 0))
        for n in self.close:
            n.fill((200, 0, 0))
            n.draw_text(str(n.fcost()), (0, 0, 0))
        if self.path_found:
            n = self.target
            while n is not None:
                n.fill((0, 150, 200))
                n = n.parent
        self.start.fill((0, 150, 200))
        self.start.draw_text('A')
        self.target.fill((0, 150, 200))
        self.target.draw_text('B')

path = PathFinding()
HEIGHT = path.grid.screen_h
WIDTH = path.grid.screen_w

def draw():
    screen.clear()
    path.draw()

def update():
    path.update()

pgzrun.go()

