#How to run

1. Download models:
http://nlp.cs.berkeley.edu/downloads/berkeleycoref-1.0-models.tgz
2. Move all the models into models/ folder
3. create empty folder output_preprocessing/ (empty folder is not commited by git)
4. move your input txt file into input/ (only one file should be in the folder)
5. run "python coref_runner.py"
6. find output: output_coref/xyz-resolved.txt

Maybe you have to increase memory limit: Replace -Xmx10g at two places in coref_runner.py with something bigger (library recommends 30g)
