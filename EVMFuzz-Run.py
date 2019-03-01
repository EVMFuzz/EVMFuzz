# -*- coding: UTF-8 -*-
import subprocess
import argparse
import random
import time
import os,shutil
import numpy as np
import heapq

contractList = []
diff_pri = {}  # an empty dict
time_pri = {}

PROJECT_DIR = "path/to/EVMFuzz"
dirPATH = PROJECT_DIR + "/example/"
binPATH = dirPATH + "bincode/"
seedPATH = dirPATH + "seed/"

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='EVMFuzz')

    parser.add_argument('--file', dest='file', default="myContract.sol", type=str)
    parser.add_argument('--func', dest='func', default="multiPath", type=str)
    parser.add_argument('--bin', dest='bin', default="MyContract", type=str)
    parser.add_argument('--sig', dest='sig',
                        default="0x87f71cef00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002",
                        type=str)
    args = parser.parse_args()
    return args


# delete pragma solidiy xxxx
# in case of compiler version problem
def preProcess(fileName):
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(seedPATH + "PreProcess" + "_" + fileName, 'w')

    for (index, line) in enumerate(f1):
        if line.find("pragma") >= 0:
            pass
        else:
            f2.write(line)

    f1.close()
    f2.close()


def update_weight(fileName, combination):
    # need mutator_diff_file.json
    diff_file = open(dirPATH + fileName, 'r')
    diff_list = diff_file.readlines()

    weight = {}  # an empty dict
    cnt = 0
    for i in range(len(diff_list)):
        cnt += int(diff_list[i])
    for i in range(len(diff_list)):
        weight[i+1] = float(int(diff_list[i]) / cnt)
    print("Weight : {}".format(weight))

    # ret = list(map(weight.index, heapq.nlargest(len(weight), weight)))
    ret = sorted(weight.items(), key=lambda x: x[1], reverse=True)
    m_queue = []
    for i in range(len(ret)) :
        m_queue.append(ret[i][0])
    print("Mutator_queue : {}".format(m_queue))

    choice = []
    if combination == 1 :
        # choice.append(m_queue[0])
        for i in range(len(m_queue)) :
            if i % 2 != 0 :
                choice.append(m_queue[i])
    elif combination == 2 :
        for i in range(len(m_queue)) :
            if i % 2 == 0 :
                choice.append(m_queue[i])
    elif combination == 3 :
        choice.append(m_queue[0])
        choice.append(m_queue[len(m_queue)-1])
    elif combination == 4 :
        choice.append(m_queue[random.randint(0, len(m_queue)-1)])

    return weight, choice

def editLine(filename, lineno, diff):
    fro = open(dirPATH+filename, "r")

    current_line = 0
    while current_line < lineno:
        fro.readline()
        current_line += 1

    seekpoint = fro.tell()
    frw = open(dirPATH+filename, "r+")
    frw.seek(seekpoint, 0)

    # read the line we want to discard
    test=fro.readline()  
    test=diff
    frw.writelines(test)
    chars = fro.readline()
    while chars:
        frw.writelines(chars)
        chars = fro.readline()

    fro.close()
    frw.truncate()
    frw.close()

def del_folder(path) :
    for i in os.listdir(path) :
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file) :
            os.remove(path_file)
        else :
            del_folder(path_file)


def scheduling(contractList, diff_pri, time_pri):  # DPSA
	print(contractList, diff_pri, time_pri)
	sortList = []
	priority = {}
	for i in range(len(contractList)):
		priority[i] = 0.7 * diff_pri[contractList[i]] + 0.3 * time_pri[contractList[i]]
	# sorted by priority
	data = [(pri, name) for pri, name in zip(priority, contractList)]
	data.sort(reverse=True)
	sortList = [name for pri, name in data]
	# update time priority
	for i in range(1, len(contractList)):
		time_pri[contractList[i]] += 1
	return sortList


