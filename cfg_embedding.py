#Copyright (c) Jayaraj Poroor
#Released under MIT License

import sys
import json
import os
from subprocess import Popen, PIPE
from math import log, sqrt

from collections import defaultdict
from sklearn.feature_extraction import DictVectorizer


def inseq_to_feature_dict(lines):
    d = defaultdict(float)
    #unigrams:
    for ins in lines:
        d[ins] += 1
    #bigram subsequences:
    for i in range(0, len(lines)):
        for j in range(i+1, len(lines)):
            f  = lines[i] + "/" +  lines[j]
            d[f] += 1
    return d

def cfg_walk(cfg, paths, curr_path=None, curr_idx=0):
    if curr_path is None:
        curr_path = []
        curr_idx = 0
    ins_desc = cfg[curr_idx]
    while len(ins_desc['next']) == 1 and curr_path.count(ins_desc['next'][0]) < 2:
        curr_path.append(curr_idx)
        curr_idx = ins_desc['next'][0]
        ins_desc = cfg[curr_idx]
    if len(ins_desc['next']) <= 1:
        paths.append(curr_path)
    else:
        for next in ins_desc['next']:
            if curr_path.count(next) < 2:
                path = curr_path.copy()
                cfg_walk(cfg, paths, path, next)

def dict_featurize(mod, df):
    res = {}
    n_methods = 0
    for method, cfg in mod.items():
        paths = []
        cfg_walk(cfg, paths, curr_path=None, curr_idx=0)
        feature_dicts = []
        for path in paths:
            path = [cfg[idx]['ins'] for idx in path]
            #print("PATH", path)
            d = inseq_to_feature_dict(path)
            #print(json.dumps(d, indent=4))
            feature_dicts.append(d)
        res[method] = feature_dicts
        n_methods += 1
    return res, n_methods

def build_nsubseqs(inpath, outpath):
    n_methods = 0
    with open(outpath, 'w') as outfd:
        for root, dirs, files in os.walk(inpath):
            path = root.split(os.sep)
            print((len(path) - 1) * '...', os.path.basename(root))
            for file in files:
                if file.endswith(".class"):
                    file_path = root + os.sep + file
                    print(len(path) * '...', file)
                    process = Popen(["javap", "-v", file_path], stdout=PIPE)
                    (output, err) = process.communicate()
                    exit_code = process.wait()
                    output = output.decode("latin1")
                    #print(output)
                    lines = output.split("\n")
                    #print(lines)
                    res = parse_jsonp(lines)
                    #print(json.dumps(res, indent=4))
                    res, n_mod_methods = dict_featurize(res, None)
                    for method, method_paths in res.items():
                        for path_features in method_paths:
                            features_line = " ".join(list(path_features.keys()))
                            outfd.write(features_line + "\n")
                    n_methods += n_mod_methods
                    print("processed", n_mod_methods, "methods")
    return n_methods

def compute_idf(df, n_methods):
    idf  = {}
    for k, v in df.items():
        idf[k] = log(n_methods/(v + 1))
    return idf

def flatten(dataset):
    res = []
    for path, feature_dicts in dataset.items():
        for method, feature_dict in feature_dicts.items():
            res.append(feature_dict)
    return res

def dict_norm(d):
    n = 0
    for v in d.values():
        n += v * v
    return sqrt(n)

def dict_cosine(d1, d2):
    n1 = dict_norm(d1)
    n2 = dict_norm(d2)
    res = 0
    for k1, v1 in d1.items():
        v2 = d2.get(k1, None)
        if v2 is not None:
            res += v1 * v2
    n = n1 * n2
    return res / n if n != 0 else 0

def normalize_line(line):
    if line.startswith("invoke"):
        ins = line.split(" ", 1)[0]
        type_ = line.split(":")[-1]
        return ins + type_, None
    elif line.startswith("new"):
        fields = line.split(" ", 1)
        ins = fields[0]
        if "class " in line:
            class_ = line.split("class ")[1]
        else:
            class_ = fields[1]
        class_  = class_.strip()
        return "new(" + class_ + ")", None
    else:
        fields = line.split(" ", 1)
        if len(fields)  == 2:
            ins, rest = fields
            if ins.startswith("if") or ins == "goto":
                return ins, int(rest)
        else:
            ins = fields[0]
        return ins, None

def parse_jsonp(src):
    MODULE = 0
    METHOD_DEFS = 1
    METHOD_BODY = 2
    state = MODULE
    curr_method = ""
    curr_method_cfg = {}
    res = {}
    next = None
    for line in src:
        sline = line.strip()
        if state == MODULE:
            if line != "" and line[0] == '{':
                state = METHOD_DEFS
        elif state == METHOD_DEFS:
            if sline.endswith(";"):
                sline = sline[0:-1]
            curr_method = sline
            curr_method_cfg = {}
            state = METHOD_BODY
        elif state == METHOD_BODY:
            if sline == "" or sline == "}":
                state = METHOD_DEFS if sline == "" else MODULE
                if curr_method != "":
                    res[curr_method] = curr_method_cfg
                curr_method = ""
                curr_method_cfg = {}
            else:
                fields = sline.split(":", 1)
                if len(fields) == 2 and fields[0].isnumeric():
                    idx = int(fields[0])
                    if next is not None and ins != "goto":
                        next.append(idx)
                    ins, next_idx = normalize_line(fields[1].strip())
                    next = []
                    if next_idx is not None:
                        next.append(next_idx)
                    node = {'ins': ins, 'next': next}
                    curr_method_cfg[idx] = node

    return res


if __name__ == "__main__":
    import sys
    build_nsubseqs(inpath=sys.argv[1], outpath=sys.argv[2])
