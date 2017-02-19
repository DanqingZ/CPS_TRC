import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from cvxpy import *

class ERGM_CVX:
    def __init__(self, E, C, V, E_all):
    	self.E = E
    	self.C = C
    	self.V = V
    	self.E_all = E_all

	def run_CVX(self):
		community = self.C.values.tolist()
		input = np.zeros((len(self.C)*len(self.C),2))
		c_matrix = np.zeros((len(self.C),len(self.C)))
		Y_matrix = np.zeros((len(self.C),len(self.C)))
		for i in range(len(self.C)):
		    for j in range(len(self.C)):
		        if i!=j:
		            if community[i]==community[j]:
		                c_matrix[i,j] = 1
		input[:,0] = c_matrix.reshape(len(self.C)*len(self.C))
		distance = self.E_all[1].values.tolist()
		input[:,1] = distance
		start = self.E[0].values.tolist()
		end  = self.E[1].values.tolist()
		names = V.values.tolist()
		start_int = np.zeros((len(start)))
		end_int = np.zeros((len(start)))
		for i in range(len(start)):
		    for j in range(len(names)):
		        if names[j][0] == start[i]:
		            start_int[i] = int(j)
		        if names[j][0] == end[i]:
		            end_int[i] = int(j)
		Y_matrix = np.zeros((len(self.C),len(self.C)))
		for i in range(len(start_int)):
		    Y_matrix[start_int[i],end_int[i]] = 1
		Y = Y_matrix.reshape(len(self.C)*len(self.C))
		import cvxpy as cvx
		w = cvx.Variable(2)
		b = cvx.Variable(1)
		Y_matrix = np.ones((len(self.C),len(self.C)))*(-1)
		for i in range(len(start_int)):
		    Y_matrix[start_int[i],end_int[i]] = 1
		Y = Y_matrix.reshape(len(self.C)*len(self.C))
		loss = cvx.sum_entries(cvx.logistic(-cvx.mul_elemwise(Y, input*w+np.ones((len(self.C)*len(self.C),1))*b)))
		problem = cvx.Problem(cvx.Minimize(loss))
		problem.solve(verbose=True)
		self.W = w.value
		self.b = b.value






