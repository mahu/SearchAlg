#!/usr/bin/python

from optparse import OptionParser 

#Function returns the next target number, only used for testing purposes 
def next_target_number(current_number_of_sticks):
	return current_number_of_sticks - what_to_take[(current_number_of_sticks % target_steps)]

#Function returns True if the given number is a Target number in the current setting 
def is_target_number(current_number_of_sticks):
	return (current_number_of_sticks%target_steps==1)

#Recursive function to determine the winning strategy
def next_move(move_number, number_of_matchsticks):
	#check all opponent possibilities
	for opponent_move in possible_moves:
		#reset the current_number_of_sticks every iteration
		current_number_of_sticks = number_of_matchsticks;
		#the opponent move
		current_number_of_sticks -= opponent_move
		#how to react on the opponent move
		take = (what_to_take[current_number_of_sticks%target_steps])
		#did we already win?
		if current_number_of_sticks-take == 1:
			print "\t"*move_number + "move "+str(move_number)+ \
				": if opponent takes " + str(opponent_move) + " -> take " + \
				str(take) + "(You win.)"
		#or do we have to go deeper?	
		else:
			print "\t"*move_number + "move "+str(move_number)+ \
				": if opponent takes " + str(opponent_move) + " -> take " + \
				str(take) + "(" + str(current_number_of_sticks-take)+" left)"
			next_move(move_number+1,current_number_of_sticks-take)

#Just a helper function do pretty print the take-options
def print_options():
	return str(possible_moves)[1:-4] + " or " + str(possible_moves[-1])


#parser stuff
usage = "usage: %prog [options]"
parser = OptionParser(usage)

parser.add_option("-s", "--sticks", action="store", type= "int",dest="sticks",
	default=7, help="specifies the number of matchsticks on the table")
parser.add_option("-m", "--moves" , action="store", type= "int",dest="moves", 
	default=3, help="the maximum number of matchsticks a player can take away in one round")

(options,args) = parser.parse_args()

#input parameter
number_of_matchsticks = options.sticks
possible_moves = [x for x in range(1,options.moves+1)]

#steps we can perform every round
target_steps = min(possible_moves)+max(possible_moves)

#dictionary for moves to take in a certain matchstick situation
what_to_take={}
for i in possible_moves:
	what_to_take[(i+1) % target_steps]= i % target_steps

#If we start at a target number there is no winning strategy, the player has to play random
if is_target_number(number_of_matchsticks):
	print "No winning strategy available."

else:
	print str(number_of_matchsticks)+" matchsticks; players can take " + print_options()
	#perform the first move to come to the next target number
	take = what_to_take[number_of_matchsticks%target_steps]
	number_of_matchsticks -= take
	print "move 1: take " + str(take) + "(" +str(number_of_matchsticks)+" left)"
	next_move(2,number_of_matchsticks)
