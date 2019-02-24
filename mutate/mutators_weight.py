# -*- coding: UTF-8 -*-
import random
import os
import sys
import re
# from interval import Interval
import argparse
from random import choice


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Run a mutator')

    parser.add_argument('--file', dest='file', default="Testwhile.sol", type=str)
    parser.add_argument('--func', dest='func', default="updateCaps", type=str)
    # number of mutators
    parser.add_argument('--total', dest='total', default=1, type=int)
    # mutator selection
    parser.add_argument('--select', dest='select', default=5, type=int)
    # feedback difference
    parser.add_argument('--DiffFile', dest='DiffFile', default="DiffFile.json", type=str)
    # file path
    parser.add_argument('--dirPATH', dest='dirPATH', type=str)


    args = parser.parse_args()
    return args


def modify_variable_type(fileName, funcName, choice):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    # traverse file to locate function range
    totalContent = f0.readlines()
    totalLen = len(totalContent)
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    ori = ["uint ", "uint ", "uint8 ", "uint16 ", "uint32 ", "uint64 ", "bytes "]
    string = ["uint16 ", "uint256 ", "uint16 ", "uint256 ", "uint256 ", "uint256 ", "bytes32 "]
    # for function signature line
    corr_ori = ["uint)", "uint)", "uint8)", "uint16)", "uint32)", "uint64)", "bytes)"]
    corr_string = ["uint16)", "uint256)", "uint16)", "uint256)", "uint256)", "uint256)", "bytes32)"]

    # modify variable type
    num = random.randint(1, len(ori))
    print("Replace word selection: {}".format(num))
    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):
            # replace all variable type
            first = re.sub(ori[num - 1], string[num - 1], line)
            # content = re.sub(corr_ori[num-1], corr_string[num-1], first)
            content = first.replace(corr_ori[num - 1], corr_string[num - 1])
            f2.write(content)
            if index == int(endLine[it]):
                it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()


def modify_variable_field(fileName, funcName, choice):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    # traverse file to locate function range
    totalContent = f0.readlines()
    totalLen = len(totalContent)
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    field = ["public", "private", "internal"]
    type_ = ["uint", "var", "bytes", "bytes16", "bytes32",
             "uint8", "uint16", "uint32", "uint64", "uint128", "uint256", "address", "string"]

    # modify variable field
    num = random.randint(1, len(field))
    print("Insert field selection: {}".format(num))
    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):
            # insert variable field
            content = line
            for i in range(0, 13):
                pos = line.rfind(type_[i])
                if pos == -1:
                    continue
                str_list = list(line)
                str_list.insert(pos + 1 + len(type_[i]), field[num - 1] + " ")
                content = "".join(str_list)
            f2.write(content)
            if index == int(endLine[it]):
                it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()


def delete_assert(fileName, funcName, choice):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):
            # delete assert statement
            if line.find("assert") == -1:
                f2.write(line)
            if index == int(endLine[it]):
                it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()



def modify_function_property(fileName, funcName, choice):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    # there maybe multiple function declarations
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    property_ = ["public", "private", "internal", "external"]

    # modify function property
    num = random.randint(1, len(property_))
    print("Insert function property: {}".format(num))
    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index == int(startLine[it]):
            content = line
            start_pos = line.find(")")
            end_pos = line.find("returns")
            # do not have return
            if end_pos == -1:
                end_pos = line.find("{")
            # without other properties
            if start_pos + 2 == end_pos:
                str_list = list(line)
                str_list.insert(start_pos + 2, property_[num - 1] + " ")
                content = "".join(str_list)
            # have other modifiers
            else:
                modifier = line[start_pos + 2:end_pos]
                if modifier.find(property_[num - 1]) == -1:
                    str_list = list(line)
                    str_list.insert(start_pos + 2, property_[num - 1] + " ")
                    content = "".join(str_list)
            f2.write(content)
            it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()



