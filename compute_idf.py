from jvm_embedding import *
import sys
import json

inpath = sys.argv[1]
outpath = sys.argv[2]
dataset, df, n_methods = build_dataset(inpath)
idf = compute_idf(df, n_methods)
print(json.dumps(idf, indent=4))
with open(outpath, 'w') as fd:
    json.dump(idf, fd, indent=4)
print("Total", n_methods, "methods")
