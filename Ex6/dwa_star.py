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
		
		calc_dynamic_heuristic(newState)

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

def calc_dynamic_heuristic(state):
	calc_h2(state)
	calc_eps_h(state)


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

def calc_eps_h(state):
	global N , epsilon
	state.mCosts = state.mCostsG + (1.0+(1.0-((min(state.mCostsG,N)/N)*epsilon)))*state.mCostsH

	#print state.mCosts

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


def search(startstate,filename):

	global OPEN, OPEN_Hash, CLOSED, CLOSED_Hash, startTime
	
	OPEN.append(startstate)
	OPEN_Hash[str(startstate)] = startstate

	startTime = time.time()

	try:
		outputFile = open(filename,'w')
		while True:
			#no state in OPEN -> A* failed
			if len(OPEN) == 0:
				print("FAILED with empty OPEN list!")
				return

			#get the minimum state
			min_state = find_min()
			#we took a goal state from OPEN -> finish
			if min_state == goal_state:
				steps = 0
				#time elapsed
				m,s = divmod(time.time()-startTime,60)
				h,m = divmod(m,60)
				timestring = "%02d:%02d:%02d" % (h,m,s)

				print("\nGoal state found!")
				tmp_state = min_state
				#print (str(tmp_state)+"\n")
				#write results to file
				outputFile.write("Nodes expanded: " + str(len(CLOSED))+"\n\n")
				outputFile.write("Elapsed time: " + timestring+ "\n\n")
				outputFile.write(str(tmp_state)+"\n\n")
				#write states from goal to start state
				while tmp_state.mParent != None:
					tmp_state = tmp_state.mParent
					#print (str(tmp_state)+"\n")
					steps += 1
					outputFile.write(str(tmp_state)+"\n\n")
				#how many states where expanded
				print len(CLOSED)
				#clean-up
				outputFile.close()
				return (len(CLOSED) , steps)

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
		exit()
	




#dictionary with the positions (values) of the tiles (keys) of the goal state
groundTruth = {0:(2,2),1:(0,0),2:(0,1),3:(0,2),4:(1,0),5:(1,1),6:(1,2),7:(2,0),8:(2,1)}

#provide information about the search
info_thread = None

#cmd-parameters
usage = "usage: %prog [options]"
parser = OptionParser(usage)

parser.add_option("-o", "--output", action="store", type= "string",dest="filename",
	default="", help="file for result")
parser.add_option("-s", "--state" , action="store", type= "string",dest="start_state_file", 
	default="s1.txt", help="file which contains the startstate")
parser.add_option("-n", "--depth" , action="store", type= "int",dest="depth", 
	default=5, help="determine the anticipated depth of the desired goal node")
parser.add_option("-e", "--epsilon" , action="store", type= "float",dest="epsilon", 
	default=1.0, help="determine the epsilon for weighted f-function")
parser.add_option("-a", "--all" , action="store_true", dest="search_all", 
	default=False, help="search for every combination or not")



(options,args) = parser.parse_args()

#input parameter
filename = options.filename
start_state_file = options.start_state_file
N = options.depth
epsilon = options.epsilon
searchAll = options.search_all

state_name = os.path.splitext(start_state_file)[0]



#start state
startstate = parse_state(start_state_file)
if not(check_sovable(startstate)):
	print "Start state not solvable, exit."
	exit()
else:
	print "Start search with state:\n" + str(startstate)+ "\nFound Zero on " + str(startstate.mZeroPosition)
	print "Save results in \"" +filename+"\""


goal_state = State([[1,2,3],[4,5,6],[7,8,0]],(2,2),0)

#insert start state to OPEN

#_sorted_ open and closed list
OPEN = []
CLOSED = []

#hash_table (dictionary) for already visited states
OPEN_Hash = {}
CLOSED_Hash = {}

if searchAll:
	try:
		allFile = open("all_results.txt",'w')
		eps_list = [0.125,0.25,0.5,1.0,2.0]
		for tmpN in range(5,51,5):
			for tmpEps in eps_list:

				del OPEN[:]
				del CLOSED[:]
				OPEN_Hash.clear()
				CLOSED_Hash.clear()

				N = tmpN
				epsilon = tmpEps
				filename = "8_Puzzle_" + state_name + "_"+str(tmpN) + "_" + str(tmpEps) + "_DWA.txt"

				print "N= " + str(N) + " eps= " + str(epsilon)
				

				startTime = time.time()

				oldNumber = 0
				
				give_information()
				number , steps = search(startstate,filename)
				info_thread.cancel()

				allFile.write(str(N) + "\t" + str(epsilon) + "\t" + str(number)+  "\t" + str(steps) + "\n")
		allFile.close()

	except KeyboardInterrupt:
		print("\n")
		info_thread.cancel()
		exit()


else:
	#default filename
	if filename == "":
		filename = "8_Puzzle_" + state_name + "_"+str(N) + "_" + str(eps) + "_DWA.txt"

	OPEN = []
	CLOSED = []

	#hash_table (dictionary) for already visited states
	OPEN_Hash = {}
	CLOSED_Hash = {}

	startTime = time.time()

	oldNumber = 0
	give_information()
	search(startstate,filename)

# WDA* algorithm
info_thread.cancel()
	
