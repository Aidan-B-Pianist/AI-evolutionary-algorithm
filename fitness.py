### fitness.py
# 
# This is a fitness function for quickly executing a lot of candidate python code pieces and evaluating time taken.
# The candidate files should be named candidateNUM.py, where NUM is from 0 to NUM_OF_CANDIDATES - 1
# The usual way to call this code is as follows.
# 
# ~> python fitness.py genericCandidateName NUM_OF_CANDIDATES
#
# If the code you are trying to execute needs to be run in a bigger project, use the following code with dummy names replaced 
# for each candidate name.
# 
# ~> python -m cProfile ./candidateName.py > outputFileName
#
# If you want to evaluate only one script, use this
# 
# ~> python fitness.py scriptName
#
# The expected output of this file is a bunch of data files that can be read on their own to find weaknesses, and there will be 
# a visualizer to show the data in an easily readable way. An example of an output file is in the repository called candidate_Result_0

import os
import sys

candName = sys.argv[1]

if len(sys.argv) > 2:
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

else:
	numberOfCandidates = 1
	cmdFront = 'python -m cProfile '
	cmdBack = ' > '+ candName +'-Result'

	cmd = cmdFront + candName + cmdBack

	try:
		os.system(cmd)

	except Exception as e:
		print('Candidate '+str(i)+' failed to be called')
		print(e)





