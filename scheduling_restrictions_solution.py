# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dimod import ConstrainedQuadraticModel
from dwave.system import LeapHybridCQMSampler

# Set the solver we're going to use
def set_sampler():
    '''Returns a dimod sampler'''

    sampler = LeapHybridCQMSampler()

    return sampler

# Set employees and preferences
def employee_preferences():
    '''Returns a dictionary of employees with their preferences'''

    preferences = { "Anna": [1,2,3,100],
                    "Bill": [3,2,1,4],
                    "Chris": [4,2,3,1],
                    "Diane": [4,1,2,3],
                    "Erica": [1,2,3,4],
                    "Frank": [3,2,1,4],
                    "George": [4,2,3,1],
                    "Harriet": [4,1,2,3]}

    return preferences

# Create CQM object
def build_cqm():
    '''Builds the CQM for our problem'''

    preferences = employee_preferences()
    num_shifts = 4

    # Initialize the CQM object
    cqm = ConstrainedQuadraticModel()

    # Represent shifts as a set of binary variables
    # for each employee
    for employee, preference in preferences.items():
        # Create labels for binary variables
        labels = [f"x_{employee}_{shift}" for shift in range(num_shifts)]
    
        # Add a discrete constraint over employee binaries
        cqm.add_discrete(labels, label=f"discrete_{employee}")

        # Incrementally add objective terms as list of (label, bias)
        cqm.objective.add_linear_from([*zip(labels, preference)])

    # TODO: Restrict Anna from working shift 4

    # TODO: Set constraints to reflect the restrictions in the README.
    for i in range(num_shifts):
        cqm.add_constraint_from_iterable([(f"x_Bill_{i}", f"x_Frank_{i}", 1)], "==", 0)
        cqm.add_constraint_from_iterable([(f"x_Erica_{i}",1), (f"x_Harriet_{i}",-1)], "==", 0)

        # sum of binary variables for all shifts for all people has to be equal to 2. This to ensure that there are always 2 people at every shift.
        cqm.add_constraint_from_iterable([(f"x_{name}_{i}",1) for name in preferences], "==", 2)

    return cqm

# Solve the problem
def solve_problem(cqm, sampler):
    '''Runs the provided cqm object on the designated sampler'''

    # Initialize the CQM solver
    sampler = set_sampler()

    # Solve the problem using the CQM solver
    sampleset = sampler.sample_cqm(cqm, label='Training - Employee Scheduling')

    # Filter for feasible samples
    feasible_sampleset = sampleset.filter(lambda x:x.is_feasible)

    return feasible_sampleset

# Process solution
def process_sampleset(sampleset):
    '''Processes the best solution found for displaying'''
   
    # Get the first solution
    sample = sampleset.first.sample

    shift_schedule=[ [] for i in range(4)]

    # Interpret according to shifts
    for key, val in sample.items():
         if val == 1.0:
            name = key.split('_')[1]
            shift = int(key.split('_')[2])
            shift_schedule[shift].append(name)

    return shift_schedule

## ------- Main program -------
if __name__ == "__main__":

    # Problem information
    shifts = [1, 2, 3, 4]
    num_shifts = len(shifts)

    cqm = build_cqm()

    sampler = set_sampler()

    sampleset = solve_problem(cqm, sampler)

    shift_schedule = process_sampleset(sampleset)

    for i in range(num_shifts):
        print("Shift:", shifts[i], "\tEmployee(s): ", shift_schedule[i])
