"""
Solution for Assignment 3 Excercise 7f)
Malik Al-hallak 90020
Sebastian Utzig 100059
Clemens Wegener 91268
"""
from optparse import OptionParser
import copy
from operator import attrgetter

OPEN = []
CLOSED = []

class State:

	weights = []
	packages = []
	to_be_inserted_weight = 0
	insertion_cost = 1

	def __init__(self,weights,packages,tbi,ic):
		self.weights = weights
		self.packages = packages
		self.to_be_inserted_weight = tbi
		self.insertion_cost = ic

	def print_state(self):
		print("------State------")
		print("weights: " + str(self.weights))
		print("packages: " + str(self.packages))
		print("next insertion: " + str(self.to_be_inserted_weight))
		print("accumulated cost with last insertion: " + str(self.insertion_cost) + " package(s)")
		print("-----------------")

def parse_list(astr):
    result=[];
    for part in astr.split(','):
        result.append(int(part))
    return result

def expand_state(cur_state):

	#if isnt leaf node:
	if len(cur_state.weights) != 0 :

		package_id = 0

		for package in cur_state.packages:
			total_weight = 0
			for weight in package:
				total_weight+=weight

			# add to existing package
			if total_weight + cur_state.to_be_inserted_weight <= weight_per_package:
				new_state = create_successor(cur_state)
				new_state.packages[package_id].append(cur_state.to_be_inserted_weight)
				OPEN.append(new_state)
			
			package_id+=1

		# create new package once is always an option
		new_state = create_successor(cur_state)
		new_state.packages.append([cur_state.to_be_inserted_weight])
		new_state.insertion_cost+=1
		OPEN.append(new_state)

	else:
		print_solution(cur_state)

def print_solution(cur_state):

	package_id = 0
	for package in cur_state.packages:
		total_weight = 0
		for weight in package:
			total_weight+=weight

		# add to existing package
		if total_weight + cur_state.to_be_inserted_weight <= weight_per_package:

			final_packages = copy.deepcopy(cur_state.packages)
			final_packages[package_id].append(cur_state.to_be_inserted_weight)
			print("Solution found: ")
			print("---------------")
			print("packages:")
			print(final_packages)
			print(" ")
			print("final costs:")
			print(cur_state.insertion_cost)


		package_id+=1
		exit()


def create_successor(cur_state):

	new_weights = copy.deepcopy(cur_state.weights)
	tbi = new_weights.pop()
	new_state = State(copy.deepcopy(new_weights),copy.deepcopy(cur_state.packages),tbi,cur_state.insertion_cost)
	return new_state


def find_min():

	global OPEN;

	OPEN = sorted(OPEN, key=attrgetter('insertion_cost'), reverse=True) # sort by insertion_cost

	# remove min from OPEN
	min_state = OPEN.pop()
	
	# push min into CLOSED
	CLOSED.append(min_state)
	return min_state




#parser stuff
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
################################################
#end parser stuff

#start state: no packages, full weights
packages = []
to_be_inserted_weight = weights.pop()
start_state = State(weights,packages,to_be_inserted_weight,0);

OPEN.append(start_state);

while True:

	current_state = find_min()
	expand_state(current_state)


