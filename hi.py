class debtonator:
	def __init__(self, testcase):
		# Initial number of people
		self.numPeople = len(testcase)

		# Initializing a copy of testcase to modify
		self.testcase = testcase

		# Initializing an adjacency list that has in-edges
		self.transpose = None

		# Number of interactions
		self.numInteractions = 0
		for entry in testcase:
			self.numInteractions += len(testcase[entry])

		self.initialInteractions = self.numInteractions

		# Net values dict
		self.netValues = {}
		for person in self.testcase:
			self.netValues[person] = 0

		# Net positive and net negative lists
		self.netPosNodes = []
		self.netNegNodes = []
		self.netZeroNodes = []

		# Result dictionary
		self.result = {}

#---------------------------------------------------HELPER FUNCTIONS---------------------------------------------------------#
	def resolveParallel(self):
		# Modifies self.testcase in-place
		# Resolve parallel
		for person in self.testcase:
			owedto = {}
			for edge in self.testcase[person]:
				if edge[0] not in owedto:
					owedto[edge[0]] = edge[1]
				else:
					owedto[edge[0]] += edge[1]
			self.testcase[person] = set()
			for entry in owedto:
				self.testcase[person].add((entry, owedto[entry]))
		# print('After resolving parallel: ', self.testcase)
		
		# Resolve anti-parallel
		for person in self.testcase:
			owedto = {}
			for edge in self.testcase[person]:
				owedto[edge[0]] = edge[1]
				for entry in list(self.testcase[edge[0]]):
					if entry[0] == person and entry[1] <= edge[1]:
						owedto[edge[0]] -= entry[1]
						self.testcase[edge[0]].remove((person, entry[1]))
			self.testcase[person] = set()
			for entry in owedto:
				self.testcase[person].add((entry, owedto[entry]))

		# print('After resolving parallels: ', self.testcase)

	def populateNetValues(self):
		# Populates self.netValues dictionary
		for person in self.testcase:
			for edge in self.testcase[person]:
				self.netValues[person] -= edge[1]
				self.netValues[edge[0]] += edge[1]
		print('Net values: ', self.netValues)


#-------------------------------------------BIPARTITE SOLVE: O(VlogV + E)---------------------------------------------#
	def createBipartite(self):
		# Takes self.netValues and creates a bipartite graph from it
		for person in self.netValues:
			if self.netValues[person] > 0:
				self.netPosNodes.append(person)
			elif self.netValues[person] < 0:
				self.netNegNodes.append(person)
			else:
				self.netZeroNodes.append(person)

		# Sorts netPosNodes and netNegNodes based on dictionary value. 
		if len(self.netPosNodes) > 1:
			self.netPosNodes.sort(key = lambda person: -1 * self.netValues[person])
		if len(self.netNegNodes) > 1:
			self.netNegNodes.sort(key = lambda person: self.netValues[person])
		print('Net zero: ', self.netZeroNodes, ' Net pos: ', self.netPosNodes, ' Net neg: ', self.netNegNodes)

	def bucketFill(self):
		# Modifies self.result in-place
		for person in self.netNegNodes:
			self.result[person] = set()

		# So we can keep track of how much we're taking out of the positive nodes
		currentTotals = self.netValues

		# Current index in netPosNodes
		posIndex = 0

		for person in self.netNegNodes:
			outSum = 0
			while outSum < -1 * self.netValues[person] and posIndex <= len(self.netPosNodes):
				if outSum + currentTotals[self.netPosNodes[posIndex]] <= -1 * self.netValues[person]:
					# Eats the entire positive node and needs more
					outSum += currentTotals[self.netPosNodes[posIndex]]
					self.result[person].add((self.netPosNodes[posIndex], currentTotals[self.netPosNodes[posIndex]]))
					# print(posIndex, self.result, person, outSum)
					currentTotals[self.netPosNodes[posIndex]] = 0
					posIndex += 1
				else:
					# Eats part of a positive node and is full
					currentTotals[self.netPosNodes[posIndex]] -= -1 * self.netValues[person] - outSum
					self.result[person].add((self.netPosNodes[posIndex], -1 * self.netValues[person] - outSum))
					outSum = -1 * self.netValues[person]
					# print(posIndex, self.result, person, outSum)

	def solveBipartite(self):
		# Returns final result
		# Fast cases
		if len(self.netNegNodes) == 1:
			self.result[self.netNegNodes[0]] = set()
			for person in self.netPosNodes:
				self.result[self.netNegNodes[0]].add((person, self.netValues[person]))
		elif len(self.netPosNodes) == 1:
			for person in self.netNegNodes:
				self.result[person] = set()
				self.result[person].add((self.netPosNodes[0], -1 * self.netValues[person]))
		elif len(self.netZeroNodes) == self.numPeople:
			return "All debts resolved."
		# Not fast cases
		else:
			self.bucketFill()
		return 'Result: '+ str(self.result)

