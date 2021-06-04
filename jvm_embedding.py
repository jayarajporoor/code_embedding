#Copyright (c) Jayaraj Poroor
#Released under MIT License

import sys
import json
import os
from subprocess import Popen, PIPE
from math import log, sqrt

from collections import defaultdict
from sklearn.feature_extraction import DictVectorizer


def lines_to_feature_dict(lines, df):
    d = defaultdict(float)
    features = set()
    n_features = 0
    #unigrams:
    for ins in lines:
        d[ins] += 1
        features.add(ins)
        n_features += 1
    #bigram subsequences:
    for i in range(0, len(lines)):
        for j in range(i+1, len(lines)):
            f  = lines[i] + "/" +  lines[j]
            d[f] += 1
            features.add(f)
            n_features += 1
    if df is not None:
        for f in features:
            df[f] += 1
        for k in d.keys():
            d[k] = d[k] / n_features
    return d

def dict_featurize(mod, df):
    res = {}
    n_methods = 0
    for method, lines in mod.items():
        res[method] = lines_to_feature_dict(lines, df)
        n_methods += 1
    return res, n_methods

def build_tf_df(inpath):
    tf_dataset = {}
    df = defaultdict(float)
    n_methods = 0
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
                res, n_mod_methods = dict_featurize(res, df)
                tf_dataset[file_path] = res
                n_methods += n_mod_methods
                print("processed", n_mod_methods, "methods")
    return tf_dataset, df, n_methods

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
                    for method, method_features in res.items():
                        features_line = " ".join(list(method_features.keys()))
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
        if state == MODULE:
            if line != "" and line[0] == '{':
                state = METHOD_DEFS
        elif state == METHOD_DEFS:
            if sline.endswith(";"):
                sline = sline[0:-1]
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


if __name__ == "__main__":
    pass