def modify_predicate(fileName, funcName, choiceNum):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choiceNum) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    # there maybe multiple function declarations
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()

    comparePredicate = [">=", "<=", ">", "<", "==", "!="]

    f1 = open(dirPATH + fileName, 'r')
    it = 0
    for (index, line) in enumerate(f1):
        content = line
        if it >= len(startLine) or index < int(startLine[it]) or index > int(endLine[it]):
            f2.write(content)

        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):

            if index == int(endLine[it]):
                it += 1

            if line.find(">=") >= 0:
                while(1):
                    temp=choice(comparePredicate)
                    if(temp!= ">="):
                        break
                content = content.replace(">=",temp)
                # f2.write(content)
                # continue

            if line.find("<=") >= 0:
                while (1):
                    temp = choice(comparePredicate)
                    if (temp != "<="):
                        break
                content = content.replace("<=", temp)
                # f2.write(content)
                # continue

            if line.find(">") >= 0 and line.find(">=") < 0 and line.find("=>") <0 :
                while (1):
                    temp = choice(comparePredicate)
                    if (temp != ">"):
                        break
                content = content.replace(">", temp)
                # f2.write(content)
                # continue

            if line.find("<") >= 0 and line.find("<=") < 0:
                while (1):
                    temp = choice(comparePredicate)
                    if (temp != "<"):
                        break
                content = content.replace("<", temp)
                # f2.write(content)
                # continue
            if line.find("==") >= 0 :
                while (1):
                    temp = choice(comparePredicate)
                    if (temp != "=="):
                        break
                content = content.replace("==", temp)
                # f2.write(content)
                # continue
            if line.find("!=") >= 0 :
                while (1):
                    temp = choice(comparePredicate)
                    if (temp != "!="):
                        break
                content = content.replace("!=", temp)
                # f2.write(content)
                # continue

            if line.find("||") >= 0 :
                content=content.replace("||", "&&")
                # f2.write(content)
                # continue
            if line.find("&&") >= 0 :
                content = content.replace("&&", "||")
                # f2.write(content)
                # continue

            f2.write(content)

    f1.close()
    f2.close()



def modify_Operator(fileName, funcName, choiceNum):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choiceNum) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    # there maybe multiple function declarations
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()

    mathOperator = ["+", "-", "*", "/", "%"]

    f1 = open(dirPATH + fileName, 'r')
    it = 0
    for (index, line) in enumerate(f1):
        content = line
        if it >= len(startLine) or index < int(startLine[it]) or index > int(endLine[it]):
            f2.write(content)

        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):

            if index == int(endLine[it]):
                it += 1

            if line.find("-") >= 0 and line.find("--") < 0 :
                while (1):
                    temp = choice(mathOperator)
                    if (temp != "<="):
                        break
                content = content.replace("<=", temp)
                # f2.write(content)
                # continue

            if line.find("+") >= 0 and line.find("++") < 0 :
                while (1):
                    temp = choice(mathOperator)
                    if (temp != "+"):
                        break
                content = content.replace("+", temp)
                # f2.write(content)
                # continue

            if line.find("*") >= 0 and line.find("**") < 0 and line.find("*/") < 0 and line.find("/*") < 0  :
                while (1):
                    temp = choice(mathOperator)
                    if (temp != "*"):
                        break
                content = content.replace("*", temp)
                # f2.write(content)
                # continue
            if line.find("/") >= 0 and line.find("/*") <0 :
                while (1):
                    temp = choice(mathOperator)
                    if (temp != "/"):
                        break
                content = content.replace("/", temp)
                # f2.write(content)
                # continue
            if line.find("%") >= 0 :
                while (1):
                    temp = choice(mathOperator)
                    if (temp != "%"):
                        break
                content = content.replace("%", temp)
                # f2.write(content)
                # continue

            if line.find("++") >= 0 :
                content=content.replace("++", "--")
                # f2.write(content)
                # continue
            if line.find("--") >= 0 :
                content = content.replace("--", "++")
                # f2.write(content)
                # continue

            f2.write(content)

    f1.close()
    f2.close()



