import argparse
import networkx as nx
import random
import math
from Network import *
from Agent import *

def __parse_arguments():
    # generate a command-line argument parser to handle hyperparameter setting
    parser = argparse.ArgumentParser()

    # L - dimension of the lattice
    parser.add_argument("--L", type=int, nargs='?', default=10)
    # N - density of population
    parser.add_argument("--N", type=float, nargs='?', default=1.0)
    # t - timesteps to simulate
    parser.add_argument("--t", type=int, nargs='?', default=500)
    # n_0 - initial amount of infected individuals
    parser.add_argument("--n_0", type=int, nargs='?', default=1)
    # lam - transmission probability 0 <= lam <= 1
    parser.add_argument("--lam", type=float, nargs='?', default=0.1)
    # asym_l - length of time for asymptomatic phase (0 = no asympt phase)
    parser.add_argument("--asym_l", type=int, nargs='?', default=20)
    # symp_l - length of time for symptomatic phase
    parser.add_argument("--symp_l", type=int, nargs='?', default=20)
    # influx - probability that new agent is added per timestep (0 = no new agents)
    parser.add_argument("--influx", type=float, nargs='?', default=0.0)

    return parser.parse_args()

def main():
    # gather command-line arguments
    args = __parse_arguments()
    # initialize network
    network = Network(args)
    # run simulation based on hyper-parameters given
    network.run_simulation()

if __name__ == "__main__":
    main()