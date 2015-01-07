import copy
from collections import deque
import time, threading
import numpy

boardsize = 3
states = []
processed = 0
class Node(object):
	
	matrix = numpy.zeros((boardsize,boardsize))
	predecessors = []
	successors = []
	nodetype = None
	goalnode = 0
	cost = -1
	def __init__(self,mat, pred, t):
		self.matrix = mat
		self.predecessors = pred
		self.nodetype = t

	def __eq__(self, other):
		if isinstance(other,Node):
			return self.matrix == other.matrix
		return NotImplemented
	
	def __ne__(self,other):
		if isinstance(other.Node):
			return self.matrix != other.matrix
		return NotImplemented

	def __str__(self):
		return "\n".join(str(elements) for elements in self.matrix)

def valid_operators(state):
	valid_operators = []
	for row in range(0,len(state.matrix)):
		for column in range(0,len(state.matrix[row])):
			if state.matrix[row][column] == 0:
				current_player = -1
				# nodetype == OR-Node ?
				if state.nodetype == 0:
					current_player = 1

				valid_operators.append((row,column,current_player))

	#print valid_operators
	return valid_operators

def apply_operator(state,operator):
	to_return = copy.deepcopy(state)
	to_return.nodetype = not(to_return.nodetype)
	to_return.matrix[operator[0]][operator[1]] = operator[2]

	already_contained = False
	for element in states:
		if element == to_return:
			to_return = element
			already_contained = True

	to_return.predecessors.append(state)
	if not(already_contained):
			states.append(to_return)

	return to_return

def check_node(state):
	for line in state.matrix:

		sum_line = sum(line) 
		
		if sum_line == boardsize:
			return 1
		elif sum_line == -boardsize:
			return -1
	

	for inner in range(0,boardsize):
		sum_column = 0
		for outer in range(0,boardsize):
			sum_column += state.matrix[outer][inner]

		if sum_column == boardsize:
			return 1
		elif sum_column == - boardsize:
			return -1

	return 0

def propagate_costs(node):
	
	for p in node.predecessors:
		
		if p.cost >= 0:
			if p.nodetype == 0:
				p.cost = min(p.cost, node.cost)
			else:
				p.cost = max(p.cost, node.cost)
		else:
			p.cost = node.cost
		propagate_costs(p)


def build_graph(node):
	global processed
	if len(valid_operators(node)) > 0:
		visited_win = False
		operators = valid_operators(node)
		next_nodes = []
		for op in operators :
			next_node = apply_operator(node,op)
			processed +=1 
			node.successors.append(next_node)
			
			next_nodes.append(next_node)

			if check_node(next_node) != 0:
				node.goalnode = check_node(next_node)
				if node.goalnode < 0:
					node.cost = 2
					visited_win = True
				elif node.goalnode > 0:
					node.cost = 0
					visited_win = True
				#propagate_costs(next_node)

		if visited_win == False:
				for node in next_nodes:
					build_graph(node)
	else:
		node_state = check_node(node)
		if node_state == -1:
			node.cost = 2
		elif node_state == 1:
			node.cost = 0
		else:
			node.cost = 1

def build_graph_2(node):
	q = deque([])
	q.append(node)

	while len(q) > 0:
		current_node = q.popleft()
		vo = valid_operators(current_node)
		for op in vo:
			q.append(apply_operator(current_node,op))
		#print len(q)
	#print "Finish\n"

def print_stuff():
	global processed
	print processed
	threading.Timer(3,print_stuff).start()


field = [[0 for x in range(boardsize)] for x in range(boardsize)]

s = Node(copy.deepcopy(field),[],0)

current_node = s

states.append(s)

print_stuff()
build_graph(s)
print processed
print states





