#!/usr/bin/python3


import math
import numpy as np
import random
import time



class TSPSolution:
	def __init__( self, listOfCities):
		self.route = listOfCities
		self.cost = self._costOfRoute()
		#print( [c._index for c in listOfCities] )

	def _costOfRoute( self ):
		cost = 0
		last = self.route[0]
		for city in self.route[1:]:
			cost += last.costTo(city)
			last = city
		cost += self.route[-1].costTo( self.route[0] )
		return cost

	def enumerateEdges( self ):
		elist = []
		c1 = self.route[0]
		for c2 in self.route[1:]:
			dist = c1.costTo( c2 )
			if dist == np.inf:
				return None
			elist.append( (c1, c2, int(math.ceil(dist))) )
			c1 = c2
		dist = self.route[-1].costTo( self.route[0] )
		if dist == np.inf:
			return None
		elist.append( (self.route[-1], self.route[0], int(math.ceil(dist))) )
		return elist


def nameForInt( num ):
	if num == 0:
		return ''
	elif num <= 26:
		return chr( ord('A')+num-1 )
	else:
		return nameForInt((num-1) // 26 ) + nameForInt((num-1)%26+1)








class Scenario:

	HARD_MODE_FRACTION_TO_REMOVE = 0.20 # Remove 20% of the edges

	def __init__( self, city_locations, difficulty, rand_seed ):
		self._difficulty = difficulty

		if difficulty == "Normal" or difficulty == "Hard":
			self._cities = [City( pt.x(), pt.y(), \
								  random.uniform(0.0,1.0) \
								) for pt in city_locations]
		elif difficulty == "Hard (Deterministic)":
			random.seed( rand_seed )
			self._cities = [City( pt.x(), pt.y(), \
								  random.uniform(0.0,1.0) \
								) for pt in city_locations]
		else:
			self._cities = [City( pt.x(), pt.y() ) for pt in city_locations]


		num = 0
		for city in self._cities:
			#if difficulty == "Hard":
			city.setScenario(self)
			city.setIndexAndName( num, nameForInt( num+1 ) )
			num += 1

		# Assume all edges exists except self-edges
		ncities = len(self._cities)
		self._edge_exists = ( np.ones((ncities,ncities)) - np.diag( np.ones((ncities)) ) ) > 0

		if difficulty == "Hard":
			self.thinEdges()
		elif difficulty == "Hard (Deterministic)":
			self.thinEdges(deterministic=True)

	def getCities( self ):
		return self._cities


	def randperm( self, n ):				#isn't there a numpy function that does this and even gets called in Solver?
		perm = np.arange(n)
		for i in range(n):
			randind = random.randint(i,n-1)
			save = perm[i]
			perm[i] = perm[randind]
			perm[randind] = save
		return perm

	def thinEdges( self, deterministic=False ):
		ncities = len(self._cities)
		edge_count = ncities*(ncities-1) # can't have self-edge
		num_to_remove = np.floor(self.HARD_MODE_FRACTION_TO_REMOVE*edge_count)

		can_delete	= self._edge_exists.copy()

		# Set aside a route to ensure at least one tour exists
		route_keep = np.random.permutation( ncities )
		if deterministic:
			route_keep = self.randperm( ncities )
		for i in range(ncities):
			can_delete[route_keep[i],route_keep[(i+1)%ncities]] = False

		# Now remove edges until 
		while num_to_remove > 0:
			if deterministic:
				src = random.randint(0,ncities-1)
				dst = random.randint(0,ncities-1)
			else:
				src = np.random.randint(ncities)
				dst = np.random.randint(ncities)
			if self._edge_exists[src,dst] and can_delete[src,dst]:
				self._edge_exists[src,dst] = False
				num_to_remove -= 1




class City:
	def __init__( self, x, y, elevation=0.0 ):
		self._x = x
		self._y = y
		self._elevation = elevation
		self._scenario	= None
		self._index = -1
		self._name	= None

	def setIndexAndName( self, index, name ):
		self._index = index
		self._name = name

	def setScenario( self, scenario ):
		self._scenario = scenario

	''' <summary>
		How much does it cost to get from this city to the destination?
		Note that this is an asymmetric cost function.
		 
		In advanced mode, it returns infinity when there is no connection.
		</summary> '''
	MAP_SCALE = 1000.0
	def costTo( self, other_city ):

		assert( type(other_city) == City )

		# In hard mode, remove edges; this slows down the calculation...
		# Use this in all difficulties, it ensures INF for self-edge
		if not self._scenario._edge_exists[self._index, other_city._index]:
			return np.inf

		# Euclidean Distance
		cost = math.sqrt( (other_city._x - self._x)**2 +
						  (other_city._y - self._y)**2 )

		# For Medium and Hard modes, add in an asymmetric cost (in easy mode it is zero).
		if not self._scenario._difficulty == 'Easy':
			cost += (other_city._elevation - self._elevation)
			if cost < 0.0:
				cost = 0.0					# Shouldn't it cost something to go downhill, no matter how steep??????


		return int(math.ceil(cost * self.MAP_SCALE))


class CityCluster:
	"""
	Note: Only works for clusters of 3+ cities! (Maybe 2+?)
	"""
	def __init__(self, route: list):
		self.route = route
		self.avg_x = 0.
		self.avg_y = 0.
		self.avg_elev = 0.

		# Optimization: use merged cities' averages
		for city in route:
			self.avg_x += city._x
			self.avg_y += city._y
			self.avg_elev += city._elevation
		self.avg_x /= len(route)
		self.avg_y /= len(route)
		self.avg_elev /= len(route)

	def _avg_distance_to(self, city, other_node):
		cost = math.sqrt( (other_node.avg_x - city._x)**2 +
		                  (other_node.avg_y - city._y)**2 )

		cost += (other_node.avg_elev - city._elevation)
		if cost < 0.0:
			cost = 0.0

		return int(math.ceil(cost * 1000.0))

	def shortest_path_between_cluster(self, other_node):
		# 1 ---> 2
		# 4 <--- 3
		cities = sorted(self.route.copy(), key=lambda c: self._avg_distance_to(c, other_node))
		for city_1 in cities:
			other_cities = sorted(other_node.route.copy(), key=lambda c: city_1.costTo(c))
			for city_2 in other_cities:
				city_3 = other_node.route[(other_node.route.index(city_2) - 1) % len(other_node.route)]
				city_4 = self.route[(self.route.index(city_1) + 1) % len(self.route)]

				if city_1.costTo(city_2) < np.inf and city_3.costTo(city_4) < np.inf:
					return [city_1, city_2]

		return None

	def merge_with(self, other_node):

		path_to_other = self.shortest_path_between_cluster2(other_node)
		if path_to_other is None:
			return None

		new_route = []
		for city in self.route:
			new_route.append(city)
			if city is path_to_other[0]:
				o_route = other_node.route
				o_start_idx = o_route.index(path_to_other[1])
				for i in range(len(o_route)):
					new_route.append(o_route[(o_start_idx + i) % len(o_route)])

		return CityCluster(new_route)

	def shortest_path_between_cluster2(self, other_cluster):
		minCost = np.inf
		minCity1 = None
		minCity2 = None
		for city1 in self.route:
			for city2 in other_cluster.route:
				city3 = other_cluster.route[(other_cluster.route.index(city2) - 1) % len(other_cluster.route)]
				city4 = self.route[(self.route.index(city1) + 1) % len(self.route)]
				cost = city1.costTo(city2) + city3.costTo(city4) - city1.costTo(city4) - city3.costTo(city2)
				if cost < minCost:
					minCost = cost
					minCity1 = city1
					minCity2 = city2
		if minCost < np.inf:
			return [minCity1, minCity2]
		else:
			return None
		



