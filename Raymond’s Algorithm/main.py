from threading import Timer
import sys


class Node:
    def __init__(self, id: int):
        self.id: int = id
        self.id_representative: int = self.id + 1  # id to represent this node in prints
        self.parent = None  # pointer to parent node
        self.local_queue: list = list()  # collect nodes whom want enter to CS
        self.token: bool = False  # has node token? token is one in ALL program
        self.is_in_CS: bool = False  # is node is in CS?
        self.time_in_CS: float = 2.0  # how many time node will be in CS
        self.timer: Timer = Timer(self.time_in_CS, self.exit_from_CS)  # timer will simulate operation in CS by node

    def __str__(self):
        return 'Node with id:' + str(self.id_representative) + ' | id parent node:' +\
            str(self.parent.id_representative if self.parent is not None else None) +\
            ' | local queue:' + str([node.id_representative for node in self.local_queue]) +\
            ' | has token:' + str(self.token) + ' | is in CS:' + str(self.is_in_CS)

    def remove_one_from_local_queue(self):
        """
        Remove first node from local queue and return him.
        :return: Node
        """

        next_node: Node = list(self.local_queue)[0]
        self.local_queue.remove(next_node)

        return next_node

    def send_request_to_parent(self):
        """
        Save this requesting node to parent's local queue.
        """

        if self not in self.parent.local_queue:
            self.parent.local_queue.append(self)
            print('Node with id', self.parent.id_representative, 'has received a request from his child node with id',
                  self.id_representative)
            print(tree)

    def enter_to_CS(self):
        """
        Node enter to CS.
        Operation in CS is time-consuming, so to simulate this node will not be available for a few seconds.
        """

        # print info
        print()
        print('Node with id', self.id_representative, 'has just enter to CS. The time operation in CS:',
              self.time_in_CS, 'sec')
        print(tree)

        self.is_in_CS = True  # node has just enter to CS
        self.timer.start()  # start timer for this node

    def exit_from_CS(self):
        """
        Node is outgoing from CS. Print info and receive the token to suitable node.
        """

        # print info
        print('Node with id', self.id_representative, 'has just left CS. His local queue:',
              [node.id_representative for node in self.local_queue])
        print(tree)

        if len(self.local_queue) > 0:  # if node has participants in local queue
            self.receive_token_down(self.remove_one_from_local_queue())  # send the token to first from local queue
        else:
            self.receive_token_up(self.parent)  # return the token to parent

    def receive_token_down(self, node):
        """
        Transfer the token to selected child node.
        Print info and check local queue for selected node.
        :param node: Node
        """

        # transfer the token
        self.token = False
        node.token = True

        # print info
        print('Node with id', self.id_representative, 'has given the token to his a child node with id',
              node.id_representative, '. Preview for local queue\'s node with id', node.id_representative,
              [node.id_representative for node in node.local_queue])
        print(tree)

        if len(node.local_queue) > 0:  # if node has participants in local queue
            node.receive_token_down(node.remove_one_from_local_queue())  # send the token to first from local queue
        else:
            node.enter_to_CS()  # node has privileges to enter to CS

    def receive_token_up(self, node):
        """
        Transfer the token to parent from selected node.
        Print info and check parent's local queue.
        :param node: Node
        """

        # transfer the token
        self.token = False
        node.token = True

        # print info
        print('Node with id', self.id_representative, 'has returned the token to his a parent node with id',
              node.id_representative)
        print(tree)

        if len(node.local_queue) > 0:  # if node has participants in local queue
            node.receive_token_down(node.remove_one_from_local_queue())  # send the token to first from local queue
        else:
            if node.parent is not None:  # node has a parent
                node.receive_token_up(node.parent)
            else:  # this node is a root
                return


class Tree:
    def __init__(self):
        self.nodes = []  # nodes in tree
        self.want_enter_to_cs = {}  # nodes whom want enter to CS

    def queuing_requests(self):
        """
        Send requests to all nodes.
        """

        for node in self.want_enter_to_cs:
            self.send_requests_to_root(node)

    def send_requests_to_root(self, node: Node):
        """
        Send requests to queuing to root node in a direct path for node
        :param node: node
        """

        # if node is root then break the recursion
        if node.parent is None:
            return

        node.send_request_to_parent()  # add node to parent local queue
        self.send_requests_to_root(node.parent)  # recursion for a parent node

    def __str__(self):
        info = '------------------- struct info -------------------\n'
        for node in self.nodes:
            info += str(node)
            info += '\n'
        info += '------------------- end -------------------'

        return info


if __name__ == '__main__':
    filename = 'graph1'
    sys.stdout = open(filename + '_output1.txt', 'w')  # save output in console to file

    """
    neighbour matrix in file must contains 0 and 1 separated with commas with except the last column
    for all columns in rows except last column:
        0 - node has not parent for n node
        1 - node has a parent for n node
    last column says which nodes want enter to CS and number greater than 0 are order for entering to CS
    """
    with open(filename + '.txt', 'r') as f:
        neighbour_matrix = [[int(num) for num in line.split(',')] for line in f]
    print('graph (neighbour matrix):', neighbour_matrix)

    # create tree structure
    tree = Tree()

    # gather all nodes from neighbour matrix
    for index, connections in enumerate(neighbour_matrix):
        # create node
        node = Node(index)

        for i, connection in enumerate(connections):
            # gather nodes whom want enter to CS
            if i == len(connections) - 1 and connection != 0:
                tree.want_enter_to_cs[connection] = node
                break

            # tag a parent for this node
            if connection != 0:
                node.parent = i

        tree.nodes.append(node)

    # remember pointer to object's node rather than node's id in a reference to parent
    for node in tree.nodes:
        node.parent = tree.nodes[node.parent] if node.parent is not None else None

    # sort nodes whom want enter to CS
    tree.want_enter_to_cs = sorted(tree.want_enter_to_cs.items())

    # nodes whom want enter to CS are list with a key to sort and node. remember only the node from sorted nodes
    tree.want_enter_to_cs = [node[1] for node in tree.want_enter_to_cs]

    # requirements from task - first node is in CS
    tree.nodes[0].token = True
    tree.nodes[0].enter_to_CS()

    # queuing requests from all nodes
    tree.queuing_requests()
