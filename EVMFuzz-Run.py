# -*- coding: UTF-8 -*-
import subprocess
import argparse
import random
import time
import os,shutil
import ctypes,sys
import heapq
import generate_input
import json

PROJECT_DIR = "/home/fuying/EVMFuzz"    # NEED TO BE MODIFIED
contractPATH = PROJECT_DIR + "/contract/"
testPATH = PROJECT_DIR + "/TestOut/"

curC = 0
totalVarient = 0

X1 = 0         # different output
X2 = 0         # more gasUsed
X3 = 0         # less gasUsed
X4 = 0         # same gasUsed
X5 = 0         # more opSeqLen
X6 = 0         # less opSeqLen
X7 = 0         # same opSeqLen

fmt = '\033[0;3{}m{}\033[0m'.format
class color: 
    BLACK = 0    #黑 
    RED  = 1     #红 
    GREEN = 2    #绿 
    YELLOW = 3   #棕 
    BLUE  = 4    #蓝 
    PURPLE = 5   #紫 
    CYAN  = 6    #青 
    GRAY  = 7    #灰 

def show_help():
    """
    Show receving arguments
    """
    welcome = "WELCOME TO EVMFUzz!"
    print(fmt(color.YELLOW, welcome.center(os.get_terminal_size().columns)))  # width: columns  height: lines
    print("\nVERSION:")
    print("   2.0.1")

    print("\nTEST EVMS:")
    print("   Go Ethereum     v1.8.13           Golang")
    print("   Ethereumjs-vm   v2.4.0            Javascript")
    print("   Py-EVM          v0.2.0-alpha.31   Python")
    print("   Aleth           v1.5.0-alpha.6    C++")
    

    print("\nSTEPS:")
    print("   1 >> Download and setup the environment.")
    print("   2 >> Upload user's EVM and the interface.(Optional)")
    print("   3 >> Fuzzing.")
    print("   4 >> Sending the report.")


def create_folder(dirPATH):
    """
    Create folders needed
    """
    binPATH = dirPATH + "bincode/"
    seedPATH = dirPATH + "seed/"
    outputPATH = dirPATH + "output/"

    if os.path.exists(binPATH) == False :
        os.makedirs(binPATH)
    if os.path.exists(seedPATH) == False :
        os.makedirs(seedPATH)
    if os.path.exists(outputPATH) == False :
        os.makedirs(outputPATH)
    return binPATH, seedPATH, outputPATH


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
def preProcess(seedPATH, fileName):
    """
    Preprocess of smart contracts
    """
    f1 = open(contractPATH + fileName, 'r')
    f2 = open(seedPATH + "PreProcess_" + fileName, 'w')

    for _, line in enumerate(f1):
        if line.find("pragma") >= 0:
            pass
        else:
            f2.write(line)

    f1.close()
    f2.close()


def update_weight(dirPATH, fileName, combination):
    """
    Update mutator weights
    """
    # need mutator_diff_file.json
    diff_file = open(dirPATH + fileName, 'r')
    diff_list = diff_file.readlines()

    weight = {}  # an empty dict
    cnt = 0
    for i in range(len(diff_list)):
        cnt += int(diff_list[i])
    for i in range(len(diff_list)):
        weight[i+1] = float(int(diff_list[i]) / cnt)
    # print("Weight : {}".format(weight))

    # ret = list(map(weight.index, heapq.nlargest(len(weight), weight)))
    ret = sorted(weight.items(), key=lambda x: x[1], reverse=True)
    m_queue = []
    for i in range(len(ret)) :
        m_queue.append(ret[i][0])
    # print("Mutator_queue : {}".format(m_queue))

    choice = []
    if combination == 1 :
        # choice.append(m_queue[0])
        for i in range(len(m_queue)) :
            if i % 2 == 0 :
                choice.append(m_queue[i])
    elif combination == 2 :
        for i in range(len(m_queue)) :
            if i % 2 != 0 :
                choice.append(m_queue[i])
    elif combination == 3 :
        choice.append(m_queue[0])
        choice.append(m_queue[len(m_queue)-1])
    elif combination == 4 :
        choice.append(m_queue[random.randint(0, len(m_queue)-1)])

    return weight, choice

