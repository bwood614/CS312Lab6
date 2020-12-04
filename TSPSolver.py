#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
from queue import PriorityQueue
import itertools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy( self,time_allowance=60.0 ):
		results = {}										# T:O(1) S:O(1)
		cities = self._scenario.getCities()					# T:O(1) S:O(1)
		ncities = len(cities)								# T:O(1) S:O(1)
		count = 0											# T:O(1) S:O(1)
		bssf = None											# T:O(1) S:O(1)
		start_time = time.time()							# T:O(1) S:O(1)
		for start_city in cities:		# T:O(n^4) S:O(n)
			if time.time() - start_time > time_allowance:	# T:O(1) S:O(1)
				break
			route = []										# T:O(1) S:O(1)
			route.append(start_city)						# T:O(1) S:O(1)
			current_city = start_city						# T:O(1) S:O(1)
			while len(route) < ncities:						# T:O(n^3) S:O(1)
				cheapest_neighbor = None					# T:O(1) S:O(1)
				cheapest_out_cost = np.inf					# T:O(1) S:O(1)
				for neighbor_city in cities:	# T:O(n^2) S:O(1)
					if neighbor_city in route or current_city.costTo(neighbor_city) == np.inf:	# T:O(n) S:O(1)
						continue
					if current_city.costTo(neighbor_city) < cheapest_out_cost:	# T:O(1) S:O(1)
						cheapest_out_cost = current_city.costTo(neighbor_city)	# T:O(1) S:O(1)
						cheapest_neighbor = neighbor_city						# T:O(1) S:O(1)
				if cheapest_neighbor is None:		# T:O(1) S:O(1)
					break
				else:
					route.append(cheapest_neighbor)		# T:O(1) S:O(1)
					current_city = cheapest_neighbor 	# T:O(1) S:O(1)
			if len(route) == ncities:					# T:O(1) S:O(1)
				solution = TSPSolution(route)			# T:O(n) S:O(n)
				count += 1								# T:O(1) S:O(1)
				if solution.cost < bssf.cost if bssf is not None else np.inf:	# T:O(1) S:O(1)
					bssf = solution						# T:O(1) S:O(1)

		end_time = time.time()
		results['cost'] = bssf.cost if bssf is not None else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results

	# returns the initial reduced cost matrix for the senario
	def getInitialState(self):		# T:O(n^2) S:O(n^2)
		cities = self._scenario.getCities() # T:O(1) S:O(1)
		state_matrix = []					# T:O(1) S:O(1)
		for i in range(len(cities)):		# T:O(n^2) S:O(n^2)
			row = []						# T:O(1) S:O(1)
			for j in range(len(cities)):								# T:O(n) S:O(n)
				row.append(cities[i].costTo(cities[j]))					# T:O(1) S:O(1)
			state_matrix.append(row)									# T:O(1) S:O(1)
		initial_state = BBState(0, [cities[0]], state_matrix, cities)	# T:O(1) S:O(n^2)
		initial_state.reduceMatrix()		# T:O(n^2) S:O(1)
		return initial_state				# T:O(1) S:O(1)

	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''
	def branchAndBound( self, time_allowance=60.0 ):
		results = {}											# T:O(1) S:O(1)
		count = 0												# T:O(1) S:O(1)
		total = 0												# T:O(1) S:O(1)
		pruned = 0												# T:O(1) S:O(1)
		max = 0													# T:O(1) S:O(1)
		# Get initial bssf
		bssf = self.greedy(time_allowance)["soln"]				# T:O(n^4) S:O(n)
		if bssf is None:    # if greedy doesnt work				# T:O(1) S:O(1)
			bssf = self.defaultRandomTour(time_allowance)["soln"]
		# Initialize Priority Queue
		pq = PriorityQueue()									# T:O(1) S:O(1)
		initial = self.getInitialState()						# T:O(n^2) S:O(n^2)
		pq.put(initial)											# T:O(logn) S:O(1)
		# Branch and Bound Algorithm
		start_time = time.time()								# T:O(1) S:O(1)
		while not pq.empty() and time.time()-start_time < time_allowance:
			if pq.qsize() > max:								# T:O(1) S:O(1)
				max = pq.qsize()								# T:O(1) S:O(1)
			currentState = pq.get()								# T:O(logn) S:O(1)
			if currentState.lower_bound < bssf.cost:			# T:O(1) S:O(1)
				children = currentState.expand()				# T:O(n^3) S:O(n^3)
				for child in children:							# T:O(n^2) S:O(n^2)
					if child.testForSolution() < bssf.cost:		# T:O(1) S:O(1)
						bssf = TSPSolution(child.route)			# T:O(n) S:O(n)
						count += 1								# T:O(1) S:O(1)
					elif child.lower_bound < bssf.cost:			# T:O(1) S:O(1)
						pq.put(child)							# T:O(logn) S:O(1)
					else:
						pruned += 1								# T:O(1) S:O(1)
					total += 1									# T:O(1) S:O(1)
			else:
				pruned += 1										# T:O(1) S:O(1)
		end_time = time.time()
		# Return result dictionary
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = max
		results['total'] = total
		results['pruned'] = pruned
		return results










	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy( self,time_allowance=60.0 ):
		pass

		



