# How to run

1. Download models:
http://nlp.cs.berkeley.edu/downloads/berkeleycoref-1.0-models.tgz
2. Move all the models into models/ folder
3. move your input txt file into input/ (only one file should be in the folder)
4. run "python3 coref_runner.py"
5. find output: output_coref/xyz-resolved.txt

Maybe you have to increase memory limit: Replace -Xmx10g at two places in coref_runner.py with something bigger (library recommends 30g)
