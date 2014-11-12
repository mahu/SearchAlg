"""
Solution for Assignment 1 Excercise 7b)
Malik Al-hallak 90020
Sebastian Utzig 100059
Clemens Wegener 91268
"""
from itertools import chain, combinations
from collections import Counter as Multiset

def powerset(multiset):
	
	return [Multiset({'M' : m, 'C' : c}) for m in range(multiset['M']+1) 
		for c in range(multiset['C']+1)]

def is_valid_state(state):
	"""A state is a 3-tuple of sets (L, R,P). It is valid if not more 
		cannibals then missionaries are present"""

	left, right, pos = state
	#constraint 1 -> every person has to be somewhere and nobody 
	#can be on both banks at the same time
	if left + right != Multiset({'M' : 3, 'C' : 3}):
		return False

	#constraint 2 -> missionaries should not be eaten -> more missionaries than 
	#cannibals or only cannibals
	if left['M'] > 0 and left['M'] < left['C'] :
		return False

	if right['M'] >0 and right['M'] < right['C'] :
		return False
		
	return True

def make_move(state, operator):
	left, right, position = state
	toMove, direction = operator  

 	if direction == 'right':
		toRet = (left-toMove, right+toMove,'right')
		return toRet
	if direction == 'left':
		toRet = (left+toMove, right-toMove,'left')
		return toRet
 
def is_valid_move(state, operator):
	
	passengers, direction = operator
	left, right, position = state

	#check if boat is on the correct bank and the direction is the other bank
	if direction == 'right' and position == 'left':
		#bring the passengers from one bank to the other
		left = left - passengers
		right = right + passengers
		#check if the passengers were available at the corresponding bank
		if left['M'] >= 0 and left['C'] >= 0 and right['C'] >= 0 and \
		right['M'] >= 0:
			return True

	#check if boat is on the correct bank and the direction is the other bank
	if direction == 'left' and position == 'right':
		#bring the passengers from one bank to the other
		left = left + passengers
		right = right - passengers
		#check if the passengers were available at the corresponding bank
		if left['M'] >= 0 and left['C'] >= 0 and right['C'] >= 0 and \
		right['M'] >= 0:
			return True

	return False

def valid_successors(state):
	succ = []
	#check for every possible operator
	for op in operators:
		#do the move
		next_state = make_move(state, op)
		#check if the move is valid and leads to a valid state
		if is_valid_move(state, op) and is_valid_state(next_state):
			succ.append((next_state, op))
	#succ holds all valid successors 
	return succ

#check if two states are equal
def check_states_are_equal(first_state, second_state):
	left_first , right_first , position_first = first_state
	left_second , right_second, position_second = second_state

	#check boat possition
	if position_first == position_second:
		#check for missionaries
		if left_first['M'] == left_second['M'] and \
		right_first['M'] == right_second['M']:
			#check for cannibals
			if left_first['C'] == left_second['C'] and \
			right_first['C'] == right_second['C']:
				return True
	return False
#check if state is conatained in state-listd
def check_contains_state(state, search_list):
	for s in search_list:
		if check_states_are_equal(state,s):
			return True
	return False

# some print functions

def print_multiset(multiset):
	return "M: " + str(multiset['M']) + " C: " + str(multiset['C'])

def print_state(state):
	left, right, position = state
	return str(print_multiset(left).ljust(13)+
		print_multiset(right).ljust(13)+position).ljust(32)

def print_operator(operator):
	passengers, direction = operator
	return str(print_multiset(passengers).ljust(12)+
		direction).ljust(20)


#start of the search
humans = Multiset({'M' : 3, 'C' : 3})

# a state is #persons left, #persons right and the position of the boat
initial_state = (humans,Multiset({'M' : 0, 'C' : 0}),'left')
goal_state = (Multiset({'M' : 0, 'C' : 0}),humans,'right')


#all possible states
all_states = [(L, R ,P) 
	for L in powerset(humans) 
	for R in powerset(humans) 
	for P in {'left','right'}]

#all valid states
valid_states = [state 
	for state in all_states if is_valid_state(state)]

#print "VALID SUBSETS:\n"
#print "\n".join(str(v) for v in valid_states) 

#all possible boat configurations
boat = [Multiset({'M' : 1 ,'C' : 0 }),
		Multiset({'M' : 0 ,'C' : 1 }),
		Multiset({'M' : 0 ,'C' : 2 }),
		Multiset({'M' : 1 ,'C' : 1 }),
		Multiset({'M' : 2 ,'C' : 0 })]

#all possible operators
operators = [(passengers,direction)
				for passengers in boat
				for direction in {'left','right'}]

#print "\nOPERATORS:"
#print "\n".join(str(o) for o in operators)


# courtesy of Michael Voelske and Johannes Kiesel ;)
queue = [([initial_state], [])]

# the solutions we find go here
solutions = []

while len(queue) > 0:
	# do BFS: take first element from queue:
	visited, oplist = queue.pop(0)
	# last visited is current state:
	current_state = visited[-1]
	for new_state, op in valid_successors(current_state):
		new_visited = visited + [new_state]
		new_oplist = oplist + [op]
		#check if the states are equal
		if check_states_are_equal(new_state,goal_state):
			solutions.append((new_visited, new_oplist))
		elif not check_contains_state(new_state, visited):
			queue.append((new_visited, new_oplist))

#print solutions in a table
for i in range(len(solutions)):
	print "Solution #" + str(i+1)
	#a real long print command for the headers
	print "Starting-State".center(32) +"|".center(5) + \
		"Operator applied".center(20)+"|".center(5) + \
		"Resulting-State".center(32) 
	#the second header
	print "left bank".ljust(13) + "right bank".ljust(13) + "boat".ljust(6) + \
		"|".center(5) + "passengers".ljust(12)+ "direction".ljust(8) + \
		"|".center(3) +"left bank".ljust(13) + "right bank".ljust(13) + \
		"boat".ljust(11)
	#the underline
	print '='*93
	#the actual content of the solution
	for s in range(len(solutions[i][0])-1):
		print print_state(solutions[i][0][s]) + "|".center(5) + \
			print_operator(solutions[i][1][s]).ljust(20) + "|".center(5) + \
			print_state(solutions[i][0][s+1])
	print print_state(solutions[i][0][-1]) + "\n"
