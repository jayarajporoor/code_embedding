# Java code embeddings from compiled class files for code similarity tasks

### Summary

A novel and simple approach for generating source code embeddings for code similarity tasks.

The approach works by compiling the high level source code to a typed intermediate language. Here we demonstrate for Java using the JVM instruction set. For other languages such as C/C++, LLVM intermediate language could be used.

We take the instruction sequence in each method (function calls are abstracted using the parameter and return types) and generate the following features:

* Each instruction is a unigram feature.
* We may take every k-subsequence in the instruction sequence to generate a k-gram feature.
  * Currently we generate for binary subsequence and generate 2-gram features.

During the learning phase, the IDF values for the features are generated and stored in a JSON file.

During similarity checking, the TF vectors are generated and scaled using the IDF values. Cosine similarity of vectors are used.

### Running

#### IDF generation:

```console
python compute_idf.py <folder containing class files> <IDF output path>
```

The folder containing class files is recursively searched for class files and the IDF is computed by aggregating data from all methods in all the class files.

#### Similarity checking

```console
python compute_similarity.py <folder containing class files> <IDF path>
```

The IDF path must point to a previously computed IDF file. All the class files are read and pair-wise similarity of all methods are printed.

### Pre-computed

The file test/idf_commons_lang.json contains IDF computed from all the class files in the Apache Commons Lang library.

### Citing

If you are using or extending this work as part of your research, please cite as:

Poroor, Jayaraj, "Java code embeddings from compiled class files for code similarity tasks", (2021), GitHub repository, https://github.com/jayarajporoor/code_embedding

BibTex:

    @misc{Poroor2021,
       author = {Poroor, Jayaraj},
       title = {Java code embeddings from compiled class files for code similarity tasks},
       year = {2021},
       publisher = {GitHub},
       journal = {GitHub repository},
       howpublished = {\url{https://github.com/jayarajporoor/code_embedding}}
    }
