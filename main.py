# import matplotlib.pyplot as plt
import numpy as np
from oct2py import octave
from branch_deactivate import branch_deactivate
from SPA_difference import SPA_difference
from distribute_slack import distribute_slack
from set_opf_constraints import set_opf_constraints
from objective_function import restoration_time
from config import case14_droop_constants,\
    distribute_slack_constants,\
    mp_opt,\
    case14_ramp_rates


# Open up IEEE 14 bus test case and run pf
base_case = octave.loadcase('case14')
base_result = octave.runpf(base_case, mp_opt)

# Remove random line(s) and run pf
base_case_contingency, branch_deactivated = branch_deactivate(case=base_case, n_branches=1)


# TODO: check for islands, run each island separately...
# TODO: write method to check which lines are deactived... might be useful
# TODO: method to evaluate restoration time

# Distribute slack using LFC (droop constants)
test_result_dist = distribute_slack(test_case=base_case_contingency,
                                    slack_ind=np.nonzero(base_case_contingency['bus'][:, 1] == 3),
                                    droop_constants=case14_droop_constants,
                                    converge_options=distribute_slack_constants,
                                    mp_options=mp_opt)

# SPA differences at each branch of base and test cases
if test_result_dist:
    base_diffs = SPA_difference(base_result)
    test_diffs = SPA_difference(test_result_dist)
    # print(base_diffs[:, 1] - test_diffs[:, 1])
    print('SPA of lines prior to deactivation: %s' % base_diffs[branch_deactivated, 1])
    print('SPA of lines after deactivation: %s' % test_diffs[branch_deactivated, 1])
else:
    print('Could not calculate SPA differences')

# Set up OPF!
test_case_opf = set_opf_constraints(base_case_contingency, branch_deactivated, max_SPA=10)

# Run OPF
test_result_opf = octave.runopf(test_case_opf, mp_opt)

# Did it work??
test_opf_diffs = SPA_difference(test_result_opf)
print('SPA of deactivated lines: %s' % test_opf_diffs[branch_deactivated, 1])
print('Original active: %s \n OPF active: %s \n\n Original reactive: %s \n OPF reactive: %s'
      % (base_case_contingency['gen'][:, 1],
         test_result_opf['gen'][:, 1],
         base_case_contingency['gen'][:, 2],
         test_result_opf['gen'][:, 2]))

# Evaluate time
restoration_time(base_case_contingency, case14_ramp_rates,)
