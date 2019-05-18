import sys
import json

file_name = sys.argv[1]

out = ""
gas = ""

with open(file_name, 'r') as f :
	for line in f.readlines()[:2]:
		if line.find("Output") >= 0 :
			pos1 = line.find(":")
			pos2 = line.find("\n")
			out = line[pos1+2:pos2]
		if line.find("Gas used") >= 0 :
			pos1 = line.find(":")
			pos2 = line.find("(")
			gas = line[pos1+2:pos2]
	print("{{\"output\": \"{}\", \"gasUsed\": \"0x{}\"}}"
		.format(out, '%x' % int(gas)))
