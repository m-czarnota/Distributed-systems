import threading
import random
import sys


class ProcessController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.process: list = []  # process controller stores processs in all system
        self.is_deadlock: bool = False  # flag if deadlock has been detected
        self.process_keys: list = []  # drawn keys for processs in order to eliminate replicas

    def build_process(self, graph) -> None:
        """
        Build processs in the system from neighbour matrix and keep them.
        :param graph:
        :return:
        """
        # for each row in neighbour matrix
        for i, connections in enumerate(graph):
            # create a process
            process = Process(i + 1, self)

            # for each connection for this process
            for connection_index, connection in enumerate(connections):
                if connection == 1:  # if the position is required by this process
                    process.required_processes.append(connection_index)  # add index to

            # keep this process
            self.process.append(process)

        # replace indexes in required processes on pointers to processs
        for i, process in enumerate(self.process):
            for j, connection in enumerate(process.required_processes):
                process.required_processes[j] = self.process[connection]

    def draw_keys(self) -> dict:
        """
        Draw unique private and public key for process, save them and returned them.
        :return:
        """
        private_key = random.randint(0, max_value)
        # public_key = random.randint(0, max_value)

        while private_key in self.process_keys:
            private_key = random.randint(0, max_value)

        # while public_key in self.process_keys:
        #     public_key = random.randint(0, max_value)

        self.process_keys.append(private_key)
        # self.process_keys.append(public_key)

        return {
            'private_key': private_key,
            'public_key': private_key
        }

    def run(self) -> None:
        """
        Run all processs.
        If deadlock is detected then algorithm is over and all processs will be terminate.
        :return:
        """
        # start each process
        for process in self.process:
            process.start()

        # wait to detecting deadlock
        while self.is_deadlock is False:
            pass

        # after detecting deadlock terminate each process
        for process in self.process:
            process.join()

    def __str__(self):
        info = "\n---------------------- Processes info ----------------------\n"
        for process in self.process:
            info += str(process)
            info += '\n'
        info += "---------------------- End info ----------------------\n"
        return info


class Process(threading.Thread):
    def __init__(self, id: int, process_controller: ProcessController):
        threading.Thread.__init__(self)

        self.id: int = id
        self.is_blocked: bool = False  # flag means if process is blocked by other process
        self.controller: ProcessController = process_controller  # reference to ProcessController
        self.required_processes: list = []  # list of all required process

        # drawing keys
        keys = self.controller.draw_keys()
        self.private_key = keys['private_key']
        self.public_key = keys['public_key']

    def run(self):
        """
        Run process. Apply block rule with required processes. Delay start transmit rule.
        :return:
        """
        # apply block rule for this process with all required processes.
        self.block_process()

        # while deadlock is not detected
        while self.controller.is_deadlock is False:
            # for each required process by this process
            for required_process in self.required_processes:
                self.change_keys_with_process(required_process)  # apply transmit rule
                s_print(self.controller)  # print info about all nodes
                self.is_deadlock_with_process(required_process)  # check if deadlock is detected with required process

    def block_process(self):
        """
        Block this process with any required process by this process.
        :return:
        """
        # for each required process by this process
        for required_process in self.required_processes:
            maximum = max([required_process.public_key, self.public_key]) + 1  # calculate maximum
            info = 'Block phase: process ' + str(self.id) + ' is blocking by process ' + str(required_process.id) + \
                   ' | block rule value: ' + str(maximum)  # gather info

            # set keys for this process
            self.public_key = maximum
            self.private_key = maximum
            self.is_blocked = True

            # print info
            s_print(info + ' ' + str(self.controller))

    def change_keys_with_process(self, required_process):
        """
        Apply transmit rule for this process and required process by this process.
        :param required_process:
        :return:
        """
        # gather info
        info = 'Transmit phase: process ' + str(self.id) + ' with process ' + str(required_process.id)

        # if public key from required process is greater than public key from this process
        if required_process.public_key > self.public_key:
            self.public_key = required_process.public_key  # apply transmit rule
            info += '\nTransmit rule has been applied for process ' + str(self.id)  # gather info

        # print info
        s_print(info)

    def is_deadlock_with_process(self, required_process) -> bool:
        """
        Check if conditions to occur deadlock is happening.
        :param required_process:
        :return:
        """
        if self.public_key == self.private_key and required_process.public_key == self.public_key:
            # print info
            s_print('DEADLOCK is detected with processes:\n', self, '\n', required_process)

            # deadlock is detected
            self.controller.is_deadlock = True
            return True

        # deadlock is not detected
        return False

    def __str__(self):
        threading.Thread.__str__(self)
        return 'Process with id: ' + str(self.id) + ' | public key: ' + str(self.public_key) + \
               ' | private key: ' + str(self.private_key) + ' | is blocked: ' + str(self.is_blocked) + \
               ' | required processes: ' + str([required_process.id for required_process in self.required_processes])


def s_print(*a, **b):
    """Thread safe s_print function"""
    with s_print_lock:
        print(*a, **b)


if __name__ == '__main__':
    # initial values
    max_value = 100
    filename = 'graph1'
    s_print_lock = threading.Lock()  # variable to save printing with using threads

    # save output in console to file
    sys.stdout = open(filename + '_output3' + '.txt', 'w')

    # read graph as neighbour matrix
    with open(filename + '.txt', 'r') as f:
        neighbour_matrix = [[int(num) for num in line.split(',')] for line in f]
    print('graph (neighbour matrix):', neighbour_matrix)  # print graph in console

    # main algorithm
    processController = ProcessController()  # create ProcessController
    processController.build_process(neighbour_matrix)  # create processes from graph
    print(processController)  # print info about created processes
    processController.start()  # start algorithm
