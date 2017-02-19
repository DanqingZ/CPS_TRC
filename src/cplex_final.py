# created by KKKL for connected population synthesis paper
from __future__ import print_function
import numpy as np
from math import floor, fabs
import sys
import cplex
from cplex.exceptions import CplexError
from inputdata import read_dat_file
import matplotlib.pyplot as plt
import pandas as pd


# python cplex_final.py x.csv y.csv result.csv


X = np.loadtxt(str(sys.argv[1]))
Y = np.loadtxt(str(sys.argv[2]))
result = []


def run_cplex(loc_X,loc_Y,m=30,M=50):
    N = loc_X.shape[0]
    C = []
    for i in range(N):
        c = []
        for j in range(N):
            c.append(np.sqrt((loc_X[i]-loc_X[j])**2+(loc_Y[i]-loc_Y[j])**2))
        C.append(c)
    print('Number of clients')
    print(len(loc_Y))
    print('Number of facilities')
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
    print(sum(C))
    Z = solution.get_values()[300:90300]
    print(sum(Z))
    Z = np.array(Z)
    Z = np.reshape(Z, (300,300)) 
    return C,Z


for i in xrange(len(X)/300):
    if i< len(X)/300-1:
        print('............')
        print(i*300)
        print((i+1)*300)
        loc_X = X[i*300:(i+1)*300]
        loc_Y = Y[i*300:(i+1)*300]
        C,Z = run_cplex(loc_X,loc_Y)
        result.append([loc_X,loc_Y,C,Z])
    else:
        print('............')
        loc_X = X[i*300:len(X)]
        loc_Y = Y[i*300:len(X)]
        C,Z = run_cplex(loc_X,loc_Y)
        result.append([loc_X,loc_Y,C,Z])


def create_DF(result,X,Y):
    C = np.zeros(len(X))
    total_commmunities = 0
    for i in xrange(len(X)/300):
        c = result[i][2]
        z = result[i][3]
        count = 0
        for j in range(len(c)):
            if int(c[j]!=0):
                c_index = total_commmunities + count + 1
                count +=1
                for k in range(len(z[:,j])):
                    if z[k,j]!=0:
                        C[300*i+k] = int(c_index)
        total_commmunities += int(sum(c))
        DF = pd.DataFrame({'X':X,'Y':Y,"C":C})
        return DF




DF = create_DF(result,X,Y)
DF.to_csv(str(sys.argv[3]),index=False)





