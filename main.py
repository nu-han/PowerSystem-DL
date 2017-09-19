from itertools import permutations

import numpy as np
from matplotlib import pyplot as plt
from oct2py import octave

from auxiliary.SPA_difference import SPA_difference
from auxiliary.config import mp_opt, \
    case14_ramp_rates, \
    line_ratings
from auxiliary.visualize_network import visualize_network
from cost.objective_function import objective_function
from set_opf_constraints import set_opf_constraints
from system.branch_deactivate import branch_deactivate
from system.check_extract_islands import check_extract_islands


# Test code
# -----------------

from system.PowerSystem import PowerSystem
from oct2py import octave
from auxiliary.config import mp_opt, \
    case14_ramp_rates, \
    line_ratings,\
    dispatchable_loads

base_case = octave.loadcase('case14')
base_case['branch'][:, 5] = line_ratings  # Have to add line ratings
base_result = octave.runpf(base_case, mp_opt)

ps = PowerSystem(base_result, n_deactivated=8)

for i, island in enumerate(ps.islands):
    print('island %s: load %s' % (i, island['is_load']))
    print('island %s: gen %s' % (i, island['is_gen']))

# -----------------

# What happened?
ps.islands_constrained[0]['gencost']
ps.islands_state[0]['gencost']  # For some reason, the gencost matrix is reset after running opf

# TODO: Next I want to create a state vis function in the PowerSystem class
# TODO: make sure that Blackout islands work -- don't currently


# -----------------






# Open up IEEE 14 bus test case and run pf
base_case = octave.loadcase('case14')
base_case['branch'][:, 5] = line_ratings  # Have to add line ratings
base_result = octave.runpf(base_case, mp_opt)


# Visualize the graph
visualize_network(base_result)

# Remove random line(s) and run pf
base_case_contingency, branch_deactivated = branch_deactivate(case=base_case, n_branches=8)


islands = check_extract_islands(base_case_contingency)
islands.shape

# Get an idea for the situation
for i, island in enumerate(islands):
    print('island %s: load %s' % (i, island['is_load']))
    print('island %s: gen %s' % (i, island['is_gen']))

# TODO: check for islands and deal with that - DONE
# TODO: For islanded systems, assume the first reconnection is free
# TODO: Write method to determine if there is unserved load.  These are more interesting cases.
# TODO: Add unserved load to the objective function
# TODO: Make loads curtailable in OPF... Need to do more tinkering with opf
# TODO: Transform objective to a monetary equivalent with one output.
# TODO: Implement the ghost line method to simulate energizing one end of a disonnected line
# TODO: Implement more error handling, what if something doesnt converge?
# TODO: Make sure lines have MVA ratings - DONE


# Make copy of islands to manipulate for opf
from copy import deepcopy
islands_opf = deepcopy(islands)

# For islands with gen and load, set up opf
for i, isl in enumerate(islands_opf):

    # Run opf if island has both gen and load
    if isl['is_gen'] and isl['is_load']:
        print('here')
        isl = set_opf_constraints(isl, set_gen=True, set_loads=True)

    # Run opf on islands
    opf_result = octave.runopf(isl, mp_opt)

    # Do some error handling if it doesn't converge

# Evaluate the total system state. (load state, gen state, line injection state)


    # SPA differences at each branch of base and test cases
    if result_distr:
        base_diffs = SPA_difference(base_result)
        test_diffs = SPA_difference(result_distr)
        # print(base_diffs[:, 1] - test_diffs[:, 1])
        print('SPA of lines prior to deactivation: %s' % base_diffs[branch_deactivated, 1])
        print('SPA of lines after deactivation: %s' % test_diffs[branch_deactivated, 1])
    else:
        print('Could not calculate SPA differences')


# Generate a list of all permutations of restoration order
perm = list(permutations(branch_deactivated))
# Preallocate outputs of objective function
objective_store = np.zeros((len(perm), 3))

for i, p in enumerate(perm):
    objective_store[i, :] = objective_function(base_case_contingency=base_case_contingency,
                                               result=result_distr,
                                               ramp_rates=case14_ramp_rates,
                                               order=p,
                                               slack_ind=slack_ind,
                                               max_SPA=20)

# Plot the results
plt.subplot(311)
plt.plot(objective_store[:, 0], 'ro-')
plt.title('restoration time')
plt.subplot(312)
plt.plot(objective_store[:, 1], 'bo-')
plt.title('total energy deviation')
plt.subplot(313)
plt.plot(objective_store[:, 2], 'go-')
plt.title('total losses')
plt.xlabel('Solution number')