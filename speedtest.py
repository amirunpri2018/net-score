#!/usr/bin/python2.7

# Script written by James Martin, for the net-score project
# Contact: jamesml@cs.unc.edu, jasleen@cs.unc.edu, gavaletz@cs.unc.edu
# In collaboration with Jasleen Kaur and Eric Gavaletz
# 
# TODO: 
# Use Eric's script and grep on HTTPHDR / follow instructions
# Double check that python is caching connections and not opening entire new ones
# 	Python library may not be low level enough
# Start to look at:
# ASN number on X axis
# Number of clients with that ASN on Y 
# TD_ASN file joined with TD file based on TEST Key field
# 	Maybe dump them into a sqldb and use some joins?

import datetime
import urllib2
import httplib
import time
import os
import subprocess

header_list = {'User-Agent': 'python-%s.%s' % ('net-lib', '0.1')}

# speedtest() -> runs a speedtest with the speedtest-cli
# args:
# 	serverID: ID of the server to run speedtest to
# 				(assigned by the speedtest-cli)
def speedtest(serverID):
	# NOTE: may need to specify absolute path to the speedtest-cli script
	full_path = os.path.abspath("speedtest-cli/speedtest_cli.py")
	p = subprocess.Popen(["python", full_path, "--simple", "--server", serverID],stdout=subprocess.PIPE)
	out, err = p.communicate()

	stats = []
	ntuple = ()
	if err is not None:
		print "Test failed, error returned: ", err
		ntuple = (err)
	else:
		stats = out.split('\n')

		# Pop empty string off end of list
		# If this fails, the test did not return 3 values
		# This should be caught above, but if not 
		try:
			stats.pop(3)
		except:
			print "Test failed."
			ntuple = (err)
			return ntuple

		counter = 0
		for word in stats:
			word.split(':')
			counter+=1

		counter = 0
		for word in stats:
			stats[counter] = (word.split(' '))[1]
			counter+=1

		# Latency, Down, Up
		ntuple = (stats[0],stats[1],stats[2])

	return ntuple

# write_to_log() -> Writes to a specific log file
# args:
# 	data: four-tuple: (TIMESTAMP, TEST_ID, LATENCY, THROUGHPUT)
# 	fileName: relative or absolute path to the log file to write to
def write_to_log(data, fileName):
	# Want to print:
	# TIMESTAMP, TEST_ID, LATENCY, THROUGHPUT
	# Write to log file
	# May need to specify absolute path to log file as well!

	logString = ""
	for i in xrange(len(data)):
		if not i == (len(data) - 1):
			logString = logString + str(data[i]) + ","
		else:
			logString = logString + str(data[i]) + "\n"
	with open(fileName, "w") as log:
		log.write(logString)
		log.flush()

# timer_test() -> Takes a connection and a path to a resource and records times
# taken for the response
# args:
# 	conn: connection object, in the form of a HTTPConnection
# 	PATH: path to a resource on the host
# 	N: number of times to run the test to get averages
def timer_test(conn, PATH, N):
	r_times = list()
	for i in xrange(0, N):
		start_wall = time.time()
		resource = "%s?to=%d&i=%d" % (PATH, start_wall, i)
		conn.request("GET", resource, headers=header_list)
		resp = conn.getresponse()
		data = resp.read()
		end_wall = time.time()
		r_times.append(end_wall - start_wall)
		if resp.status < 200 or resp.status > 206:
			print "NOT OK %d (%s)" % (resp.status, resource)
	return r_times

# server_test() -> abstraction for calculating mean latency and throughput values for
# a connection to a host
# args:
# 	host
# 	path_late: path to object used to measure latency, normally a small image
# 	path_thr: path to object used to measure throughput
# 	to: timeout
# 	test_length: number of times to run the test
def server_test(host, path_late, path_thr, to, test_length):
	late_resource = "%s?to=%d&i=%d" % (path_late, time.time(), 2)
	thr_resource = "%s?to=%d&i=%d" % (path_thr, time.time(), 2)

	conn = httplib.HTTPConnection(host, timeout=to)

	# Latency connection
	conn.request("GET", path_late, headers=header_list)
	imgA = conn.getresponse().read()
	sz_late = len(imgA)

	# Throughput connection
	conn.request("GET", path_thr, headers=header_list)
	imgB = conn.getresponse().read()
	sz_thr = len(imgB)

	# Grab times for each
	late_times = timer_test(conn, path_late, test_length)
	thr_times = timer_test(conn, path_thr, test_length)

	# Calculate averaged RTT and size in bits
	mean_rtt = sum(late_times) / len(late_times)
	thr_bits = sz_thr * 8 / 1000000.0

	thrs = list()

	# Calculate mean throughput
	for i in xrange(0, test_length):
		rtt = late_times[i]*1000
		thr = thr_bits / (thr_times[i] - mean_rtt)
		thrs.append(thr)
	mean_thr = sum(thrs) / len(thrs)

	return ((mean_rtt * 1000), mean_thr)

