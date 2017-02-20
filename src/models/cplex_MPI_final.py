# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import print_function
import numpy as np
from math import floor, fabs
import sys
import cplex
from cplex.exceptions import CplexError
import matplotlib.pyplot as plt
import pandas as pd
import multiprocessing


# example: python cplex_final.py x.csv y.csv result.csv
# X = np.loadtxt(str(sys.argv[1]))
# Y = np.loadtxt(str(sys.argv[2]))
# result = []

class cplex_CPS:
	def __init__(self, X, Y,filepath,filename):
		self.X = X
		self.Y = Y
		self.result = []
		self.filepath = filepath
		self.filename = filename

	def run_cplex(self,loc_X,loc_Y,m=30,M=50):
		N = loc_X.shape[0]
		C = []
		for i in range(N):
			c = []
			for j in range(N):
				c.append(np.sqrt((loc_X[i]-loc_X[j])**2+(loc_Y[i]-loc_Y[j])**2))
			C.append(c)
		print('Number of people for assignment')
		print(len(loc_Y))
		print('Number of potential social center')
		print(len(loc_X))
		num_facilities = len(loc_X)
		num_clients = len(loc_Y)
		model = cplex.Cplex()
		model.parameters.mip.tolerances.mipgap.set(0.2)
		model.set_log_stream(None)
		model.set_error_stream(None)
		model.set_warning_stream(None)
		model.set_results_stream(None)
		# Create one binary variable for each individual. The variables model
		# whether this individual is social center or not
		model.variables.add(obj = np.zeros(N),
							lb=[0] * num_facilities,
							ub=[1] * num_facilities,
							types=["B"] * num_facilities)
		center = []
		# for c in range(num_clients):
		#     supply.append([])
		for f in range(num_facilities):
			center.append(f)
		# Create one binary variable for each facility/client pair. The variables
		# model whether a client is served by a facility.

		for c in range(num_clients):
			model.variables.add(obj=C[c],
								lb=[0] * num_facilities,
								ub=[1] * num_facilities,
								types=["B"] * num_facilities)

		# Create corresponding indices for later use
		supply = []
		for c in range(num_clients):
			supply.append([])
			for f in range(num_facilities):
				supply[c].append((c + 1) * (num_facilities) + f)
		# Each client must be assigned to exactly one location
		for c in range(num_clients):
			assignment_constraint = cplex.SparsePair(ind=[supply[c][f] for f in
														  range(num_facilities)],
													 val=[1.0] * num_facilities)
			model.linear_constraints.add(lin_expr=[assignment_constraint],
										 senses=["E"],
										 rhs=[1])
		# The number of clients assigned to a facility must be less than the
		# capacity of the facility, and clients must be assigned to an open
		# facility
		for f in range(num_facilities):
			index = [f]
			value = [-M*center[f]]
			for c in range(num_clients):
				index.append(supply[c][f])
				value.append(1.0*center[f])
			capacity_constraint = cplex.SparsePair(ind=index, val=value)
			model.linear_constraints.add(lin_expr=[capacity_constraint],
										 senses=["L"],
										 rhs=[0])   
		for f in range(num_facilities):
			index = [f]
			value = [-m*center[f]]
			for c in range(num_clients):
				index.append(supply[c][f])
				value.append(1.0*center[f])
			capacity_constraint = cplex.SparsePair(ind=index, val=value)
			model.linear_constraints.add(lin_expr=[capacity_constraint],
										 senses=["G"],
										 rhs=[0])
		# Our objective is to minimize cost. Fixed and variable costs
		# have been set when variables were created.
		model.objective.set_sense(model.objective.sense.minimize)
		model.solve()  
		solution = model.solution
		C = solution.get_values()[0:300]
		# print(sum(C))
		Z = solution.get_values()[300:90300]
		# print(sum(Z))
		Z = np.array(Z)
		Z = np.reshape(Z, (300,300))
		return C,Z

	def worker(self,loc_X,loc_Y,send_end):
		'''worker function'''
		C,Z = self.run_cplex(loc_X,loc_Y)
		result = [C,Z,loc_X,loc_Y]
		print('parallel')
		send_end.send(result)

	def parallel(self):
		jobs = []
		pipe_list = []
		for i in xrange(len(self.X)/300):
			recv_end, send_end = multiprocessing.Pipe(False)
			loc_X = self.X[i*300:(i+1)*300]
			loc_Y = self.Y[i*300:(i+1)*300]
			p = multiprocessing.Process(target=self.worker, args=(loc_X,loc_Y, send_end))
			jobs.append(p)
			pipe_list.append(recv_end)
			p.start()

		print('check step 1')
		for proc in jobs:
			proc.join()
			print('done')
		print('check step 2')
		result_list = [x.recv() for x in pipe_list]
		print('check step 3')
		for result in result_list:
			self.result.append(result)
		print('check step 4')
	

	def create_DF(self):
		C = np.zeros(len(self.X))
		total_commmunities = 0
		for i in xrange(len(self.X)/300):
			c = self.result[i][2]
			z = self.result[i][3]
			count = 0
			for j in range(len(c)):
				if int(c[j]!=0):
					c_index = total_commmunities + count + 1
					count +=1
					for k in range(len(z[:,j])):
						if z[k,j]!=0:
							C[300*i+k] = int(c_index)
			total_commmunities += int(sum(c))
			self.DF = pd.DataFrame({'X':self.X,'Y':self.Y,"C":C})


	def run(self):
		self.parallel()
		self.create_DF()
		self.DF.to_csv(self.filepath +'/'+ self.filename,index=False)












