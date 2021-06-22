import time
from threading import Timer
import random
import sys
import json
from tabulate import tabulate


class SiteController:
    def __init__(self):
        self.sites: list = []  # sites in system
        self.sites_matrix: dict = {}  # info gathered from all sites to find deadlock
        self.sites_matrix_str: dict = {}  # info gathered from all sites to display info about them in matrix

    def build_matrix(self):
        """
        Build matrix with processes and resources from all sites.
        Build matrix to find deadlock and another matrix to display info about sites.
        :return:
        """
        # for each site in all sites
        for site in self.sites:
            # for each resource in this site
            for resource in site.resources:
                # set a proper key in dictionaries for matrices
                resource_key_str = 'R' + str(resource.id)  # key for the matrix to display info about sites
                self.sites_matrix_str[resource_key_str] = {}
                self.sites_matrix[resource] = {}

                # we have to check all processes from each site for this resource
                for site2 in sites:
                    # for each process from each site
                    for process in site2.processes:
                        # set a proper key in dictionaries for matrices
                        process_key_str = 'P' + str(process.id)  # key for the matrix to display info about sites

                        # set initial value for matrices - default 0
                        self.sites_matrix_str[resource_key_str][process_key_str] = 0
                        self.sites_matrix[resource][process] = 0

                        # if resource is required by this process
                        if resource in process.required_resources:
                            self.sites_matrix[resource][process] = -1  # this process is waiting for this resource
                            self.sites_matrix_str[resource_key_str][process_key_str] = -1  # the same like above
                        elif process.actual_using_resource == resource:  # if resource is used by this process
                            self.sites_matrix[resource][process] = 1  # this process is using the indicated resource
                            self.sites_matrix_str[resource_key_str][process_key_str] = 1  # the same like above

    def search_deadlock(self) -> bool:
        """
        Search deadlock in matrix.
        If deadlock is detected, then end his work.
        :return:
        """
        # for each resource from all sites
        for resource_pointer in self.sites_matrix:
            # for each process from all sites which are connected with this resource
            for process_pointer in self.sites_matrix[resource_pointer]:
                # if deadlock has been detected
                if self.check_deadlock(resource_pointer, process_pointer, process_pointer, 0) is True:
                    print('Find deadlock', 'END OF THIS ALGORITHM')  # print info
                    print('Process with id', process_pointer.id, 'with resource', resource_pointer.id,
                          'are involved in cycle')
                    return True  # end this algorithm

        print('Deadlock not detected')
        return False

    def check_deadlock(self, resource_pointer, process_pointer, first_process=None, jump_counter: int = 0) -> bool:
        """
        Recursion function. If resource is used by process, then check all required resources for this process and check
        them.
        Remember first calling with original process with pointer to the first process.
        With first calling pointer to the process and pointer to the first process are the same, but jump counter is 0.
        When the situation repeats itself then jump counter will be greater than 0 and deadlock will be detected.
        :param resource_pointer: Resource
        :param process_pointer: Process
        :param first_process: Process
        :param jump_counter: int
        :return: bool
        """
        # if pointer to the this process is the same as pointer to the first process and function is calling with these parameters is repeated
        if process_pointer == first_process and jump_counter > 0:
            return True  # deadlock has been detected

        # increase jump counter for this first process
        jump_counter += 1

        # if this process is using this resource
        if self.sites_matrix[resource_pointer][process_pointer] == 1:
            # we have to check all required resources by this process
            for required_resource in process_pointer.required_resources:
                for process in self.sites_matrix[required_resource]:
                    # if deadlock has been detected
                    if self.check_deadlock(process_pointer.required_resources[0], process, first_process, jump_counter):
                        return True  # end loops

        # deadlock has not been detected
        return False

    def drawing(self):
        processes = list(self.sites_matrix[list(self.sites_matrix.keys())[0]].keys())
        resources = list(self.sites_matrix.keys())
        for process in processes:
            required_resources_counter = random.randint(0, len(resources))
            for required_resource in range(required_resources_counter):
                process.required_resources.append(resources[random.randint(0, len(resources) - 1)])

            if random.randint(1, 10) > 6 and len(process.required_resources) > 0:
                drawn_actual_using_resource = process.required_resources[0]
                while drawn_actual_using_resource in process.required_resources:
                    drawn_actual_using_resource = resources[random.randint(0, len(resources) - 1)]
                process.actual_using_resource = drawn_actual_using_resource
                process.is_blocked = True
                drawn_actual_using_resource.is_blocked = True

        self.build_matrix()

    def __str__(self):
        info = []
        headers = ['R/P']

        for resource in self.sites_matrix_str:
            for process in self.sites_matrix_str[resource]:
                headers.append(process)
            break

        for i, resource in enumerate(self.sites_matrix_str):
            info.append([self.sites_matrix_str[resource][process] for process in self.sites_matrix_str[resource]])
            info[i].insert(0, resource)

        info = tabulate(info, headers=headers, tablefmt='orgtbl')

        return info


