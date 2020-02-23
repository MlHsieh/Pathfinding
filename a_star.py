# pylint: disable=missing-module-docstring, invalid-name, missing-function-docstring
import random
import math
import typing
import heapq

import pygame

class Node:
    """Hold information of a node. """
    def __init__(
            self,
            walkable: bool,
            grid_postion: typing.List[int],
            position: typing.List[float],
            size: int
    ):
        self.walkable = walkable
        self.col = grid_postion[0]
        self.row = grid_postion[1]
        self.position = position
        self.size = size
        self.gcost = 0
        self.hcost = 0
        self.parent = None  # Previous node on the path

    def draw(self, screen, color=pygame.Color(255, 255, 255)):
        """ Draw itself onto screen."""
        pygame.draw.rect(
            screen, color,
            (self.position[0], self.position[1], self.size, self.size)
        )

    def fcost(self):
        """ total movement required from start node to target node"""
        return self.gcost + self.hcost

    def dist(self, other: 'Node'):
        """ Calculate the distance between self and other.
            Since diagonal path is not allowed, the distance is dx + dy.
        """
        return abs(self.row - other.row) + abs(self.col - other.col)

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
    """ Hold information of all the nodes.
        Nodes are stored in a 1 dimensional list.
    """
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
        for _ in range(math.floor(self.cols*self.rows/1.5)):
            self.nodes[
                random.randint(2, self.cols*self.rows-3)
            ].walkable = False

    def find_neighbors(self, node: Node):
        """Find neighbor of node. (no diagonal) """
        index = node.col*self.rows + node.row
        neighbors_index = [index+self.rows, index-self.rows]
        # if node.row != 0:
        #     neighbors_index.append(index-1)
        # if node.row != self.rows-1:
        #     neighbors_index.append(index+1)
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

    def draw(self, screen: pygame.display):
        """ Draw all the nodes. """
        for n in self.nodes:
            if n.walkable:
                n.draw(screen)
            else:
                n.draw(screen, (0, 0, 0))


class AStarPathFinding:
    """ A* pathfinding algorithm
        Start from top left corner to bottom right corner.
        Obstacles are generated randomly.
    """
    def __init__(self):
        self.grid = Grid(100, 50, 10, 1)
        self.start = self.grid.nodes[0]
        self.target = self.grid.nodes[self.grid.cols*self.grid.rows-1]
        self.open = [self.start] # Nodes to be evaluated
        self.close = set()  # Nodes already evaluated
        self.path_found = False

    def update(self):
        if self.open and not self.path_found:
            # Start from node in open with the lowest fcost
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

    def draw(self, screen: pygame.display):
        if not self.path_found:
            for n in self.open:
                n.draw(screen, pygame.Color(0, 200, 0))
            for n in self.close:
                n.draw(screen, pygame.Color(200, 0, 0))
            self.start.draw(screen, pygame.Color(0, 150, 200))
            self.target.draw(screen, pygame.Color(0, 150, 200))
        else:
            # Draw the path
            n = self.target
            while n.parent is not None:
                n.draw(screen, pygame.Color(0, 150, 200))
                n = n.parent


def main():
    path = AStarPathFinding()

    # Initialize
    pygame.init()
    screen = pygame.display.set_mode((path.grid.screen_w, path.grid.screen_h))
    screen.fill(pygame.Color(80, 80, 80))
    path.grid.draw(screen)

    # Start the event loop
    run = True
    while run:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_F4 and
                  (key[pygame.K_LALT] or key[pygame.K_RALT])
                 ):
                run = False

        path.draw(screen)
        path.update()

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
