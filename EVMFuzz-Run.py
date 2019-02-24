# -*- coding: UTF-8 -*-
import subprocess
import argparse
import random
import time
import os,shutil
import numpy as np
import heapq

contractList = []

PROJECT_DIR = "path~to~EVMFuzz"
dirPATH = PROJECT_DIR+"/example/"

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
    f2 = open(dirPATH + "PreProcess" + "_" + fileName, 'w')

    for (index, line) in enumerate(f1):
        if line.find("pragma") >= 0:
            pass
        else:
            f2.write(line)

    f1.close()
    f2.close()

def find_sub_max(arr, n):
    if n == 1 :
        return np.argmax(arr) + 1
    elif n == len(arr) :
        return np.argmin(arr) + 1
    else :
        arr_ = arr
        for i in range(n-1):
            arr_ = arr
            arr_[np.argmax(arr_)] = np.min(arr)
            arr = arr_
        return np.argmax(arr_) + 1


def update_weight(fileName, combination):
    # need mutator_diff_file.json
    diff_file = open(dirPATH + fileName, 'r')
    diff_list = diff_file.readlines()

    weight = []
    cnt = 0
    for i in range(len(diff_list)):
        cnt += int(diff_list[i])
    for i in range(len(diff_list)):
        weight.append(str(float(int(diff_list[i]) / cnt)))
    # print(weight)

    import numpy as np
    import heapq

    ret = list(map(weight.index, heapq.nlargest(len(weight), weight)))
    m_queue = [i+1 for i in ret]

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

    return choice

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

    # now move the rest of the lines in the file
    # one line back
    chars = fro.readline()
    while chars:
        frw.writelines(chars)
        chars = fro.readline()

    fro.close()
    frw.truncate()
    frw.close()


def main():
    args = parse_args()

    fileName = args.file
    funcName = args.func
    binName = args.bin
    sigName = args.sig

    preProcess(fileName)
    fileName = "PreProcess" + "_" + fileName

    # initial seed
    contractList.append(fileName)

    index = 0

    # mutate 50 times
    while index<=50:
        a = index % (len(contractList))
        fileName = contractList[a]

        if index==0:
            contract=fileName
        else:
            # mutate
            choice = update_weight("mutator_diff", 2) # mutator list
            shutil.copyfile(dirPATH + fileName, dirPATH + fileName.split(".sol")[0]+"_" + str(index)+".sol" )
            print("mutate len"+str(len(choice)))
            for i in range(len(choice)) :
                print("mutate choice" + str(choice[i]))
                retcode = subprocess.call(
                    "python2.7 "+PROJECT_DIR + "/mutate/mutators_weight.py --file " +fileName.split(".sol")[0]+"_" + str(index)+".sol"  + " --func " + funcName + " --select " + str(choice[i])+ " --dirPATH "+dirPATH,
                    shell=True)
                if retcode==1 :
                    continue

                print(retcode)
                print("mutate")

                contract = fileName.split(".sol")[0]+"_" + str(index)+".sol"


        # use solc compile
        retcode = subprocess.call("solc --bin-runtime " + dirPATH + contract + " -o " + dirPATH + "bincode"+str(index), shell=True)
        print(retcode)
        if(retcode==1):
            continue
        # read bincode
        codefile = open(dirPATH + "bincode"+str(index)+"/" + binName + ".bin-runtime", "r")
        bincode = codefile.read()
        codefile.close()
        shutil.copyfile(dirPATH+contract, dirPATH + "bincode"+str(index)+"/"+contract)

        # muti-EVM run
        
        retcode = subprocess.call(
            "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/js_runcode.js --code " + bincode + " --sig " + sigName + " > " + dirPATH + "output/jsout.json",
            shell=True)
        print(str(retcode)+"jsrun")

        retcode = subprocess.call(
            "python3 " + PROJECT_DIR + "/Py-EVM/py_runcode.py --data " + bincode + " --sig " + sigName + " > " + dirPATH + "output/pyout.json",
            shell=True)
        print(str(retcode)+"pyrun")

        retcode = subprocess.call(
            "./aleth-vm trace --code " + bincode + " --mnemonics --input " + sigName + " > " + dirPATH + "output/aletraceout",
            shell=True)
        print(str(retcode)+"cpprun")

        retcode = subprocess.call(
            "python3 " + PROJECT_DIR + "/aleth/convert_json.py " + dirPATH + "output/aletraceout " + " > " + dirPATH + "output/aleout.json",
            shell=True)
        print(retcode)

        retcode = subprocess.call(
            "./aleth-vm  --code " + bincode + "--input " + sigName + " --mnemonics" + " >> " + dirPATH + "output/aleout.json",
            shell=True)
        print(str(retcode)+"cpprun2")

        time.sleep(5)

        # compare result
        # compute diff
        retcode = subprocess.call(
            "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/evmfuzz_cmp.js --js_file " + dirPATH + "output/jsout.json" + " --py_file " + dirPATH + "output/pyout.json" + " --cpp_file " + dirPATH + "output/aleout.json" +" --ret_dir "+ dirPATH + "newdiff" +" --txdata "+sigName +" --resfile "+dirPATH + "result" ,
            shell=True)
        print(retcode)
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

        if index==0:
            diffhistory = open(dirPATH + "diffHis", "a")
            diffhistory.write(contract + "_" + "first" + "_" + str(newdiff).strip() + '\n')
            diffhistory.close()
        else:
            diffhistory = open(dirPATH + "diffHis", "a")
            diffhistory.write(contract + "_" + str(choice) + "_" + str(newdiff).strip() + '\n')
            diffhistory.close()



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