def modify_loop(fileName, funcName, choiceNum):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choiceNum) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    # there maybe multiple function declarations
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()

    f1 = open(dirPATH + fileName, 'r')
    it = 0

    for (index, line) in enumerate(f1):
        content = line
        if it >= len(startLine) or index < int(startLine[it]) or index > int(endLine[it]):
            f2.write(content)

        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):

            if index == int(endLine[it]):
                it += 1

            if line.find("for") >= 0 and line.find("(")>=0 and line.find(")")>=0 and line[-2]!=";":
                temp=content.split(";")
                temp[1]+="+99"
                print (temp[1])
                content=temp[0]+";"+temp[1]+";"+temp[2]
                # print content
                f2.write(content)

            elif line.find("while") >= 0 and line.find("(")>=0 and line.find(")")>=0 and line[-2]!=";":
                temp=content.split(")")
                temp[0]+="+99"
                print (temp[0])
                content=temp[0]+")"+temp[1]
                # print content
                f2.write(content)
            else:
                f2.write(content)

    f1.close()
    f2.close()




def update_weight(fileName, totalMutator):
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

    # roulette probability selection
    sum_ = 0
    num_ = []
    for i in range(totalMutator):
        num_.append(str(i))

    ran = random.random()
    for num, r in zip(num_, weight):
        sum_ += float(r)
        if ran < sum_:
            break
    choice = num_.index(num)
    return choice

def delete_return(fileName, funcName, choice):
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):
            if line.find("return") == -1:
                f2.write(line)
            else :
                if line.find("function") != -1:
                    pos1 = line.find("return")
                    pos2 = line.find("{")
                    content = line[:pos1] + line[pos2:]
                    f2.write(content)

            if index == int(endLine[it]):
                it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()


def add_loop_control(fileName, funcName, choice) :
    f0 = open(dirPATH + fileName, 'r')
    f1 = open(dirPATH + fileName, 'r')
    f2 = open(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, 'w')

    totalContent = f0.readlines()
    totalLen = len(totalContent)
    startLine = []
    endLine = []
    current = 0
    for (index, line) in enumerate(f1):
        if line.find("function") != -1 and line.find(funcName) != -1:
            startLine.append(str(index))
            for i in range(int(startLine[current]) + 1, totalLen):
                if totalContent[i].find("function") != -1:
                    endLine.append(str(i - 1))
                    current += 1
                    break
        if index == totalLen - 1 and startLine != 0:
            endLine.append(str(index))
    f1.close()
    f1 = open(dirPATH + fileName, 'r')

    it = 0
    for (index, line) in enumerate(f1):
        if it < len(startLine) and index >= int(startLine[it]) and index <= int(endLine[it]):
            if line.find("for") != -1:
                f2.write(line)
                ran = random.randint(1, 4) # 0.25 prob
                if ran == 1 :
                    f2.write("continue;\n")
                elif ran == 3 :
                	   f2.write("break;\n")
            else :
                f2.write(line)

            if index == int(endLine[it]):
                it += 1
        else:
            f2.write(line)

    f1.close()
    f2.close()

def main():
    args = parse_args()

    fileName = args.file
    funcName = args.func

    # fileName="PreProcess" + "_" + fileName
    choice = args.select

    if choice == 1:
        modify_variable_type(fileName, funcName, choice)
    elif choice == 2:
        modify_function_property(fileName, funcName, choice)
    elif choice == 3:
        modify_Operator(fileName, funcName, choice)
    elif choice == 4:
        modify_predicate(fileName, funcName, choice)
    elif choice == 5:
        modify_loop(fileName, funcName, choice)
    elif choice == 6:
        delete_assert(fileName, funcName, choice)
    elif choice == 7:
        delete_return(fileName, funcName, choice)
    elif choice == 8:
        add_loop_control(fileName, funcName, choice)
    else:
        pass

    os.remove(dirPATH + fileName)
    os.rename(dirPATH + "after_M" + str(choice) + "_" + funcName + "_" + fileName, dirPATH + fileName)



if __name__ == '__main__':
    main()


