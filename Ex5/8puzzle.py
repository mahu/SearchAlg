import copy
import time
import threading
import bisect
import numpy
import sys
import os
import time
import random
import ast
from optparse import OptionParser

#State of a 8-Puzzle
class State:

	mMatrix =[[]]
	mZeroPosition = None
	mParent = None
	mChildren = []
	mCostsG = 0
	mCostsH = 0
	mCosts = 0

	def __init__(self,mat,zero_pos,costs):
		self.mMatrix = mat
		self.mZeroPosition = zero_pos
		self.mCostsG = costs

	def __str__(self):
		return "\n".join(str(elements)for elements in self.mMatrix)

	def __eq__(self,other):
		if isinstance(other,State):
			return self.mMatrix == other.mMatrix
		return NotImplemented

	def __ne__(self,other):
		if isinstance(other,State):
			return self.mMatrix != other.mMatrix
		return NotImplemented
	
	def __lt__(self,other):
		return self.mCosts < other.mCosts

	def __le__(self,other):
		return self.mCosts <= other.mCosts
	
	def __gt__(self,other):
		return self.mCosts > other.mCosts
	
	def __ge__(self,other):
		return self.mCosts >= other.mCosts

	def set_costs(self,costsH):
		if self.mCostsG > self.mParent.mCostsG:
			self.mCostsH = costsH
			self.mCosts = self.mCostsH + self.mCostsG
		else:
			raise ValueError("Error successor has same costs like parent")


#determine the valid operators of the current state
def valid_operators(state):

	neighbors = []
	zero_pos = state.mZeroPosition

	# puzzle borders/boundary
	if(zero_pos[0] == 0):

		neighbors.append((state.mMatrix[zero_pos[0]+1][zero_pos[1]],'N'))

	elif(zero_pos[0] == 2):

		neighbors.append((state.mMatrix[zero_pos[0]-1][zero_pos[1]],'S'))

	else:
		neighbors.append((state.mMatrix[zero_pos[0]+1][zero_pos[1]],'N'))
		neighbors.append((state.mMatrix[zero_pos[0]-1][zero_pos[1]],'S'))


	if(zero_pos[1] == 0):

		neighbors.append((state.mMatrix[zero_pos[0]][zero_pos[1]+1],'W'))

	elif(zero_pos[1] == 2):

		neighbors.append((state.mMatrix[zero_pos[0]][zero_pos[1]-1],'E'))

	else:
		neighbors.append((state.mMatrix[zero_pos[0]][zero_pos[1]+1],'W'))
		neighbors.append((state.mMatrix[zero_pos[0]][zero_pos[1]-1],'E'))
		
	#print (neighbors)
	return neighbors

#apply all valid operators to the current state to get the successors
def expand_state(state):

	global heuristic_function

	op = valid_operators(state)

	newStates = []

	for o in op:
		
		newState = copy.deepcopy(state)
		newState.mCostsH=0
		newState.mMatrix[newState.mZeroPosition[0]][newState.mZeroPosition[1]] = o[0]

		if o[1] == 'N':
			newState.mMatrix[newState.mZeroPosition[0]+1][newState.mZeroPosition[1]] = 0
			newState.mZeroPosition = (newState.mZeroPosition[0]+1,newState.mZeroPosition[1])
		elif o[1] == 'S':
			newState.mMatrix[newState.mZeroPosition[0]-1][newState.mZeroPosition[1]] = 0
			newState.mZeroPosition = (newState.mZeroPosition[0]-1,newState.mZeroPosition[1])
		elif o[1] == 'W':
			newState.mMatrix[newState.mZeroPosition[0]][newState.mZeroPosition[1]+1] = 0
			newState.mZeroPosition = (newState.mZeroPosition[0],newState.mZeroPosition[1]+1)
		elif o[1] == 'E':
			newState.mMatrix[newState.mZeroPosition[0]][newState.mZeroPosition[1]-1] = 0
			newState.mZeroPosition = (newState.mZeroPosition[0],newState.mZeroPosition[1]-1)
		else:
			raise ValueError("Undefined Operator: Unknown cardinal direction!")

		newState.mParent = state
		newState.mCostsG += 1;
		
		heuristic_function(newState)

		newStates.append(newState)


	state.mChildren.append(newStates)
	
	return newStates

