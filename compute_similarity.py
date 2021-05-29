from jvm_embedding import *
import sys
import json

inpath = sys.argv[1]
idfpath = sys.argv[2]
dataset, df, n_methods = build_dataset(inpath)
with open(idfpath) as fd:
    idf = json.load(fd)

for path, method_features in dataset.items():
    for  method in method_features.keys():
        feature_dict = method_features[method]
        for f in feature_dict.keys():
            feature_dict[f] = feature_dict[f] * idf.get(f, 1.0)

for path1, method_features1 in dataset.items():
    for path2, method_features2 in dataset.items():
        if path1 == path2:
            continue
        for method1, feature_dict1 in method_features1.items():
            for method2, feature_dict2 in method_features2.items():
                sim = dict_cosine(feature_dict1, feature_dict2)
                print(path1, method1, "vs", path2, method2, ":", sim)