#---------------------------------------------GRAPH TRAVERSAL SOLVE Poly(V)--------------------------------------------------#
	def graphTranspose(self):
		self.transpose = {}
		for node in self.testcase:
			for edge in self.testcase[node]:
				if edge[0] not in self.transpose:
					self.transpose[edge[0]] = set()
					self.transpose[edge[0]].add((node, edge[1]))
				else:
					self.transpose[edge[0]].add((node, edge[1]))
		# print("transpose: ", self.transpose)

	def addSupernode(self):
		'''
		In adding a supernode with 0-edges to each other node, we can
		access the whole graph with DFS. Only want to have trace of 
		supernode in self.testcase as we want to elimate unnecessary
		operations using self.transpose. 
		'''
		self.testcase[self.numPeople] = set()
		for i in range(self.numPeople):
			self.testcase[self.numPeople].add((i, 0))


	def graphTraversal(self):
		'''
		Multiple DFS's with relaxations. Source node is that with the highest net out. 
		Traverses in DFS order and relaxes: if in-edge.value > out-edge.value, reassign
		in-edge and delete out-edge. Keeps track of if the recent iteration has changed the graph,
		and if so, does another iteration. Modifies self.testcase in place.
		'''

		def relax(current):
			if current in self.transpose and len(self.testcase[current]):
				for inedge in self.transpose[current]:
					for outedge in self.testcase[current]:
						if inedge[1] >= outedge[1] and inedge[0] != outedge[0]:
							# print("relaxing")
							# reassign outedge
							self.testcase[current].remove(outedge)
							self.testcase[inedge[0]].add(outedge)

							# change inedge
							self.testcase[inedge[0]].remove((current, inedge[1]))
							if inedge[1] - outedge[1] != 0:
								self.testcase[inedge[0]].add((current, inedge[1] - outedge[1]))

							# change self.transpose[current]
							self.transpose[current].remove(inedge)
							if inedge[1] - outedge[1] != 0:
								self.transpose[current].add((inedge[0], inedge[1] - outedge[1])) 

							# change self.transpose[new edge destination]
							self.transpose[outedge[0]].remove((current, outedge[1]))
							self.transpose[outedge[0]].add((inedge[0], outedge[1]))

							# self.resolveParallel()
							return 1

						elif inedge[1] < outedge[1] and inedge[0] != outedge[0]:
							# print("relaxing")
							# reassign inedge
							self.testcase[inedge[0]].remove((current, inedge[1]))
							self.testcase[inedge[0]].add((outedge[0], inedge[1]))

							# change outedge
							self.testcase[current].remove(outedge)
							self.testcase[current].add((outedge[0], outedge[1] - inedge[1]))

							# change self.transpose[destination]
							self.transpose[outedge[0]].remove((current, outedge[1]))
							self.transpose[outedge[0]].add((current, outedge[1] - inedge[1]))
							self.transpose[outedge[0]].add(inedge)

							# change self.transpose[current]
							self.transpose[current].remove(inedge)

							# self.resolveParallel()
							return 1

			# print('nothing to relax')
			return 0

		# Preset indicator to 1 so we can enter the while loop
		indicator = 1

		while indicator:
			# Add supernode
			self.addSupernode()

			# Initialize source, visited, and stack
			source = self.numPeople 
			# print(source)
			visited, stack = set(), [source]
			# print(stack)

			# Set indicator to 0 so we can update it each time we do DFS
			indicator = 0

			# DFS
			while stack:
				vertex = stack.pop()
				# print("currently on vertex: ", vertex)
				# relax here
				if vertex != source:
					# indicator gets updated here
					while relax(vertex) == 1:
						indicator = 1

					# print('Updated: ', self.testcase)

				if vertex not in visited:
					visited.add(vertex)
					for node in self.testcase[vertex]:
						if node[0] not in visited and node[0] not in stack:
							stack.append(node[0])
			# print("rerun?: ", indicator)
			# print('visited: {}'.format(visited))
			# print("ok")

		self.resolveParallel()
		self.testcase.pop(source)
		print("final: ", self.testcase)

