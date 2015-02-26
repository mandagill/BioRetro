import os
import requests
import json
import numpy


hr_json = open('./raw_data/hr_manual.txt').read()

data = json.loads(hr_json)
dataset = []

# Extract the data points and put them in the dataset list so I can establish the baseline with it
for each in data['point']:
	# Each is a dictionary. Extract a datapoint and add it to the dataset list, casting it as an int
	dataset.append(each['value'][0]['fpVal'])

sd_of_dataset = numpy.std(dataset)
print (sd_of_dataset * 2)

# How many are more than a SD away from mean? FIXME this isn't working, not sure why.
num_high_bpm = []
for each_dp in dataset:
	if each_dp > sd_of_dataset:
		num_high_bpm.append(each_dp)

print "The mean of all data points is ", numpy.mean(dataset)
print "The standard deviation of the dataset is ", sd_of_dataset
print "%r data points are two standard deviations higher than the mean. They are: " % len(num_high_bpm), num_high_bpm
