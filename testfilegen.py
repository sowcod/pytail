#-*- coding: utf-8 -*-

import random
import os.path

strs = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def gen(filename) :
    line_num = random.randint(1,1000)
    with open(filename, 'w') as wf:
        for i in range(line_num):
            num = random.randint(0, len(strs) - 1)
            wf.write('{content}\n'.format(content=strs[num] * (num+1) * 1))

def main():
    basedir = os.path.abspath(os.path.dirname(__file__))
    for i in range(30):
        filename = 'testfile{num}.txt'.format(num=i)
        gen(os.path.join(basedir, filename))

if __name__ == '__main__' :
    main()

