#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def run(args, msg, target, cmd):
    """ 
    run one command to create a target file if this target file doen not already exists
    with test option : only print message about command to be run
    with shell option : only create a shell script with commands to be run
    """
    if os.path.isfile(target):
        if args.verbose: print("OK %s" % (target))
        #if args.shell:
        #    args.f_shell.write("# OK {} => {} [{}]\n".format(msg, target, cmd))
    else:
        if args.test:
            if args.verbose : print("should run : msg=%s target=%s, cmd=[%s]" % (msg, target, cmd))
        else:
            if args.verbose : print("will run : msg=%s, target=%s, cmd=[%s]" % (msg, target, cmd))
            if args.shell:
                args.f_shell.write("# {} => {}\n".format(msg, target))
                args.f_shell.write("{}\n".format(cmd))
            else:
                ret = os.system(cmd)
                #ret = 0
                if ret!=0:
                    print("erreur sur l'execution de", cmd)
                else:
                    if args.verbose : print("==> OK", cmd)

def list2file(alist, afile):
    """ write a list to a file, one item per line """
    with open(afile, "w") as f:
        for i in alist:
            f.write("{}\n".format(i))

def file2list(afile):
    """ read a list from a file, one item per line, skip lines starting with # """
    alist = list()
    with open(afile) as f:
        for l in f:
            if l.startswith('#'):
                continue
            alist.append(l.strip())
    return alist

def file2dict(afile):
    """ read a map from a file, one (k, v) pair per line, skip lines starting with #  """
    adict = dict()
    with open(afile) as f:
        for l in f:
            if l.startswith('#'):
                continue
            (k, v) = l.strip().split('\t')
            if k in adict:
                print("file {}, key {} already exists".format(afile, k))
            else:
                adict[k] = v
    return adict

def hnum(val):
    """ write numerical value in human readable way, ie K, M, G for Kilo, Mega an Giga """
    if isinstance(val, (int, long, float, complex)):
        units = { 1e+03 : "K", 1e+06 : "M", 1e+09 : "G" }
        if (val < 0):
            tmp = -val
        else:
            tmp = val
        for unit in sorted(units.keys(), reverse=True):
            if tmp >= unit:
                return "%d%s" % (int(val / unit), units[unit])
    return val


if __name__ == '__main__':
    for i in [3e+1, 3e+2, 3e+3, 3e+4, 3e+5, 3e+6, 3e+7, 3e+8, 3e+9, 3e+10, "aaa"]:
        print("%s => %s" % (str(i), hnum(i)))

    print(file2list("f1.txt"))
    print(file2dict("f1.txt"))