def find_min():

	global OPEN , OPEN_Hash,CLOSED_Hash,CLOSED

	#OPEN is sorted so the first element is the cheapest
	min_state = OPEN[0]
	del OPEN[0]
	OPEN_Hash.pop(str(min_state),None) 
	
	#the minimal state is added to CLOSED
	CLOSED.append(min_state)
	CLOSED_Hash[str(min_state)] = min_state

	return min_state

def node_equal_state(state):
	
	global CLOSED_Hash , OPEN_Hash
	
	if str(state) in OPEN_Hash:
		return True

	if str(state) in CLOSED_Hash:
		return True

	return False

def calc_h0(state):
	#h0 provide no knowledge about the rest problem
	state.set_costs(0)		

def calc_h1(state):

	error = 0
	for r in range(0,len(state.mMatrix)):
		for c in range(0,len(state.mMatrix[r])):
			#0-tile will not count in the error
			if (state.mMatrix[r][c] != 0) and (state.mMatrix[r][c] != goal_state.mMatrix[r][c]):
				error+=1

	state.set_costs(error)

def calc_h2(state):

	error = 0
	testDict = {}
	#build a dictionary with the positions of the tiles in the current state
	for r in range(0,len(state.mMatrix)):
		for c in range(0,len(state.mMatrix[r])):
			toTest = state.mMatrix[r][c]
			testDict[toTest]=(r,c)

	#subtract the dictionary from the groundtruth --> correct tiles have a (0,0) incorrect the manhattan distance
	difference_dictionary = {key: tuple(numpy.subtract(testDict[key],groundTruth.get(key, 0))) for key in testDict.keys()}

	#sum the errors
	for e in difference_dictionary.values():
		error += abs(e[0])+abs(e[1])	
	
	
	state.set_costs(error)

#thread to give feedback about the search
def give_information():
	global oldNumber , startTime, info_thread
	#calculate elapsed time
	m,s = divmod(time.time()-startTime,60)
	h,m = divmod(m,60)
	timestring = "%02d:%02d:%02d" % (h,m,s)
	#overwrite the line with blanks to erase the last line
	sys.stdout.write("\r"+170*" ")
	sys.stdout.flush()
	#provide information about the search
	sys.stdout.write("\rTime elapsed: " + timestring + "\tNodes expanded: " + str(len(CLOSED)) + "\tNodes in OPEN: " + str(len(OPEN)) + "\tNodes/s: " + str(len(CLOSED)-oldNumber))
	sys.stdout.flush()
	oldNumber = len(CLOSED)
	#restart the thread in 1 second
	info_thread = threading.Timer(1,give_information)
	info_thread.start()

def check_sovable(state):

	linear = []
	inversions = 0
	for r in range(0,len(state.mMatrix)):
		for c in range(0,len(state.mMatrix[r])):
			if(state.mMatrix[r][c] > 0 ):
				linear.append(state.mMatrix[r][c])

	for i in range(0,len(linear)):
		for j in range(i+1,len(linear)):
			if linear[i]>linear[j]:
				inversions+=1
	print inversions
	#if number of inversions is odd, the state is not solvable
	return (not(inversions%2))

#parse a state from a file and check if the state is correct
def parse_state(filename):
	stateMatrix = None
	with open(filename,'r') as f:
		stateMatrix = f.read()
		stateMatrix = ast.literal_eval(stateMatrix)

	zero_pos = None
	number_of_elements = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0}
	for r in range(0,len(stateMatrix)):
		for c in range(0,len(stateMatrix[r])):
			if(stateMatrix[r][c] in number_of_elements.keys()):
				if (number_of_elements[stateMatrix[r][c]] == 0):
						number_of_elements[stateMatrix[r][c]] += 1
						if(stateMatrix[r][c] == 0):
							zero_pos = (r,c)
				else:
					raise ValueError("Invalid State, found two entries for " + str(stateMatrix[r][c]))
			else:
				raise ValueError("Invalid State, unknown tile found: " + str(stateMatrix[r][c]))

	return State(stateMatrix,zero_pos,0)