# main() -> executes specific tests
def main():
	# Path information for timer test to YouTube edge server
	yt_host = "i1.ytimg.com"
	yt_path_late = "/i/augF6Vv2TDgBRvKVeSqyUg/1.jpg"
	yt_path_thr = "/i/pF_Dv5_lbIaAimjzSqUzWA/1.jpg"

	# Path information to the TWC Speedtest server
	twc_host = "24.25.5.24"
	twc_path_late = "/speedtest/latency.txt"
	twc_path_thr = "/speedtest/random500x500.jpg"

	# Path information to the Tranquil Hosting Speedtest server
	# Speedtest ID: 544
	tran_host = "speedtest.ral.tqhosting.com"
	tran_path_late = "/speedtest/latency.txt"
	tran_path_thr = "/speedtest/random500x500.jpg"

	# Path information to the Duke Speedtest server
	# Speedtest ID: 4185
	# http://speedtest.oit.duke.edu/speedtest/upload.php
	duke_host = "speedtest.oit.duke.edu"
	duke_path_late = "/speedtest/upload.php"
	duke_path_thr = "/speedtest/random500x500.jpg"

	TIMEOUT = 10
	TEST_LENGTH = 100

	# "Net-score" feather test
	youtube_timer = ()
	try:
		youtube_timer = server_test(yt_host, yt_path_late, yt_path_thr, TIMEOUT, TEST_LENGTH)
	except:
		youtube_timer = ("NaN", "NaN")

	# TWC tests, first using "net-score" feather test, then using Speedtest CLI
	twc_timer = ()
	twc_speed = ()
	try:
		twc_timer = server_test(twc_host, twc_path_late, twc_path_thr, TIMEOUT, TEST_LENGTH)
	except:
		twc_timer = ("NaN", "NaN")
	try:
		twc_speed = speedtest("999");
	except:
		twc_speed = ("NaN", "NaN", "NaN")

	# Tranquil hosting tests, first using "net-score" feather test, then using Speedtest CLI
	tran_timer = ()
	tran_speed = ()
	try:
		tran_timer = server_test(tran_host, tran_path_late, tran_path_thr, TIMEOUT, TEST_LENGTH)
	except:
		tran_timer = ("Nan", "Nan")
	try:
		tran_speed = speedtest("544")
	except:
		tran_speed = ("NaN", "NaN", "NaN")

	duke_timer = ()
	duke_speed = ()
	try:
		duke_timer = server_test(duke_host, duke_path_late, duke_path_thr)
	except:
		duke_timer = ("NaN", "NaN")
	try:
		duke_speed = speedtest("4185")
	except:
		duke_speed = ("NaN", "NaN", "NaN")

	# Generate data to be written to CSV file
	timestamp = time.time()
	dataString = ( datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Timestamp for entire test
		       	"YT" + str(timestamp), # YouTube server test ID ("net-score" test)
		        youtube_timer[0], # Latency
		        youtube_timer[1], # Throughput
		        "TWC_timer" + str(timestamp), # TWC server test ID ("net-score" test)
		        twc_timer[0], # Latency
		        twc_timer[1], # Throughput
		        "TWC_speed" + str(timestamp), # TWC speedtest-cli test ID
		        twc_speed[0], # Latency
		        twc_speed[1], # Download speed
		        twc_speed[2], # Upload speed
		        "Tran_timer" + str(timestamp), # Tranquil server test ID ("net-score" test)
		        tran_timer[0], # Latency
		        tran_timer[1], # Throughput
		        "Tran_speed" + str(timestamp), # Tranquil speedtest-cli test ID
		        tran_speed[0], # Latency
		        tran_speed[1], # Download speed
		        tran_speed[2] )# Upload speed
	#log_name = "data/" + str(timestamp).split('.')[0] + "_log.txt" # Log file with timestamp
	log_name = "data/results_log.csv"
	log_file = os.path.abspath(log_name)
	write_to_log(dataString, log_file)

# END main()

if __name__ == "__main__":
	main()