#-----------------------------------------------RETURN STRING GENERATORS---------------------------------------------#
	def finalNumInteractions(self):
		# Modifies self.result in-place
		self.initialInteractions = self.numInteractions
		self.numInteractions = 0
		for person in self.result:
			self.numInteractions += len(self.result[person])
		return 'Number of transactions is {}, which is {}% less than there were initially.'.format(self.numInteractions,
			(self.initialInteractions - self.numInteractions)/self.initialInteractions * 100)

	def strictLowerBound(self):
		return 'Strict lower bound: {} transaction(s). \nBenchmark: {} transaction(s)'.format(max(len(self.netPosNodes
			), len(self.netNegNodes)), self.numPeople - 1)

#--------------------------------------------------------MAIN: BIPARTITE-------------------------------------------------------------#
	def main(self):
		print('Initial transactions: ', self.numInteractions)
		print('Number of people: ', self.numPeople)
		if self.numPeople <= 1:
			return "Number of people must be greater than 1."
		elif self.numInteractions == 0:
			return "Number of interactions must be greater than 0."
		else:
			self.resolveParallel()
			self.populateNetValues()
			self.createBipartite()

			returnAlgo = self.solveBipartite() + '\n' + self.finalNumInteractions() + '\n' + self.strictLowerBound()
			returnOG = 'Result: ' + str(self.testcase) + '\n' + self.strictLowerBound()
			if '-' in returnAlgo:
				for person in range(self.numPeople):
					if len(self.testcase[person]) == 0:
						del self.testcase[person]
				returnOG = 'Result: ' + str(self.testcase) + '\n' + self.strictLowerBound()
				return returnOG
			else:
				return returnAlgo

#---------------------------------------------------MAIN: GRAPH TRAVERSAL-----------------------------------------------------------#
	def main2(self):
		print('Init transactions: ', self.numInteractions)
		print('Number of people: ', self.numPeople)
		if self.numPeople <= 1 or self.numInteractions == 0:
			pass
		else:
			self.resolveParallel()
			self.populateNetValues()
			self.graphTranspose()
			self.graphTraversal()
			for person in self.testcase:
				if len(self.testcase[person]):
					self.result[person] = self.testcase[person]
					
			print(self.finalNumInteractions())
			return self.testcase

#---------------------------------------------------------------MAIN: GUI--------------------------------------------------#
	def guimain(self):
		print('Initial transactions: ', self.numInteractions)
		print('Number of people: ', self.numPeople)

		self.resolveParallel()
		self.populateNetValues()
		self.createBipartite()
		self.solveBipartite()
		self.finalNumInteractions()
		return [self.result, self.initialInteractions, self.numInteractions, self.numPeople]