#_sorted_ open and closed list
OPEN = []
CLOSED = []

#hash_table (dictionary) for already visited states
OPEN_Hash = {}
CLOSED_Hash = {}


state_number = 0
oldNumber = 0
startTime = time.time()

#dictionary with the positions (values) of the tiles (keys) of the goal state
groundTruth = {0:(2,2),1:(0,0),2:(0,1),3:(0,2),4:(1,0),5:(1,1),6:(1,2),7:(2,0),8:(2,1)}

#provide information about the search
info_thread = None

#cmd-parameters
usage = "usage: %prog [options]"
parser = OptionParser(usage)

parser.add_option("-o", "--output", action="store", type= "string",dest="filename",
	default="", help="file for result")
parser.add_option("-u", "--heuristic" , action="store", type= "int",dest="heuristic", 
	default=0, help="determine which heuristic to take (0,1,2)")
parser.add_option("-s", "--state" , action="store", type= "string",dest="start_state_file", 
	default="s1.txt", help="file which contains the startstate")

(options,args) = parser.parse_args()

#input parameter
filename = options.filename
heuristic = options.heuristic
start_state_file = options.start_state_file

state_name = os.path.splitext(start_state_file)[0]
#default filename
if filename == "":
	filename = "8_Puzzle_" + state_name + "_H"+str(heuristic)+".txt"

#if filename already exist -> don't overwrite, just add a random number
if os.path.isfile(filename):
	filename = "8_Puzzle_S1_H"+str(heuristic)+"_"+str(random.randint(10,99)) + ".txt"


#determine which heuristic to take
heuristic_function = None
if heuristic == 0:
	heuristic_function= calc_h0
elif heuristic == 1:
	heuristic_function= calc_h1
elif heuristic == 2:
	heuristic_function= calc_h2
else:
	raise ValueError("Unknown Heuristic " + str(heuristic))



#start state
startstate = parse_state(start_state_file)
if not(check_sovable(startstate)):
	print "Start state not solvable, exit."
	exit()
else:
	print "Start search with state:\n" + str(startstate)+ "\nFound Zero on " + str(startstate.mZeroPosition)
	print "Save results in \"" +filename+"\""

outputFile = open(filename,'w')

goal_state = State([[1,2,3],[4,5,6],[7,8,0]],(2,2),0)

#insert start state to OPEN
OPEN.append(startstate)
OPEN_Hash[str(startstate)] = startstate

give_information()

# A* algorithm
try:
	while True:
		#no state in OPEN -> A* failed
		if len(OPEN) == 0:
			print("FAILED with empty OPEN list!")
			info_thread.cancel()
			exit()

		#get the minimum state
		min_state = find_min()
		#we took a goal state from OPEN -> finish
		if min_state == goal_state:
			#time elapsed
			m,s = divmod(time.time()-startTime,60)
			h,m = divmod(m,60)
			timestring = "%02d:%02d:%02d" % (h,m,s)

			print("\nGoal state found!")
			tmp_state = min_state
			print (str(tmp_state)+"\n")
			#write results to file
			outputFile.write("Nodes expanded: " + str(len(CLOSED))+"\n\n")
			outputFile.write("Elapsed time: " + timestring+ "\n\n")
			outputFile.write(str(tmp_state)+"\n\n")
			#write states from goal to start state
			while tmp_state.mParent != None:
				tmp_state = tmp_state.mParent
				print (str(tmp_state)+"\n")
				outputFile.write(str(tmp_state)+"\n\n")
			#how many states where expanded
			print len(CLOSED)
			#clean-up
			info_thread.cancel()
			outputFile.close()
			exit()

		#expand the state and get the successors
		successors = expand_state(min_state)

		for s in successors:
			#if state was already processed, this time would be more expensive
			#-> only take states which are not processed yet
			if node_equal_state(s) == False:
				bisect.insort_right(OPEN,s)
				OPEN_Hash[str(s)]= s
	
except KeyboardInterrupt:
	print("\n")
	outputFile.close()
	info_thread.cancel()
	exit()
