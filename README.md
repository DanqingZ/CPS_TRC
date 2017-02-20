# CPS_TRC
This repository contains the source code described in "Connected Population Synthesis for Urban Simulation"(Zhang D., Cao J., Feygin S., Tang D.and Pozdnoukhov A., Connected Population Synthesis for Urban Simulation. (in review), 2017)

### Prerequisites

* [cvxpy] (http://www.cvxpy.org/en/latest/install/) 
* [cplex python API](http://www.ibm.com/support/knowledgecenter/SSSA5P_12.5.0/ilog.odms.cplex.help/CPLEX/GettingStarted/topics/set_up/Python_setup.html)
* [R bnlearn/hexbin packages](https://math.usask.ca/~longhai/software/installrpkg.html)

## Running the tests
The connected population synthesis pipeline consists of three steps:
### [Step 1] Bayesian Networks learning and simulation
Composition and socio-economic char- acteristics of the synthetic households are generated based on Bayesian network parameters estimated from a typical household survey data

We utilized R bnlearn package for bayesian networks parts.Please check [bnlearn notebook](https://github.com/DanqingZ/CPS_TRC/blob/master/notebook/call_bnlearn.ipynb)


## License

This project is licensed under the MIT License 
