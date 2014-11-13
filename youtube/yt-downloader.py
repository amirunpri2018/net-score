#/usr/bin/python2.7

import datetime
import httplib
import time
import os
import subprocess

def timed_test(video):
	full_path = os.path.abspath("./youtube-dl");
	p = subprocess.Popen([full_path, video, "-q"], stdout=subprocess.PIPE);
	out, err = p.communicate();

	if err is not None:
		print "Error."
	else:
		print out

def main():
	video = "https://www.youtube.com/watch?v=ZwzY1o_hB5Y";
	timed_test(video);

if __name__ == "__main__":
	main()