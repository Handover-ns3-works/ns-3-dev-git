
import subprocess

# ttt=[0, 0.04, 0.08, 0.1, 0.128, 0.16, 0.256, 0.32, 0.48, 0.572, 0.64, 0.024, 1.28, 2.56, 5.120]
ttt=[2500, 3100, 3200, 3300, 3400, 4000, 4500, 5000]
hys = [3 for i in range(0, len(ttt))]
# dist = [x for x in range(400, 910, 10)]

args = {
	"--timeToTrigger": [str(x) for x in ttt],
	# "--hysteresis": [str(x) for x in hys],
	# "--distance": [str(x) for x in dist]
}
argsStr = [x + "=" + y for x in args.keys() for y in args[x]]

# number of iterations to run for each configuration
iterationsPerConfig = 1

# selected configurations of hysteresis and timeToTrigger
# selectedConfigs = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
selectedConfigs = [argsStr.index(x) for x in argsStr]

# init a csv file
# filename = "rlf_results.csv"
# f = open(filename, "w")
# f.write("TTT, Hys, RLF count, RLF average time\n")

for i in selectedConfigs:
	# rlfSumByConfig = 0
	# rlfAveragesPerIteration = []
	print("Running config " + str(argsStr[i]))
	
	for j in range(1, iterationsPerConfig+1):
		print("Running iteration " + str(j))
		
		# run the simulation with args
		# Catch and exit if there is an error
		try: 
			output = subprocess.check_output([
				"./ns3", "run", 
				'"scratch/handover-ns3-works/scenario/scenario.cc ' + argsStr[i] + '"'
			])
			output = output.decode("utf-8")
			print(output)
		except subprocess.CalledProcessError as e:
			print("Error running simulation")
			# exit(1)
			##############################################################################################
			break;
		
		# RNTIs where the Handover command was recieved when T310 timer was running
		# Supposed to be reported as a HOF, but NS-3 is configured with an Ideal RRC, so it doesn't happen
		# This needs to be subtracted from number of HOs, to give actual number of Handovers
		rlf_rnti = set([x.split()[-1] for x in output.split('\n') if 'T310' in x])
		handover_rnti = set([x.split()[-1] for x in output.split('\n') if 'Handover' in x])
		HOF_by_Command = rlf_rnti.intersection(handover_rnti)
		
		rlf_count = [x.split()[-1] for x in output.split('\n') if 'RLF count: ' in x][0]
		ho_count = [x.split()[-1] for x in output.split('\n') if 'HO count: ' in x][0]
		hof_count = int(rlf_count) + len(HOF_by_Command)
		
		# print(rlf_rnti, handover_rnti, HOF_by_Command, rlf_count, ho_count)
		print("HOF by Command not Recieved: " + str(len(HOF_by_Command)))
		print("HOF by RLF during TTT: " + str(rlf_count))
		print("Total Handover Failures: " + str(hof_count))
		
		# rlfSumByConfig += int(rlf_count)

		# rlf_times = [x.split()[-1] for x in output.split('\n') if 'RLF time: ' in x]
		# if len(rlf_times) == 0:
		# 	rlf_avg = 0
		# else:
		# 	rlf_avg = sum([float(x) for x in rlf_times]) / len(rlf_times)
		# rlfAveragesPerIteration.append(rlf_avg)
		
	# print("RLF count: " + str(rlfSumByConfig))
	# rlfAverageTimeByConfig = sum(rlfAveragesPerIteration) / len(rlfAveragesPerIteration)
	# print("RLF average time: " + str(rlfAverageTimeByConfig))
	print("---------------------")
	
	# f.write(str(ttt[i]) + ", " + str(hys[i]) + ", " + str(rlfSumByConfig) + ", " + str(rlfAverageTimeByConfig) + "\n")

# f.close()	