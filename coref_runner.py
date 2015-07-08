import os
from CorefOutputParser import CorefOutputParser
import sys, getopt

if __name__ == "__main__":
    
    skipCorefBasics = False 
    try:
       opts, args = getopt.getopt(sys.argv[1:],"hs")
    except getopt.GetoptError:
       print('coref_runner.py [-s] \n s: skip berkeley coref resolution und starting with the already processed files')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print('coref_runner.py [-s] \n s: skip berkeley coref resolution und starting with the already processed files')
          sys.exit()
       elif opt == "-s":
          skipCorefBasics = True

    input_file_name = ""

    #get filenames
    dir = "./input"
    fnames = os.listdir(dir)
    for fname in fnames:        
        name = fname.split(".")[0]
        input_file_name = name

    if not skipCorefBasics:

        print("--preprocessing....")
        os.system("java -cp berkeleycoref-1.1.jar -Xmx10g edu.berkeley.nlp.coref.preprocess.PreprocessingDriver ++base.conf \
                    -execDir tmp \
                    -inputDir input \
                    -outputDir output_preprocessing")

        print("--changing file endings...")
        dir = "./output_preprocessing"
        fnames = os.listdir(dir)
        for fname in fnames:        
            name = fname.split(".")[0]
            input_file_name = name
            print(fname)
            if name != "":
                os.rename(os.path.join(dir, fname), os.path.join(dir, name + ".auto_conll"))

        print("--extracting coreferences...")
        os.system("java -jar -Xmx10g berkeleycoref-1.1.jar ++base.conf \
                      -execDir tmp \
                      -modelPath models/coref-rawtext-final.ser \
                      -testPath output_preprocessing \
                      -outputPath tmp/berkeley_output_tmp.txt \
                      -mode PREDICT")

        print("--preparing output file (remove first and last line) ...")
        readFile = open("tmp/berkeley_output_tmp.txt")
        lines = readFile.readlines()
        readFile.close()
        w = open("output_coref/" + input_file_name + "-coref-raw.txt",'w')
        w.writelines([item for item in lines[1:-1]])
        w.close()


    print("--generating textfile with resolutions...")
    corefOutputParser = CorefOutputParser("output_coref/" + input_file_name + "-coref-raw.txt")

    new_text = corefOutputParser.get_resolved_text()
    print("-- number of resolved referenes: ", corefOutputParser.count)
    print("-- number of removed sents (lacking entity): ", corefOutputParser.count_removed_sents)

    w = open("output_coref/" + input_file_name + "-resolved.txt",'w')
    w.write(new_text)
    w.close()

    #delete preprocessing files
    folder = 'output_preprocessing'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    print("SUCCESSFULLY FINISHED")

