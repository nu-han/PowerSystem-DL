import numpy as np
from auxiliary.set_opf_constraints import set_opf_constraints


def within_energized(ps, island_1, bus_ids):

    state_list = list()

    # Take preliminary snapshot of the system
    prelim_state = ps.evaluate_state(list(ps.islands_evaluated.values()))
    prelim_state['Title'] = 'Preliminary state'  # Shows up on plot
    state_list.append(prelim_state)

    # Set opf constraint to SPA diff
    # TODO: I have to make sure that the current state is updated with respect to island ids
    branch_ind = np.all(ps.islands[ps.island_map[island_1]]['branch'][:, 0:2] == bus_ids, axis=1)
    ps.islands[ps.island_map[island_1]] = set_opf_constraints(test_case=ps.islands[ps.island_map[island_1]],
                                                              set_branch=branch_ind,
                                                              max_SPA=10,
                                                              set_gen=False,
                                                              set_loads=False)
    # Run opf on the islands
    ps.evaluate_islands()  # Matpower needs to be altered for this to work -- Think I got it

    # Achieved by making islands_evaluated a dictionary
    ps.islands_evaluated[ps.island_map[island_1]]['branch'][branch_ind, 10] = 1  # For animation
    reschedule_state = ps.evaluate_state(list(ps.islands_evaluated.values()))
    reschedule_state['Title'] = 'Rescheduling for connection of branch %s - %s' % (int(bus_ids[0]), int(bus_ids[1]))
    state_list.append(reschedule_state)

    # Close the line and restore the SPA diff constraint
    ps.islands[ps.island_map[island_1]]['branch'][branch_ind, 10] = 1
    ps.islands[ps.island_map[island_1]] = set_opf_constraints(test_case=ps.islands[ps.island_map[island_1]],
                                                              set_branch=branch_ind,
                                                              max_SPA=360,
                                                              set_gen=False,
                                                              set_loads=False)

    # Add another state for a pause between spa reschedule and new steady state
    # state_list.append(reschedule_state)

    # Run opf to get final steady state
    ps.evaluate_islands()
    after_connection_state = ps.evaluate_state(list(ps.islands_evaluated.values()))
    after_connection_state['Title'] = 'Solving state after line connection'
    state_list.append(after_connection_state)

    return state_list
