class Graph:
    def __init__(self):
        self.neighbour_matrix = [[]]
        self.NodesCovered = []  # connected nodes with others, suitable node is right index in this array and contain array with connections
        self.visitedNodes = set()  # without repeat
        self.goodNodes = []  # array with boolean values, suitable node is right index in this array and say if node is good to be first in the graph
        self.stop = 500  # max limit for jump_counter as stop condition, prevents infinite loop
        self.jump_counter = 0  # count jumping between nodes

    def gather_connected_elements(self):
        # matrix is square, so loop on each element (A, B or E is only once in matrix)
        for node in range(len(graph.neighbour_matrix)):
            connected_nodes = []

            # loop on right row, where node is connected with itself
            for i, connection in enumerate(self.neighbour_matrix[node]):
                # if node outcome to other element
                if connection == 1:
                    connected_nodes.append(i)

            # save node connections
            self.NodesCovered.append(connected_nodes)

    # node is index
    def check_connection_node(self, node: int):
        # add 1 to jump counter
        self.jump_counter += 1

        # stop condition
        if self.jump_counter >= self.stop:
            return

        # print(node)
        # check if with this node is connected with only one other node and stop if this connection is visited
        if len(self.NodesCovered[node]) == 1 and self.NodesCovered[node][0] in self.visitedNodes:
            return

        for i, connection in enumerate(self.NodesCovered[node]):
            self.visitedNodes.add(connection)
            self.check_connection_node(connection)

    def check_connections(self):
        # each connections with other nodes is array which contains indexes to connected nodes, i - index of each node
        for i, connections in enumerate(self.NodesCovered):
            # reset all visited nodes from previous connections
            self.visitedNodes = set()
            self.jump_counter = 0

            # node is connected node with actual i node
            for j, node in enumerate(connections):
                self.visitedNodes.add(node)
                self.check_connection_node(node)

            # check if all nodes have been visited
            if len(self.visitedNodes) == len(self.neighbour_matrix):
                self.goodNodes.append(True)
            else:
                self.goodNodes.append(False)


if __name__ == '__main__':
    # neighbour matrix in file must contains 0 and 1 separated with commas (description below)
    with open('graph.txt', 'r') as f:
        neighbour_matrix = [[int(num) for num in line.split(',')] for line in f]
    print('graph (neighbour matrix):', neighbour_matrix)

    graph = Graph()

    """
    neighbour matrix, symbols:
    0 - actual element don't outcome to other element
    1 - actual element outcome to other element
    """
    graph.neighbour_matrix = neighbour_matrix

    graph.gather_connected_elements()
    print('\nconnected nodes:')
    for i, nodes in enumerate(graph.NodesCovered):
        print(i, nodes)

    graph.check_connections()
    print('\nwhich nodes will be good on first node in graph:')
    for i, nodes in enumerate(graph.goodNodes):
        print(i, nodes)
