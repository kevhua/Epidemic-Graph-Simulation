import networkx as nx
import random
import math
import matplotlib.pyplot as plt
from Agent import *

class Network:
    """Network class
    Represents the entire Network structure.
    """
    def __init__(self, args):
        """__init__ - Network Initialization function
        Inputs:
            - args: argument parser dictionary
        Outputs:
            - None; returns Network object
        """
        # network-based parameters (taken from arguments)
        self.__network_params = { "N": args.N, # population density of agents
                                  "L": args.L, # lattice L/W dimension
                                  "num_nodes": args.L * args.L, # number of total nodes
                                  "t": args.t, # total time steps to portray
                                  "influx": args.influx, # probability of new agent being added per timestep
                                  "n_0": args.n_0 } # initial infected population size 
        # agent-based parameters (taken from arguments)
        self.__agent_params = { "asympt_length": args.asym_l, # length of time for asympt phase
                                "sympt_length": args.symp_l, # length of time for sympt phase
                                "lambda": args.lam, # disease transmission probability
                                "beta": { 1: 1, 2: 2 , 3: 3, 4: 4 } } # age-dependent mobility factor
        # initialize start time to 0
        self.__time_elapsed = 0
        # counter for number of agents
        self.__num_agents = 0
        # statistical counters
        self.__stats = {i: {"total": 0, "alive": 0, "dead": 0, "infected": 0} for i in range(1, 5)}
        self.__plot_points = {i: [] for i in range(0, 5)}
        # generate and populate lattice
        self.__generate_lattice()
        self.__populate_lattice()
        # initialize the display of the network
        plt.figure(figsize=(15, 8))
        plt.plot()

    # ----------------------------------------------------------#
    #                Internal Class Functions                   #
    # ----------------------------------------------------------#

    def __generate_lattice(self):
        """__generate_lattice - generates a lattice structure
        Inputs:
            - None; uses self.__network_params to get required values
        Outputs:
            - None; saves lattice in self.__lattice
        """
        # generate an empty linear LxL lattice
        self.__lattice = nx.grid_2d_graph(m=self.__network_params["L"], n=self.__network_params["L"])
        # set each edge weight to be 1 for ease of display
        for edge in self.__lattice.edges:
            self.__lattice.edges[edge]["weight"] = 1.0
        # manually add diagonal edges to account for full 8 neighbors per node
        # weight for each each sqrt(1^2+1^2) = ~1.41
        self.__lattice.add_edges_from([((x, y), (x+1, y+1))
                                       for x in range(self.__network_params["L"]-1)
                                       for y in range(self.__network_params["L"]-1)] + 
                                      [((x+1, y), (x, y+1))
                                       for x in range(self.__network_params["L"]-1)
                                       for y in range(self.__network_params["L"]-1)], weight=1.41)
        # generate new labels for nodes based on integer indices
        labels = {}; index_counter = 0
        for i in range(self.__network_params["L"]):
            for j in range(self.__network_params["L"]):
                labels[(i, j)] = index_counter; index_counter += 1
        # update labels for each node to be an integer index for easier association
        nx.relabel_nodes(self.__lattice, labels, copy=False)
        # set all nodes to 'unoccupied' (or empty list)
        for i in range(self.__network_params["num_nodes"]):
            self.__lattice.nodes[i]["occupants"] = []


    def __populate_lattice(self):
        """__populate_lattice - fills lattice with N agents randomly
        Inputs:
            - None; uses self.__agent_params to get required values
        Outputs:
            - None; saves agents in node occupancy lists
        """
        # handle initial infected cases by randomly assigning id's that would be infected
        infected_indices = []
        # repeat until required number of infected indices met
        for i in range(self.__network_params["n_0"]):
            # get a new index to infect
            ind = random.randint(0, int(self.__network_params["num_nodes"] * self.__network_params["N"]))
            while ind in infected_indices:
                ind = random.randint(0, int(self.__network_params["num_nodes"] * self.__network_params["N"]))
            # add to list
            infected_indices.append(ind)
        # randomly disperse agents across lattice, with population of density * num_nodes
        for i in range(int(self.__network_params["num_nodes"] * self.__network_params["N"])):
            # create agent at random location
            agent = Agent(random.randint(0, self.__network_params["num_nodes"] - 1))
            # check if infected
            if i in infected_indices:
                agent.set_infected()
                # update infection statistics
                self.__stats[agent.get_age()]["infected"] += 1
            # append to lattice node occupancy list
            self.__lattice.nodes[agent.get_location()]["occupants"].append(agent)
            # increment number of active agents counter
            self.__num_agents += 1
            # update statistical counters
            self.__stats[agent.get_age()]["total"] += 1
            self.__stats[agent.get_age()]["alive"] += 1

    def __check_for_movement(self):
        """__check_for_movement - checks which agent should move and tries to move agent
        Inputs:
            - None
        Outputs:
            - None
        """
        # randomly select index of site 1
        s_1_index = random.randint(0, self.__network_params["num_nodes"] - 1)
        # ensure that s_1_index is not devoid of occupants
        while len(self.__lattice.nodes[s_1_index]["occupants"]) == 0:
            s_1_index = random.randint(0, self.__network_params["num_nodes"] - 1)
        # identify site 1's neighbors
        neighbors = [n for n in self.__lattice.neighbors(s_1_index)]
        # randomly select index of site 2 from list of neighbor nodes
        s_2_index = neighbors[random.randint(0, len(neighbors) - 1)]
        # check to ensure no infectious individual is at s_2
        # use repeat_counter to ensure no infinite loops
        repeat_counter = 0
        while True:
            # if caught in infinite loop, no movement
            if repeat_counter > 30:
                return
            # initialize a flag to catch infectiousness
            check_infectious = False
            # iterate over every agent in the s_2 site
            for agent_index in range(0, len(self.__lattice.nodes[s_2_index]["occupants"]) - 1):
                # if infectious, re-randomize s_2 and set to recheck again
                if self.__lattice.nodes[s_2_index]["occupants"][agent_index].get_symptomatic():
                    check_infectious = True
                    s_2_index = neighbors[random.randint(0, len(neighbors) - 1)]
                    repeat_counter += 1 
                    break
            # if check passed, exit loop
            if not check_infectious:
                break
        # randomly select agent in s_1 to attempt to move
        agent_index = random.randint(0, len(self.__lattice.nodes[s_1_index]["occupants"]) - 1)
        # initially setting n_age_1 to be 0 (to be used as a counter)
        n_age_1 = 0
        # noting age category of selected agent to move
        age_category = self.__lattice.nodes[s_1_index]["occupants"][agent_index].get_age()
        # calculating n_age_1 by iterating over occupants of site 1 (s_1)
        for occupant_index in range(0, len(self.__lattice.nodes[s_1_index]["occupants"])):
            # incrementing only if matching age
            if self.__lattice.nodes[s_1_index]["occupants"][occupant_index].get_age() == age_category:
                n_age_1 += 1
        # intially setting n_age_2 to be 0 (to be used as a counter)
        n_age_2 = 0
        # calculating n_age_2 by iterating over occupants of site 2 (s_2)
        for occupant_index in range(0, len(self.__lattice.nodes[s_2_index]["occupants"])):
            # incrementing only if matching age
            if self.__lattice.nodes[s_2_index]["occupants"][occupant_index].get_age() == age_category:
                n_age_2 += 1
        # attempt to move the agent from s_1 to s_2
        if self.__lattice.nodes[s_1_index]["occupants"][agent_index].move_agent(n_age_1, n_age_2, # n_age values for s_1 and s_2 respectively
                                                                                self.__lattice.nodes[s_2_index], # target node
                                                                                self.__agent_params["beta"]): # beta associative list
            # on success, update lists for both s_1 and s_2 accordingly
            self.__lattice.nodes(data=True)[s_2_index]["occupants"].append(self.__lattice.nodes(data=True)[s_1_index]["occupants"].pop(agent_index))

    def __check_for_infection(self):
        """__check_for_infection - checks all agents for infection, tries to propogate
        Inputs:
            - None
        Outputs:
            - None
        """
        # iterate over every node in lattice
        for node in self.__lattice.nodes(data=True):
            # for each node, gather up all the neighboring nodes (including self)
            neighbors = [n for n in self.__lattice.neighbors(node[0])] + [node[0]]
            # iterate over every occupant of the node
            for occupant_index in range(0, len(node[1]["occupants"])):
                # if current occupant is infectious...
                if node[1]["occupants"][occupant_index].get_infectious():
                    # iterate over all neighboring nodes
                    for neighbor in neighbors:
                        # iterate over all occupants of neighboring node
                        for o_index in range(0, len(self.__lattice.nodes[neighbor]["occupants"]) - 1):
                            # expose each neighboring occupant to infection with probability lambda
                            if self.__lattice.nodes[neighbor]["occupants"][o_index].expose_to_infection(self.__agent_params["lambda"]):
                                # update statistics
                                self.__stats[self.__lattice.nodes[neighbor]["occupants"][o_index].get_age()]["infected"] += 1

    def __check_for_death(self):
        """__check_for_death - checks all agents for infectious status and applies death as needed
        Inputs:
            - None
        Outputs:
            - None
        """
        # iterate over every node in lattice
        for node in self.__lattice.nodes(data=True):
            # for each node, iterate over all occupants
            for occupant_index in range(0, len(node[1]["occupants"])):
                # update agent's status
                if node[1]["occupants"][occupant_index].update_agent(self.__agent_params["asympt_length"], self.__agent_params["sympt_length"]):
                    # decrement counter for death
                    self.__num_agents -= 1
                    # update statistics
                    self.__stats[node[1]["occupants"][occupant_index].get_age()]["alive"] -= 1
                    self.__stats[node[1]["occupants"][occupant_index].get_age()]["dead"] += 1

    def __check_for_influx(self):
        """__check_for_influx - checks to see if new members of population should be added (randomly)
        Inputs:
            - None
        Outputs:
            - None
        """
        # compute a probability of adding new agent to population
        probability = random.randint(1, 100) / 100
        # if probability is sufficient...
        if probability < self.__network_params["influx"]:
            # add new agent to lattice randomly
            agent = Agent(random.randint(0, self.__network_params["num_nodes"] - 1))
            self.__lattice.nodes[agent.get_location()]["occupants"].append(agent)
            # increment num_agents counter
            self.__num_agents += 1
            # update statistics
            self.__stats[agent.get_age()]["total"] += 1
            self.__stats[agent.get_age()]["alive"] += 1

    def __timestep(self):
        """__timestep - handling of a single timestep
        Runs a single timestep of the model on the network.
        Based on a Metropolitan algorithm, so a single agent moves per step
        Inputs:
            - None
        Outputs:
            - None; lattice updated with new configuration
        """
        # check if infection spreads and carry it out
        self.__check_for_infection()
        # update status of agents and check for death - apply as needed
        self.__check_for_death()
        # check if agent makes movement and carry it out
        self.__check_for_movement()
        # check if new agent to be introduce to population
        self.__check_for_influx()

        # increment timestep counter
        self.__time_elapsed += 1

    def __generate_colorations(self, color_map):
        """__generate_colorations - generate the associated color list for nodes
        Inputs:
            - color_map: associated mapping
        Outputs:
            - colorations: list of colors for the nodes
        """
        # initializing a list to store the colors for each node
        colorations = []
        # iterate over each node in lattice
        for node in self.__lattice.nodes(data=True):
            # if no occupants at node, simply assign 'blank' color (equivalent to all dead)
            if len(node[1]["occupants"]) == 0:
                colorations.append(color_map["dead"])
            # for all other cases, figure out color association
            else:
                # initialize boolean flags for each scenario
                contains_asymp = False
                contains_sympt = False
                contains_healthy = False
                # check all occupants in node for status
                for agent in node[1]["occupants"]:
                    # if at least one is asymptomatic, flip flag
                    if agent.get_status()[0] == "asymptomatic":
                        contains_asymp = True
                    # if at least one is symptomatic, flip flag
                    if agent.get_status()[0] == "symptomatic":
                        contains_sympt = True
                    # if at least one is health, flip flag
                    if agent.get_status()[0] == "healthy":
                        contains_healthy = True
                # check in decreasing order of priority...
                # 1. symptomatic
                # 2. asymptomatic
                # 3. healthy
                if contains_sympt:
                    colorations.append(color_map["symptomatic"])
                elif contains_asymp:
                    colorations.append(color_map["asymptomatic"])
                elif contains_healthy:
                    colorations.append(color_map["healthy"])
                else:
                    colorations.append(color_map["dead"])
        # return coloration list
        return colorations

    def __generate_labels(self):
        """__generate_labels - generate the node's labels
        Inputs:
            - None
        Outputs:
            - labels: list of labels for the nodes
        """
        # get the iterator for node's labels
        labels = nx.get_node_attributes(self.__lattice, "occupants")
        # iterate over the nodes in the iterator
        for node in labels:
            # initialize num_infected; num_dead to 0
            num_infected = 0; num_dead = 0
            # iterate over the agents in the node
            for agent in labels[node]:
                # if agent is in any way infected, increment counter
                if agent.get_status()[0] in ["asymptomatic", "symptomatic"]:
                    num_infected += 1
                # if agent is dead, increment counter
                elif agent.get_status()[0] in ["dead"]:
                    num_dead += 1
            # update label depending on health status
            if len(labels[node]) > 0:
                labels[node] = f"{num_infected}|{len(labels[node]) - num_infected - num_dead}"
            else:
                labels[node] = ""
        # return list of labels
        return labels

    def __update_display(self, color_map={ "healthy": "green", "asymptomatic": "orange", "symptomatic": "red", "dead": "gray" }):
        """__update_display - handles the display with matplotlib
        Inputs:
            - (Optional) color_map: an association dictionary for status->color
        Outputs:
            - None; displays as a window
        """
        plt.clf()
        plt.title(f"{self.__time_elapsed} / {self.__network_params['t']} - Number of Agents: {self.__num_agents}")
        # get list of colorations
        colorations = self.__generate_colorations(color_map)
        # get list of labels
        labels = self.__generate_labels()
        # generate the lattice drawing
        nx.draw_spectral(self.__lattice, node_color=colorations, labels=labels)
        # update the display for animation-purposes
        plt.pause(0.05)

    def __generate_statistical_display(self):
        """__generate_statistical_display - generates a graph stats over time
        Inputs:
            - None
        Outputs:
            - None; displays as a window
        """
        plt.clf()
        plt.title(f"λ={self.__agent_params['lambda']}; Density={self.__network_params['N']}; InfluxRate={self.__network_params['influx']}")
        plt.plot([i for i in range(0, self.__network_params["t"])], self.__plot_points[0], label="total population")
        plt.plot([i for i in range(0, self.__network_params["t"])], self.__plot_points[1], label="adults")
        plt.plot([i for i in range(0, self.__network_params["t"])], self.__plot_points[2], label="elderly")
        plt.plot([i for i in range(0, self.__network_params["t"])], self.__plot_points[3], label="youths")
        plt.plot([i for i in range(0, self.__network_params["t"])], self.__plot_points[4], label="babies")
        plt.xlabel("Timesteps")
        plt.ylabel("Number of Agents")
        plt.legend()
        plt.show()

    # ----------------------------------------------------------#
    #                          Getters                          #
    # ----------------------------------------------------------#

    def get_lattice(self):
        # returns the lattice structure
        return self.__lattice
    def get_elapsed_time(self):
        # returns how many time steps have passed
        return self.__time_elapsed

    # ----------------------------------------------------------#
    #                     Class Methods                         #
    # ----------------------------------------------------------#

    def run_simulation(self):
        """run_simulation - runs t timesteps of simulation
        Inputs:
            - None
        Outputs:
            - None
        """
        while self.__time_elapsed < self.__network_params["t"]:
            self.__timestep()
            self.__update_display()
            # update statistic plot-points
            for key in self.__stats:
                self.__plot_points[key].append(self.__stats[key]["infected"] - self.__stats[key]["dead"])
            self.__plot_points[0].append(sum([self.__stats[key]["infected"] - self.__stats[key]["dead"] for key in self.__stats]))
        plt.show()
        # display statistical graphs
        self.__generate_statistical_display()
        