def main():
    args = parse_args()

    fileName = args.file
    funcName = args.func
    binName = args.bin
    sigName = args.sig

    if os.path.exists(dirPATH + "diffHis") :
        diffhistory = open(dirPATH + "diffHis", 'w')
        diffhistory.seek(0)
        diffhistory.truncate()
        diffhistory.close()
    del_folder(binPATH)
    del_folder(seedPATH)

    preProcess(fileName)
    fileName = "PreProcess" + "_" + fileName

    # initial seed
    global contractList
    contractList.append(fileName)

    choice = []
    weight = {}
    index = 0

    # mutate 50 times
    while index<=50:
        
        if index == 0:
        	pass
        else:
        	contractList = scheduling(contractList, diff_pri, time_pri)
        fileName = contractList[0]

        if index == 0:
            contract = fileName
        else:
            select = random.randint(1, 4)
            # select = 1
            weight, choice = update_weight("mutator_diff", select) # combined strategy
            shutil.copyfile(seedPATH + fileName, seedPATH + fileName.split(".sol")[0]+"_" + str(index)+".sol" )
            # print("mutate len = "+str(len(choice)))
            for i in range(len(choice)) :
                print("mutate choice: " + str(choice[i]))
                retcode = subprocess.call(
                    "python3 " + PROJECT_DIR + "/ConditionEdit/mutators_weight.py --file " + fileName.split(".sol")[0]+"_" + str(index) +".sol"  + " --func " + funcName + " --select " + str(choice[i]),
                    shell=True)
                if retcode == 1 :
                    continue

                contract = fileName.split(".sol")[0]+"_" + str(index)+".sol"

        # use solc compile
        retcode = subprocess.call("solc --bin-runtime " + seedPATH + contract + " -o " + binPATH + "bincode" + str(index), shell=True)
        
        if(retcode == 1):
            print(retcode, contract)
            # os._exit(0)
            os.remove(seedPATH + contract)
            continue
        print("Generate bytecode.")

        # read bincode
        codefile = open(binPATH + "bincode"+str(index)+"/" + binName + ".bin-runtime", "r")
        bincode = codefile.read()
        codefile.close()
        shutil.copyfile(seedPATH+contract, binPATH + "bincode"+str(index)+"/"+contract)

        # muti-EVM run
        retcode = subprocess.call(
            "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/DifferentialTesting/runcode_index.js --code " + bincode + "--sig " + sigName + " > " + dirPATH + "output/jsout.json",
            shell=True)
        print(str(retcode)+" jsrun")

        retcode = subprocess.call(
            "python3 " + PROJECT_DIR + "/py-evm/test_tx.py --data " + bincode + " --sig " + sigName + " > " + dirPATH + "output/pyout.json",
            shell=True)
        print(str(retcode)+" pyrun")

        retcode = subprocess.call(
            "./aleth-vm trace --code " + bincode + " --mnemonics --input " + sigName + " > " + dirPATH + "output/aletraceout",
            shell=True)
        # print(str(retcode)+" cpprun")

        retcode = subprocess.call(
            "python3 " + PROJECT_DIR + "/cpp_convert_json.py " + dirPATH + "output/aletraceout " + " > " + dirPATH + "output/aleout.json",
            shell=True)

        retcode = subprocess.call(
            "./aleth-vm  --code " + bincode + "--input " + sigName + " --mnemonics" + " >> " + dirPATH + "output/aleout.json",
            shell=True)
        print(str(retcode)+" cpprun")

        time.sleep(5)

        # compare result
        # compute diff
        retcode = subprocess.call(
            "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/DifferentialTesting/evmfuzz_cmp.js --js_file " + dirPATH + "output/jsout.json" + " --py_file " + dirPATH + "output/pyout.json" + " --cpp_file " + dirPATH + "output/aleout.json" +" --ret_dir "+ dirPATH + "newdiff" +" --txdata "+sigName +" --resfile "+dirPATH + "result" ,
            shell=True)
        print("Compare diff.")
        time.sleep(5)

        newdiffFile = open(dirPATH + "newdiff", "r")
        newdiff = int(newdiffFile.read().strip())
        newdiffFile.close()

        diffFile = open(dirPATH + "diff", "r")
        olddiff = int(diffFile.read().strip())
        diffFile.close()

        if newdiff > olddiff:
            # update diff
            diffFile = open(dirPATH + "diff", "w")
            diffFile.write(str(newdiff))
            diffFile.close()

            contractList.append(contract)
            # record priority
            diff_pri[contract] = newdiff
            time_pri[contract] = 0

        // update diff history
        if index == 0:
            diffhistory = open(dirPATH + "diffHis", "a")
            diffhistory.write(contract + "_" + "first" + "_" + str(newdiff).strip() + '\n')
            # write mutator weight
            diffhistory.write(str(weight) + '\n')
            diffhistory.close()
        else:
            diffhistory = open(dirPATH + "diffHis", "a")
            diffhistory.write(contract + "_" + str(choice) + "_" + str(newdiff).strip() + '\n')
            # write mutator weight
            diffhistory.write(str(weight) + '\n')
            diffhistory.close()
        print("Update contract diff.")



        # write mutator_diff file
        if index==0:
            mutatordiffFile = open(dirPATH + "mutator_diff", "w")
            for i in range(1, 9):
                mutatordiffFile.write(str(newdiff).strip()+'\n')
            mutatordiffFile.close()
        else:
            for i in range(len(choice)):
                editLine("mutator_diff",choice[i]-1,str(newdiff).strip()+'\n')

        index += 1

if __name__ == '__main__':
    main()
