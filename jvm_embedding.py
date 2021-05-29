#Copyright (c) Jayaraj Poroor
#Released under MIT License

import sys
import json
import os
from subprocess import Popen, PIPE

from collections import defaultdict
from sklearn.feature_extraction import DictVectorizer

def normalize_line(line):
    if line.startswith("invoke"):
        ins = line.split(" ", 1)[0]
        type_ = line.split(":")[1]
        return ins + type_
    elif line.startswith("new"):
        fields = line.split(" ", 1)
        ins = fields[0]
        if "class " in line:
            class_ = line.split("class ")[1]
        else:
            class_ = fields[1]
        class_  = class_.strip()
        return "new(" + class_ + ")"
    else:
        return line.split(" ", 1)[0]

def lines_to_feature_dict(lines):
    d = defaultdict(int)
    for ins in lines:
        d[ins] += 1
    for i in range(0, len(lines)):
        for j in range(i+1, len(lines)):
            d[lines[i] + "/" +  lines[j]] += 1
    return d

def dict_featurize(mod):
    res = {}
    for method, lines in mod.items():
        res[method] = lines_to_feature_dict(lines)
    return res

def parse_jsonp(src):
    MODULE = 0
    METHOD_DEFS = 1
    METHOD_BODY = 2
    state = MODULE
    curr_method = ""
    curr_method_code = []
    res = {}
    for line in src:
        sline = line.strip()
        if sline == "":
            continue
        if state == MODULE:
            if line[0] == '{':
                state = METHOD_DEFS
        elif state == METHOD_DEFS:
            curr_method = sline
            curr_method_code = []
            state = METHOD_BODY
        elif state == METHOD_BODY:
            if sline == "" or sline == "}":
                state = METHOD_DEFS if sline == "" else MODULE
                if curr_method != "":
                    res[curr_method] = curr_method_code
                curr_method = ""
                curr_method_code = []
            else:
                fields = sline.split(":", 1)
                if len(fields) == 2 and fields[0].isnumeric():
                    curr_method_code.append(normalize_line(fields[1].strip()))

    return res

def build_dataset(inpath):
    dataset = {}
    for root, dirs, files in os.walk(inpath):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            if file.endswith(".class"):
                file_path = root + os.sep + file
                print(len(path) * '---', file)
                process = Popen(["javap", "-v", file_path], stdout=PIPE)
                (output, err) = process.communicate()
                exit_code = process.wait()
                output = output.decode()
                lines = output.split("\n")
                #print(lines)
                res = parse_jsonp(lines)
                res = dict_featurize(res)
                dataset[file_path] = res
    return dataset

def flatten(dataset):
    res = []
    for path, feature_dicts in dataset.items():
        for method, feature_dict in feature_dicts.items():
            res.append(feature_dict)
    return res

if __name__ == "__main__":

    inpath = sys.argv[1]
    #outpath = sys.argv[2]
    dataset = build_dataset(inpath)
    dataset = flatten(dataset)
    print(json.dumps(dataset, indent=4))
    #with open(inpath) as fd:
    #    res = parse_jsonp(fd)
    #res = dict_featurize(res)
    #print(json.dumps(res, indent=4))
    #feature_vecs = [feature_vec for method, feature_vec in res.items()]
    #print(feature_vecs)
    #vectorizer = DictVectorizer(sparse=False)
    #X = vectorizer.fit_transform(feature_vecs)
    #print(X)
