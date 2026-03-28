# fitness.py
# 
# This is a fitness function for quickly executing a lot of candidate python code pieces and evaluating time taken.
# The usual way to call this code is as follows.
# 
# ~> python fitness.py candidate NUM_OF_CANDIDATES
#
# If the code you are trying to execute needs to be run in a bigger project, use the following code with dummy names replaced.
# 
# ~> python -m cProfile ./yourFileName.py > outputFileName

import os
import sys

candName = sys.argv[1]
numberOfCandidates = int(sys.argv[2])

for i in range(numberOfCandidates):

	cmdFront = 'python -m cProfile ./'
	cmdBack = '.py > candidateResult_'

	cmd = cmdFront + candName + str(i) + cmdBack + str(i)

	try:
		os.system(cmd)

	except Exception as e:
		print('Candidate '+str(i)+' failed to be called')
		print(e)
