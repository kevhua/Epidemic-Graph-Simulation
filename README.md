# Epidemic-Graph-Simulation
A simulation of an epidemic on a lattice graph.
Code written by Kevin Hua - April 2020.

## Dependencies
- matplotlib
- networkx
- math
- random
- argparse

## Files in Project:
- Source Code/Agent.py
- Source Code/Network.py
- Source Code/main.py
- README.md

### Agent.py
Contains code relevant to the Agent object. Agents are stored in the Network.


### Network.py
Contains code for modeling the Network and simulations.


### main.py
Contains code for running the simulation in general.
Code uses command-line arguments to set the hyper-parameters.
Each parameter uses a default value, but can be overridden.

## Running the Simulation
Basic run:

```bash
> python3 main.py
```

Parameters:
- [```--L```] Lattice Size (L x L)                ==>   *(default=100)*
- [```--N```] population density                  ==>   *(default=1.0)*
- [```--t```] timesteps to show                   ==>   *(default=500)*
- [```--n_0```] initial infected population size  ==>   *(default=1)*
- [```--lam```] basic infection rate              ==>   *(default=0.1)*
- [```--asym_l```] length of asymptomatic phase   ==>   *(default=20)*
- [```--symp_l```] length of symptomatic phase    ==>   *(default=20)*
- [```--influx```] influx rate                    ==>   *(default=0.0)*

Sample modified run:

```bash
> python3 main.py --L=1000 --N=0.2
```
