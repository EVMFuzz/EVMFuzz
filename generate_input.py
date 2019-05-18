import numpy as np
import random

def make(dataList):
    ret = ""
    for _, val in enumerate(dataList) : 
        if (val.find("uint") != -1) or (val.find("int") != -1) :
            ls1 = list(np.random.randint(0, 100, size=1))
            ls2 = [hex(i)[2:] for i in ls1]
            uint_str = ''.join(ls2)
            full_str = uint_str.zfill(64)
            ret += full_str
        elif val.find("bool") != -1:
            ls1 = list(np.random.randint(0, 2, size=1))
            ls2 = [hex(i)[2:] for i in ls1]
            bool_str = ''.join(ls2)
            full_str = bool_str.zfill(64)
            ret += full_str
        elif val.find("address") != -1:
            ls1 = list(np.random.randint(0, 16, size=40))
            ls2 = [hex(i)[2:] for i in ls1]
            addr_str = ''.join(ls2)
            full_str = addr_str.zfill(64)
            ret += full_str
        else :
            pass
    return ret

# print("*", make(['address','uint','bool']))