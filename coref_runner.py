import os
from CorefOutputParser import CorefOutputParser

if __name__ == "__main__":

    input_file_name = ""

    print("--preprocessing....")
    os.system("java -cp berkeleycoref-1.1.jar -Xmx5g edu.berkeley.nlp.coref.preprocess.PreprocessingDriver ++base.conf \
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
    os.system("java -jar -Xmx5g berkeleycoref-1.1.jar ++base.conf \
                  -execDir tmp \
                  -modelPath models/coref-rawtext-final.ser \
                  -testPath output_preprocessing \
                  -outputPath output_coref/berkeley_output.txt \
                  -mode PREDICT")
    
    print("--preparing output file (remove first and last line) ...")
    readFile = open("./output_coref/berkeley_output.txt")
    lines = readFile.readlines()
    readFile.close()
    w = open("tmp/berkeley_output_tmp.txt",'w')
    w.writelines([item for item in lines[1:-1]])
    w.close()

    print("--generating textfile with resolutions...")
    corefOutputParser = CorefOutputParser("tmp/berkeley_output_tmp.txt")
    
    #corefOutputParser.print_df()

    new_text = corefOutputParser.get_resolved_text()
    print("-- number of resolved referenes: ", corefOutputParser.count)

    #corefOutputParser.create_entity_dict()
    #corefOutputParser.entity_dict

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
        except Exception, e:
            print e

    print("SUCCESSFULLY FINISHED")

