__author__ = 'bernhard'

import os
import shutil
import subprocess

from qa_jbt.utils.paths import create_paths

from jbt_berkeley_coref_resolution.CorefOutputParser import CorefOutputParser


def do_coreference(article_content, data_path=os.path.join('.', 'data'), max_memory=6):

    temp_path = os.path.join(os.path.normpath(data_path), 'coref_temp')
    jar_home = os.path.normpath(os.path.join(data_path, '..', '..', 'jbt_berkeley_coref_resolution'))
    paths = {
        'input': os.path.join(temp_path, 'input'),
        'preprocess': os.path.join(temp_path, 'output_preprocessing'),
        'output': os.path.join(temp_path, 'output_coref'),
        'exec_p': os.path.join(temp_path, 'exec_p'),
        'exec_c': os.path.join(temp_path, 'exec_c')
    }

    create_paths(data_path, temp_path, [paths['input'], paths['preprocess'], paths['output']])

    # write to file
    with open(os.path.join(paths['input'], 'article'), mode='w', encoding='utf-8') as o:
        o.writelines(article_content)

    # call preprocessor
    try:
        output = subprocess.check_output(
            "java -cp berkeleycoref-1.1.jar "
            "-Xmx{}g "
            "edu.berkeley.nlp.coref.preprocess.PreprocessingDriver "
            "++base.conf "
            "-execDir {} "
            "-inputDir {} "
            "-outputDir {} "
            "-skipSentenceSplitting true "
            "-respectInputLineBreaks true".format(
                max_memory,  # max Heap size in GB
                paths['exec_p'],
                paths['input'],
                paths['preprocess']
            ),
            cwd=jar_home,
            shell=True
        )
        print(output)
    except subprocess.CalledProcessError as e:
        print(e)
        return None

    # rename file for later use
    os.rename(
        os.path.join(paths['preprocess'], 'article'),
        os.path.join(paths['preprocess'], 'article.auto_conll')
    )

    # extracting coreferences
    try:
        output = subprocess.check_output(
            "java -jar -Xmx{}g berkeleycoref-1.1.jar "
            "++base.conf "
            "-execDir {} "
            "-modelPath {} "
            "-testPath {} "
            "-outputPath {} "
            "-mode PREDICT".format(
                max_memory,  # max memory for process
                paths['exec_c'],  # execDir for coreference
                os.path.join('models', 'coref-rawtext-final.ser'),  # model path
                paths['preprocess'],  # input path
                os.path.join(paths['preprocess'], 'berkeley_output_temp')  # output file
            ),
            cwd=jar_home,
            shell=True
        )
        print(output)
    except subprocess.CalledProcessError as e:
        print(e)
        return None

    # preparing output
    with open(os.path.join(paths['preprocess'], 'berkeley_output_temp'), mode='r', encoding='utf-8') as input_file:
        lines = input_file.readlines()
        with open(os.path.join(paths['output'], 'article-coref-raw'), mode='w', encoding='utf-8') as output_file:
            output_file.writelines(lines[1:-1])

    # get parsed output file
    lines = CorefOutputParser(os.path.join(paths['output'], 'article-coref-raw')).get_resolved_text()

    # remove temp path after running
    shutil.rmtree(temp_path)

    return lines
