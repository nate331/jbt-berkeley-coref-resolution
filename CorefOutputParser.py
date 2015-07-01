import numpy as np
import pandas as pd
import re
import os, sys

class CorefOutputParser:
    
    def __init__(self, file):
        self.entity_dict = {}
        self.df = pd.read_csv(file, sep='\t', header=None)
        self.df.columns = ["document_name","some id", "sentence_word_nr", "word", "pos_tag", "parsing_part", "", "", "", "", "", "coref"]
    
    def __create_entity_dict(self):
        '''
        private
        '''
        current_entity = ""
        in_entity = False
        current_coref_num = None
        
        for index, row in self.df.iterrows():
            #print("!!!!----!!!!")
            #print(row["coref"])
            if (isinstance(row["coref"], str)):
                match = re.search("\d+", row["coref"])
                if match != None:
                    current_coref_num = int(match.group())
                
                if "(" in row["coref"] and ")" in row["coref"]:
                    current_entity = row["word"]
                    if current_coref_num not in self.entity_dict:
                        self.entity_dict[current_coref_num] = current_entity
                    current_entity = ""
                    in_entity = False
                elif "(" in row["coref"]:
                    in_entity = True
                    current_entity = row["word"] + " "
                elif ")" in row["coref"]:
                    current_entity += row["word"]
                    if current_coref_num not in self.entity_dict:
                        self.entity_dict[current_coref_num] = current_entity
                    in_entity = False
                    current_entity = ""
                elif in_entity == True:
                    current_entity += row["word"] + " "
    
    def get_resolved_text(self):
        self.__create_entity_dict()
        
        self.count = 0
        text = ""
        in_entity = False
        coref_num = None
        for index, row in self.df.iterrows():

            if (isinstance(row["coref"], str)):
                match = re.search("\d+", row["coref"])
                if match != None:
                    coref_num = int(match.group())
                    
                if "(" in row["coref"] and ")" in row["coref"]:
                    text += self.entity_dict[coref_num]
                    self.count += 1
                elif "(" in row["coref"]:
                    in_entity = True
                elif ")" in row["coref"]:
                    text += self.entity_dict[coref_num]
                    self.count += 1
                    in_entity = False
                elif in_entity == False:
                    text += row["word"] + " "
            
        return text
    
    def get_orig_text(self):
        text = ""
        for index, row in self.df.iterrows():    
            text += row["word"] + " "
            
        return text
    
    def print_df(self):
        print(self.df[["word", "coref"]].to_string())
