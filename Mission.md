Okay, let's take a step back:

- Multithreaded connections are a good metric of total capacity. If you want to see if you're getting what you're paying for
- Single threaded connections are closer to most users browsing or using an application that is making single http requests

- How do we say that our figures are better metrics for a single threaded video streaming application?

- Could modify CLI to download image file from YT server using multithreaded connection

- Modify duke script to retreive latency.txt

How do we quantify a single thread is closer to the video stream throughput?
	- Normally videos request frames on a single threaded connection
	- Industry is becoming much more high tech, proprietary, two (or more) ways to report bandwidth
	- We can tell you that most video streaming services today, at time of publication, use a single threaded connection
	- We are not throwing out multithreaded model

	- Measure how long it takes

	Action items:
	1. Watch youtube video a few times, measure how many bytes are transmitted and how long with a tcp dump
	2. Use the web Speedtest client to see if the CLI is reporting similar times
	3. Concat all CSV files with ASN location and plot all the ASNs we're capturing

	Notion of capacity vs. what users see