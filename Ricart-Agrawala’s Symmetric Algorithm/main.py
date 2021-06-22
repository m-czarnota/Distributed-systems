import random
import time


class Node:
    def __init__(self, id: int):
        self.id = id
        self.requests = set()  # list of requests to other nodes
        self.waiting_requests = set()  # list of request's nodes which is waiting on response from this node
        self.responses_from_nodes = set()  # set nodes whom has given response to this node
        self.is_in_CS = False  # flag saying if node is in CS currently
        self.is_served = False  # flag saying if node has been in CS


class Request:
    def __init__(self):
        self.timestamp = random.uniform(0, 1)
        self.status = 0
        self.node = None  # node's id as pointer


if __name__ == '__main__':
    """
    neighbour matrix in file must contains 0 and 1 separated with commas
    0 - node will not send request to selected node
    1 - node will send request to selected node
    because it will be Ricart–Agrawala Algorithm then all node must send to every other nodes request
    neighbour matrix is a quite clear saying which node wants to enter to CS
    """
    with open('graph2.txt', 'r') as f:
        neighbour_matrix = [[int(num) for num in line.split(',')] for line in f]
    print('graph (neighbour matrix):', neighbour_matrix)


    # variables
    nodes = []  # all nodes from neighbour matrix
    counter = 0  # global shared variable used in CS
    CS_busy = None  # pointer on node whom is in CS currently

    # gather all nodes from neighbour matrix and create requests to other nodes
    for index, connections in enumerate(neighbour_matrix):
        # create node
        node = Node(index)

        # create requests for this node
        for i, connection in enumerate(connections):
            if connection == 1:
                request = Request()
                request.node = i

                node.requests.add(request)

        nodes.append(node)

    while(True):
        # for each node
        for i, node in enumerate(nodes):
            # print('node ' + str(node.id) + ' has ' + str(len(node.requests)))

            # CRITICAL SECTION - if node is now in CS then do something operations
            if node.is_in_CS is True and node.is_served is False and CS_busy == node:
                counter += 1

                # node has ended doing his operations, he will go out from CS
                if counter % 3 == 0 and counter != 0:
                    node.is_in_CS = False
                    node.is_served = True  # node has been in CS, it is not necessary to enter again

                    # send reply to all nodes who has asked this node about response
                    print('node', node.id, 'is going out from CS. nodes who is waiting for reply from this node', [waiting_request.id for waiting_request in node.waiting_requests])
                    for node_to_reply in node.waiting_requests:
                        node_to_reply.responses_from_nodes.add(nodes[i])

                    CS_busy = None  # CS is available

            # check if all nodes have been serving
            all_nodes_served = True
            for node_ in nodes:
                if node_.is_served is False:
                    all_nodes_served = False
                    break

            if all_nodes_served is True:
                exit(0)

            if node.is_served is False and node.is_in_CS is False:
                # if node has not received reply from all requested nodes (avoid doing below loop another time)
                if node.responses_from_nodes != node.requests:
                    # for each request in selected node
                    for j, request in enumerate(node.requests):
                        # send request
                        if len(nodes[request.node].requests) == 0:  # check if asked nodes have not own other requests
                            # if he have not then add to list index of requested node as reply
                            node.responses_from_nodes.add(nodes[request.node])
                            nodes[request.node].is_served = True  # this node is not waiting for any other response
                        elif nodes[request.node].is_in_CS is True:  # check if asked nodes is in CS
                            # if he is then save asking node
                            nodes[request.node].waiting_requests.add(node)
                            print('node', node.id, 'is waiting for response from node', nodes[request.node].id, 'because node', nodes[request.node].id, 'is in CS')

                        # for each request in requested node
                        for k, request_ in enumerate(nodes[request.node].requests):
                            # check if requested node wants response from currently asking
                            if request_.node == node.id:  # if yes, then compare requests' timestamps
                                # if requested node has lesser timestamp than currently asking
                                if request_.timestamp < request.timestamp:
                                    nodes[request_.node].responses_from_nodes.add(nodes[request.node])
                                else:
                                    nodes[request.node].responses_from_nodes.add(nodes[request_.node])

                                # it is not necessary to continue above loop, because each node is in requests only once
                                break

                # ALLOW NODE TO ENTER TO CRITICAL SECTION - if node has received reply from all requested nodes
                if len(node.responses_from_nodes) == len(node.requests) and len(node.requests) > 0 and CS_busy is None:
                    # then this node is allowed to income to CS
                    node.is_in_CS = True
                    CS_busy = node  # CS is busing by this node

                    # print status list
                    print('\nnode', node.id, 'is allowed to enter to CS. his received responses:', [requested_node.id for requested_node in node.responses_from_nodes])
