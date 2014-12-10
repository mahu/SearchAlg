"""
Solution for Assignment 3 Excercise 7f)
Malik Al-hallak 90020
Sebastian Utzig 100059
Clemens Wegener 91268

Solution for bin packing problem using BF* 
because of underlying state-space representation.
State-space representations are appropriate for 
non-decomposable problems.
"""

# example call:
# python packing.py -p 20 -w 1,4,6,7,7,9,11,13,15,16

from optparse import OptionParser
import copy
from operator import attrgetter

OPEN = []
CLOSED = []

class State:

	weights = []
	packages = []
	insertion_cost = 1

	def __init__(self,weights,packages,ic):
		self.weights = weights
		self.packages = packages
		self.insertion_cost = ic

	def __str__(self):
		return "------State------\n" +\
		"Weights: " + str(self.weights) +"\n" +\
		"Packages: " + str(self.packages) + "\n"+\
		"Accumulated cost with last insertion: " + str(self.insertion_cost) + " package(s)\n" +\
		"-----------------"


def parse_list(astr):
    result=[];
    for part in astr.split(','):
        result.append(int(part))
    return result


def expand_state(cur_state):

	#if isnt leaf node:
	if len(cur_state.weights) != 0 :

		# for all successors we need to push a new weight into packages
		new_weights = copy.deepcopy(cur_state.weights)
		to_be_inserted_weight = new_weights.pop()

		package_id = 0

		# check available space in already existing packages
		for package in cur_state.packages:
			total_weight = 0
			for weight in package:
				total_weight+=weight

			# add to existing package if we are under weight_per_package limit
			if total_weight + to_be_inserted_weight <= weight_per_package:
				new_state = State(new_weights,copy.deepcopy(cur_state.packages),cur_state.insertion_cost)
				new_state.packages[package_id].append(to_be_inserted_weight)
				OPEN.append(new_state)
			
			package_id+=1

		# create new package once (is always an option)
		new_state = State(new_weights,copy.deepcopy(cur_state.packages),cur_state.insertion_cost)
		new_state.packages.append([to_be_inserted_weight])
		new_state.insertion_cost+=1 # since we created a new package, the cost increases
		OPEN.append(new_state)

	else:

		# delayed termination (reached the first leaf node which is minimum because of accumulated costs)
		print("\nSolution found: ")
		print("---------------")
		print(str(cur_state))

		exit()


def find_min():

	global OPEN;

	# sort by insertion_cost
	OPEN = sorted(OPEN, key=attrgetter('insertion_cost'), reverse=True)

	# remove min from OPEN
	min_state = OPEN.pop()
	
	# push min into CLOSED
	CLOSED.append(min_state)

	return min_state



usage = "usage: %prog [options]"
parser = OptionParser(usage)

parser.add_option("-w", "--weights", action="store", type= "string",dest="weights",
	default="", help="list of weights")
parser.add_option("-p", "--weight_per_package" , action="store", type= "int",dest="weight_per_package", 
	default=20, help="specifies the maximum weight per package")

(options,args) = parser.parse_args()

#input parameter
weights = parse_list(options.weights)
weight_per_package = options.weight_per_package


#start state: no packages, full weights
packages = []
start_state = State(weights,packages,0);

OPEN.append(start_state);

# delayed termination in expand_state() will exit loop if minimum is found
while True:

	current_state = find_min()
	expand_state(current_state)