def editLine(dirPATH, filename, lineno, diff):
    fro = open(dirPATH+filename, "r")

    current_line = 0
    while current_line < lineno:
        fro.readline()
        current_line += 1

    seekpoint = fro.tell()
    frw = open(dirPATH+filename, "r+")
    frw.seek(seekpoint, 0)

    # read the line we want to discard
    test = fro.readline()  # 读入一行进内存 同时！ 文件指针下移实现删除
    test = diff
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


def del_folder(path) :
    """
    Empty the folder
    """
    for i in os.listdir(path) :
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file) :
            os.remove(path_file)
        else :
            del_folder(path_file)


def scheduling(contractList, diff_pri, time_pri):
    """
    Dynamic Priority Scheduling Algorithm
    """
    # print(contractList, diff_pri, time_pri)
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
    # args = parse_args()
    
    if os.path.exists(testPATH) :
        shutil.rmtree(testPATH)
    os.makedirs(testPATH)
    
    global curC
    global totalVarient

    global X1
    global X2
    global X3
    global X4
    global X5
    global X6
    global X7

    need_prefix = True
        
    maxIter = 100
    print(fmt(color.RED, "\n"))
    print(fmt(color.RED, "Please set fuzz times: (The default setting is 100)"))
    times = input()
    if times != "":
        maxIter = int(times)

    for _, _, filenames in os.walk(contractPATH, followlinks=True):
        # Step 1.遍历合约
        for fileName in filenames:
            curC += 1
            dirPATH = testPATH + "contract" + str(curC) + "/" 
            binPATH, seedPATH, outputPATH = create_folder(dirPATH)
            
            contractList = []
            diff_pri = {}  # an empty dict
            time_pri = {}

            # 清空 diffHis文件 bincode/ seed/
            # if os.path.exists(dirPATH + "diffHis") :
            #     diffhistory = open(dirPATH + "diffHis", 'w')
            #     diffhistory.seek(0)
            #     diffhistory.truncate()
            #     diffhistory.close()
            # del_folder(binPATH)
            # del_folder(seedPATH)

            preProcess(seedPATH, fileName)
            fileName = "PreProcess_" + fileName

            # 生成函数签名
            # p = subprocess.Popen("solc " + seedPATH + fileName + " --hashes -o " + dirPATH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # sout = p.stdout.readlines()
            
            retcode = subprocess.call("solc " + seedPATH + fileName + " --hashes -o " + dirPATH, shell=True)
            if(retcode == 1):
                os.remove(seedPATH + fileName)
                continue
            print("\n")
            print(fmt(color.YELLOW, "Generate function signature, Done!"))
            # print("Done!")
            # p1 = input()

            # 初始种子
            contractList.append(fileName)

            for f in os.listdir(dirPATH):
                if os.path.splitext(f)[1] == '.signatures':
                    sigfile = open(dirPATH + f, "r")
                    line = sigfile.read().splitlines()

                    # Step 2.遍历函数
                    for signature in line:
                        pos1 = signature.find('(')
                        pos2 = signature.find(')')
                        funcName = signature[10:pos1]

                        sig = "0x" + signature[:8]
                        dataList = signature[pos1+1:pos2].split(',')
                        # check parameter type
                        canDeal = True
                        for i, val in enumerate(dataList) :  
                            if (val.find('bool') == -1) and (val.find('uint') == -1) and (val.find('int') == -1) and (val.find('address') == -1):
                                canDeal = False
                                break
                            if (val.find('[') != -1) and (val.find(']') != -1) : # 数组
                                canDeal = False
                                break
                        if canDeal == False :
                            continue

                        inputData = generate_input.make(dataList) 
                        sigName = sig + inputData
                        print(fmt(color.RED, "Select contract: "),fileName)
                        print(fmt(color.RED, "Select function: "), funcName)
                        # print(fmt(color.YELLOW, "Select contract: {}, function: {}".format(fileName, funcName))
                        print(fmt(color.RED, "Input data: "),sigName)
                        
                        # print("Select contract: {}, function: {}".format(fileName, funcName))
                        # print("Input data: {}".format(sigName))
                        # p2 = input()

                        choice = []
                        weight = {}
                        index = 0

                        # 循环
                        while index < maxIter:
                            # a = index % (len(contractList))
                            # fileName = contractList[a]
                            print(fmt(color.YELLOW, "Start iteration {}: ".format(index)))

                            if index == 0:
                                pass
                            else:
                                contractList = scheduling(contractList, diff_pri, time_pri)
                            fileName = contractList[0]

                            if index == 0:
                                contract = fileName
                            else:
                                select = random.randint(1, 4)
                                select_name = ['EvenComb', 'OddComb', 'ExtremeComb', 'RandomComb']
                                print(fmt(color.RED, "Selected combined strategy in #iter {}: ".format(index)),select_name[select-1])
                                # print("Selected combined strategy in #iter{}: {}".format(index, select_name[select-1]))
                                weight, choice = update_weight(dirPATH, "mutator_diff", select) # combined strategy
                                shutil.copyfile(seedPATH + fileName, seedPATH + fileName.split(".sol")[0] + "_" + str(index) + ".sol" )

                                print(fmt(color.RED, "Combined mutators: "),choice)
                                # print("Combined mutators: {}".format(choice))
                                p3 = input()
                                for i in range(len(choice)) :
                                    retcode = subprocess.call(
                                        "python3 " + PROJECT_DIR + "/mutators_weight.py --file " + fileName.split(".sol")[0] + "_" + str(index) + ".sol" 
                                        + " --dir " + seedPATH + " --func " + funcName + " --select " + str(choice[i]),
                                        shell=True)
                                    if retcode == 1 :
                                        continue

                                    contract = fileName.split(".sol")[0] + "_" + str(index) + ".sol"


                            # 删除bin文件夹 solc编译
                            # subprocess.call("rm -rf " + dirPATH + "bincode", shell=True)
                            
                            # print("Generating bytecode.")
                            # retcode = subprocess.call("solc --bin-runtime " + seedPATH + contract + " -o " + binPATH + "bincode_" + funcName + "_" + str(index), shell=True)
                            p = subprocess.Popen("solc --bin-runtime " + seedPATH + contract + " -o " + binPATH + "bincode_" + funcName + "_" + str(index), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            sout = p.stderr.readlines()
                            if "Error" in sout:
                                print(contract)
                                # os._exit(0)
                                os.remove(seedPATH + contract)
                                if contract in contractList :
                                    contractList.remove(contract)
                                continue
            
                            # if(retcode == 1):
                            #     print(retcode, contract)
                            #     # os._exit(0)
                            #     os.remove(seedPATH + contract)
                            #     if contract in contractList :
                            #         contractList.remove(contract)
                            #     continue

                            # print("Done!")
                            print(fmt(color.YELLOW, "Generating bytecode Done!"))
                            print("\n")

                            # 读取bincode
                            path_list = binPATH + "bincode_" + funcName + "_" + str(index) + "/"
                            for f in os.listdir(path_list):
                                if os.path.splitext(f)[1] == '.bin-runtime':  # 判断文件后缀
                                    codefile = open(path_list + f, "r")
                            bincode = codefile.read()
                            codefile.close()
                            shutil.copyfile(seedPATH + contract, path_list + contract)


                            # 4个平台运行
                            retcode = subprocess.call(
                                "/usr/local/bin/node " + PROJECT_DIR + "/benchmarkEVMs/jsEVM/js_runcode.js --code " + bincode + "--sig " + sigName + " > " + outputPATH + "jsout.json",
                                shell=True)
                            if retcode == 0 :
                                # print("jsevm Success!")
                                print(fmt(color.YELLOW, "jsevm Success!"))
                            else :
                                # print("jsevm Fail!")
                                print(fmt(color.RED, "jsevm Fail!"))

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/benchmarkEVMs/py-evm/test_tx.py --data " + bincode + " --sig " + sigName + " > " + outputPATH + "pyout.json",
                                shell=True)
                            if retcode == 0 :
                                print(fmt(color.YELLOW, "pyevm Success!"))
                                # print("pyevm Success!")
                            else :
                                print(fmt(color.RED, "pyevm Fail!"))
                                # print("pyevm Fail!")

                            retcode = subprocess.call(
                                "./benchmarkEVMs/evm --debug --json --code " + bincode + " --input " + sigName[2:] + " run > " + outputPATH + "gethout.json",
                                shell=True)
                            if retcode == 0 :
                                # print("geth Success!")
                                print(fmt(color.YELLOW, "geth Success!"))
                            else :
                                # print("geth Fail!")
                                print(fmt(color.RED, "geth Fail!"))

                            # aleth trace
                            retcode = subprocess.call(
                                "./benchmarkEVMs/aleth-vm trace --code " + bincode + " --mnemonics --input " + sigName + " > " + outputPATH + "aletraceout",
                                shell=True)

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/benchmarkEVMs/cpp_convert_json_1.py " + outputPATH + "aletraceout " + " > " + outputPATH + "alethout.json",
                                shell=True)

                            # aleth output
                            retcode = subprocess.call(
                                "./benchmarkEVMs/aleth-vm stats --code " + bincode + " --mnemonics --input " + sigName + " > " + outputPATH + "aleresultout",
                                shell=True)

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/benchmarkEVMs/cpp_convert_json_2.py " + outputPATH + "aleresultout " + " >> " + outputPATH + "alethout.json",
                                shell=True)
                            if retcode == 0 :
                                # print("aleth Success!")
                                print(fmt(color.YELLOW, "aleth Success!"))
                            else :
                                # print("aleth Fail!")
                                print(fmt(color.RED, "aleth Fail!"))

                            time.sleep(5)

                            # 比较结果 diff
                            retcode = subprocess.call(
                                "/usr/local/bin/node " + PROJECT_DIR + "/benchmarkEVMs/jsEVM/evmfuzz_cmp.js --js_file " 
                                + outputPATH + "jsout.json" + " --py_file " 
                                + outputPATH + "pyout.json" + " --cpp_file " 
                                + outputPATH + "gethout.json" + " --geth_file " 
                                + outputPATH + "alethout.json" + " --ret_dir "
                                + dirPATH + "newdiff" + " --txdata " + sigName + " --resfile " + dirPATH + "result" ,
                                shell=True)
                            # print("Compare diff.")
                            time.sleep(5)

                            try :
                                open(dirPATH + "newdiff", "r")
                            except :
                                os.mknod(dirPATH + "newdiff")
                            newdiffFile = open(dirPATH + "newdiff", "r")
                            if os.path.getsize(dirPATH + "newdiff") == 0:
                                newdiff = 0
                            else :
                                newdiff = int(newdiffFile.read().strip())
                            newdiffFile.close()

                            try :
                                open(dirPATH + "diff", "r")
                            except :
                                os.mknod(dirPATH + "diff")
                            diffFile = open(dirPATH + "diff", "r")
                            if os.path.getsize(dirPATH + "diff") == 0:
                                olddiff = 0
                            else :
                                olddiff = int(diffFile.read().strip())
                            diffFile.close()

                            if newdiff > olddiff:
                                # 更新diff文件
                                diffFile = open(dirPATH + "diff", "w")
                                diffFile.write(str(newdiff))
                                diffFile.close()

                                contractList.append(contract)
                                # record priority
                                diff_pri[contract] = newdiff
                                time_pri[contract] = 0

                            if index == 0 :
                                diff_pri[contract] = newdiff
                                time_pri[contract] = 0


                            # 写 diff history 文件
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
                            # print("Update contract diff.")


                            # 写 mutator_diff 文件
                            if index == 0:
                                mutatordiffFile = open(dirPATH + "mutator_diff", "w")
                                for i in range(1, 9):
                                    mutatordiffFile.write(str(newdiff).strip()+'\n')
                                mutatordiffFile.close()
                            else:
                                for i in range(len(choice)):
                                    editLine(dirPATH, "mutator_diff", choice[i]-1, str(newdiff).strip()+'\n')
                                # mutatordiffFile = open(dirPATH + "mutator_diff", "w")
                                # for i in range(1, 6):
                                #     if choice==i:
                                #         mutatordiffFile.write(str(newdiff).strip() + '\n')
                                # mutatordiffFile.close()
                            # print("Update mutator diff.")

                            # record Testing result
                            # print(fmt(color.YELLOW, "Collecting information."))
                            # print("Collecting information.")
   
                            index += 1
                            totalVarient += 1
    




if __name__ == '__main__':
    show_help()
    main()
    print(fmt(color.YELLOW, "\nFuzz Done! You can find the results in 'TestOut' folder."))

