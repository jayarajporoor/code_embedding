from cfg_embedding import *
import sys
import json
import gensim
import numpy as np
inpath = sys.argv[1]
vecpath = sys.argv[2]
if len(sys.argv) > 3:
    scale = float(sys.argv[3])
else:
    scale = 1.0

def similarity(v1, v2):
    #return np.dot(v1, v2)
    return np.linalg.norm(v1 - v2)/scale

model = gensim.models.KeyedVectors.load_word2vec_format(vecpath, binary=False)

dataset, n_methods = build_path_features(inpath)

method_embeddings = {}
for path, method_features in dataset.items():
    method_embeddings[path] = {}
    for  method, feature_dicts in method_features.items():
        for feature_dict in feature_dicts:
            vec = sum(model[f]*v for f, v in feature_dict.items() if f in model)
            if method in method_embeddings[path]:
                method_embeddings[path][method] += vec
            else:
                method_embeddings[path][method] = vec

for path1, method_features1 in dataset.items():
    for method1, feature_dict1 in method_features1.items():
        print()
        print(path1, "@", method1, "vs: ")
        res = []
        for path2, method_features2 in dataset.items():
                for method2, feature_dict2 in method_features2.items():
                    if path1 == path2 and method1 == method2:
                        continue
                    sim = similarity(method_embeddings[path1][method1], method_embeddings[path2][method2])
                    res.append( (path2 + " " + method2, sim))
        res.sort(reverse=False, key=lambda t: t[1])
        for target, sim in res:
            print("    ", target, ":", sim)
