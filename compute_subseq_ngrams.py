from jvm_embedding import *
import sys
import json

inpath = sys.argv[1]
outpath = sys.argv[2]
n_methods = build_subseq_ngrams(inpath, outpath)
print("Total", n_methods, "methods")
