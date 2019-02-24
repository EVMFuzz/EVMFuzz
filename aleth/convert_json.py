import sys
import json

# file_name = "cpp_output.json"
file_name = sys.argv[1]

with open(file_name, 'r') as f :
	openfile = json.loads(f.read())
	for i in range(len(openfile)) :
		# print opcode object
		print("{{\"pc\": {}, \"gas\": \"0x{}\", \"gasCost\": "
			"\"0x{}\", \"stack\": {}, \"depth\": {}, \"opName\": \"{}\"}}"
			.format(openfile[i]['pc'],
				'%x' % int(openfile[i]['gas']),
				'%x' % int(openfile[i]['gasCost']),
				openfile[i]['stack'],
				openfile[i]['depth'],
				openfile[i]['op']))
