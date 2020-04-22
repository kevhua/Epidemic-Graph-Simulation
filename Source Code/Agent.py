import random
import math

class Agent:
    """Agent class
    Represents an agent on the network.
    """
    agent_id = 0
    def __init__(self, node):
        """__init__ - Agent Initialization function
        Inputs:
            - node: location at which Agent starts at
        Outputs:
            - None; returns Agent object
        """
        # set the agent's id and increment class counter
        self.__id = Agent.agent_id; Agent.agent_id+= 1
        self.__health_status = { "label": "healthy", 
                                 "days_infected": -1 }

        self.__age_categorize(random.randint(0, 82))
        self.__location = node
        self.__susceptibility_factor = math.e**(-(self.__age) / 10)

    # ----------------------------------------------------------#
    #                Internal Class Functions                   #
    # ----------------------------------------------------------#

    def __age_categorize(self, age):
        """__age_categorize - converts integer age to categorical label [1-4]
        Inputs:
            - age: integer denoting age
        Outputs:
            - None
        """
        # Baby age category - most at risk, highest categorical denomination
        if age <= 4:
            self.__age = 4
        # Youth age category - second most at risk
        elif 5 <= age <= 14:
            self.__age = 3
        # Adult age category - least at risk
        elif 15 <= age <= 64:
            self.__age = 1
        # Elderly age category - second least at risk
        else:
            self.__age = 2

    # ----------------------------------------------------------#
    #                          Getters                          #
    # ----------------------------------------------------------#

    def get_id(self):
        # get agent's id
        return self.__id
    def get_status(self):
        # get status tuple: (label, days_infected)
        return self.__health_status["label"], self.__health_status["days_infected"]
    def get_infectious(self):
        # returns boolean about infectious or not
        if self.__health_status["label"] in ["asymptomatic", "symptomatic"]:
            return True
        return False
    def get_symptomatic(self):
        # returns if symptomatic or not
        return self.__health_status["label"] == "symptomatic"
    def get_age(self):
        # get age category
        return self.__age
    def get_location(self):
        # get location node where agent is current on
        return self.__location

    # ----------------------------------------------------------#
    #                         Setters                           #
    # ----------------------------------------------------------#

    def set_location(self, node):
        # sets location to be new node
        self.__location = node
    def set_infected(self):
        # sets agent to be infected - for initial cases
        self.__health_status["label"] = "asymptomatic"
        self.__health_status["days_infected"] = 0

    # ----------------------------------------------------------#
    #                     Class Methods                         #
    # ----------------------------------------------------------#

    def update_agent(self, asympt_phase_length, sympt_phase_length):
        """update_agent method
        Performs a single time-step update on agent
        Inputs:
            - asympt_phase_length: integer denoting length of time for asymptomatic phase
            - sympt_phase_length: integer denoting length of time for symptomatic phase
        Outputs:
            boolean: indicative of death flag
        """
        # updates performed only on infected individuals - skip if dead or healthy
        if self.__health_status["label"] not in ["healthy", "dead"]:
            # increment the days_infected counter
            self.__health_status["days_infected"] += 1

            # check if phase transition is required (asympt -> sympt) and update
            if self.__health_status["label"] == "asymptomatic":
                if self.__health_status["days_infected"] > asympt_phase_length:
                    self.__health_status["label"] = "symptomatic"
            # check if phase transition is required (sympt -> dead) and update
            else:
                if self.__health_status["days_infected"] > asympt_phase_length + sympt_phase_length:
                    self.__health_status["label"] = "dead"
                    self.__health_status["days_infected"] = -1
                    return True
        return False

    def expose_to_infection(self, λ):
        """expose_to_infection method
        Attempt to expose agent to infection, with probability of catching
        Inputs:
            - λ: probability of catching infection
        Outputs:
            - boolean: returns boolean of if infection occurred; potential update in health_status
        """
        # check for existing infection; can't catch while already caught
        if self.__health_status["label"] not in ["asymptomatic", "symptomatic", "dead"]:
            # compute a probability to compare to
            probability = random.randint(1, 100) / 100
            # check if agent will be infected (factoring in susceptibility)
            # update if necessary
            if probability <= (λ * self.__susceptibility_factor):
                self.__health_status["label"] = "asymptomatic"
                self.__health_status["days_infected"] = 0
                return True
        return False

    def move_agent(self, n_age_1, n_age_2, target_node, β):
        """move_agent method
        Attempts to move agent to target node
        2 Possible Probabilities dependent on situation:
            (1) s_1 -> s_2 = increase or constant in n_age_2 score compared to n_age_1
                p_(s_1->s_2) = min([1, e^(β * (Δn_age))])
            (2) s_1 -> s_2 = decrease in n_age_2 score compared to n_age_1
                p_(s_1->s_2) = e^(-β * (Δn_age))
        Inputs:
            - n_age_1: integer representing number of same-age nearest neighbors at site 1
            - n_age_2: integer representing number of same-age nearest neighbors at site 2
            - target_node: node representing location to move
            - β: age-dependent mobility factor (dictionary object)
        Outputs:
            - Status (boolean): did operation succeed?
        """
        # check if infected (symptomatic) - if yes, return False
        if self.__health_status["label"] == "symptomatic":
            return False

        # computer a probability to compare to
        probability = random.randint(1, 100) / 100

        # Case 1: s_1 -> s_2 movement increases/remains constant to n_age_2 as compared to n_age_1
        if n_age_1 <= n_age_2:
            prob_1_to_2 = min([1, math.e**(β[self.__age] * (n_age_2 - n_age_1))])
        # Case 2: s_1 -> s_2 movement lessens n_age_2 compared to n_age_1
        else:
            prob_1_to_2 = math.e**(-β[self.__age] * (n_age_2 - n_age_1))

        # make movement if probability is sufficient
        if probability <= prob_1_to_2:
            self.__location = target_node
            return True
        return False