class Site:
    def __init__(self, id: int):
        self.id: int = id
        self.resources: list = []  # list of resources' site
        self.processes: list = []  # list of processes' site

    def __str__(self):
        return 'Site with id: ' + str(self.id) + ' | resources list: ' + \
               str([resource.id for resource in self.resources]) + ' | process list: ' + \
               str([process.id for process in self.processes])


class Process:
    def __init__(self, id: int):
        self.id: int = id
        self.required_resources: list = []  # list of required resources by this process
        self.is_blocked: bool = False  # flag if process is blocked - process is doing operation
        self.actual_using_resource = None  # pointer to resource used by this process currently

    def __str__(self):
        return 'Process with id: ' + str(self.id) + ' | is blocked: ' + str(self.is_blocked) + \
               ' | required resources: ' + str([resource.id for resource in self.required_resources])


class Resource:
    def __init__(self, id: int):
        self.id: int = id
        self.is_blocked: bool = False  # flag if resource is blocked

    def __str__(self):
        return 'Resource with id: ' + str(self.id) + ' | is blocked: ' + str(self.is_blocked)


if __name__ == '__main__':
    # numbers
    count_sites = 3  # how many nodes will be in algorithm
    count_processes_per_site = 2  # how many process will be each node in algorithm
    count_resources_per_site = 3  # how many resources will be each node in algorithm

    for k in range(10):
        # counters to suitable id
        counter_processes_per_site = 1  # global counter for processes
        counter_resources_per_site = 1  # global counter for resources

        # generate nodes with process and resources for them
        sites = []
        for i in range(count_sites):
            # create node
            site = Site(id=i + 1)

            # create process for above node
            for j in range(count_processes_per_site):
                process = Process(id=counter_processes_per_site)
                site.processes.append(process)
                counter_processes_per_site += 1

            # create resource for above node
            for j in range(count_resources_per_site):
                resource = Resource(id=counter_resources_per_site)
                site.resources.append(resource)
                counter_resources_per_site += 1

            # add created node to global list
            sites.append(site)

        site_controller = SiteController()
        site_controller.sites = sites
        site_controller.build_matrix()
        site_controller.drawing()

        # # set required resources and actual using resource for process
        # sites[2].processes[1].required_resources.append(sites[1].resources[0])
        # sites[2].processes[1].actual_using_resource = sites[1].resources[1]
        # sites[2].processes[1].is_blocked = True
        # sites[1].resources[1].is_blocked = True
        #
        # # set required resources and actual using resource for process
        # sites[1].processes[1].required_resources.append(sites[1].resources[1])
        # sites[1].processes[1].actual_using_resource = sites[1].resources[0]
        # sites[1].processes[1].is_blocked = True
        # sites[1].resources[0].is_blocked = True
        #
        # # control info
        # print('Process with id', sites[2].processes[1].id, 'is working with resource with id',
        #       sites[2].processes[1].actual_using_resource.id, 'and he is required resource with id',
        #       sites[2].processes[1].required_resources[0].id)
        # print('Process with id', sites[1].processes[1].id, 'is working with resource with id',
        #       sites[1].processes[1].actual_using_resource.id, 'and he is required resource with id',
        #       sites[1].processes[1].required_resources[0].id)
        # print()

        sys.stdout = open('output' + str(k) + '.txt', 'w')  # save output in console to file
        is_deadlock = site_controller.search_deadlock()
        print(site_controller)
        sys.stdout.close()
