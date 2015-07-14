import pandas as pd
import re
import nltk


class CorefOutputParser:

    def __init__(self, file):
        self.entity_dict = {}
        self.df = pd.read_csv(file, sep='\t', header=None)
        self.df.columns = ["document_name", "some id", "sentence_word_nr", "word", "pos_tag", "parsing_part", "", "", "", "", "", "coref"]
        self.count = 0
        self.count_removed_sents = 0

    def __get_entity(self, coref_num, start_index):

        entity = ""
        search_length = 5
        good_tags = ["DT", "NNP", "NNS", "NN", "NNPS", "PRP", "PRP$", "JJ", "JJR", "JJS", "CC", "CD", "POS", "IN"]
        important_tags = ["NNP", "NNS", "NN", "NNPS"]
        found_end = False
        end_index = None
        contains_important_tag = False

        for index in range(start_index, start_index + search_length):

            if index >= self.df.shape[0]:
                break

            if not isinstance(self.df.ix[index, "coref"], str):
                continue  # jump to next index

            entity += self.df.ix[index, "word"] + " "

            # check for bad pos_tags in entity
            if self.df.ix[index, "pos_tag"] not in good_tags:
                return None, None

            if self.df.ix[index, "pos_tag"] in important_tags:
                contains_important_tag = True

            # find end of entity
            coref = self.df.ix[index, "coref"]
            digits_in_coref = re.findall("\d+", coref)
            if ")" in coref and str(coref_num) in digits_in_coref:
                found_end = True
                end_index = index
                break

        if found_end and contains_important_tag:
            return entity.strip(), end_index
        else:
            return None, None

    def __create_entity_dict(self):
        """
        private
        """
        current_coref_num = None

        for index, row in self.df.iterrows():
            if isinstance(row["coref"], str):
                match = re.search("\d+", row["coref"])
                if match is not None:
                    current_coref_num = int(match.group())

                if "(" in row["coref"] and ")" in row["coref"]:
                    tmp_entity = row["word"]
                    if current_coref_num not in self.entity_dict:
                        self.entity_dict[current_coref_num] = tmp_entity
                elif "(" in row["coref"]:
                    tmp_entity, end_index = self.__get_entity(current_coref_num, index)
                    if tmp_entity is not None and current_coref_num not in self.entity_dict:
                        self.entity_dict[current_coref_num] = tmp_entity

    def get_resolved_text(self):
        self.__create_entity_dict()

        self.count = 0
        self.count_removed_sents = 0
        total_text = ""
        sent_text = ""
        coref_num = None
        sent_contains_entity = False

        length = self.df.shape[0]
        index = 0

        while index < length:
            row = self.df.loc[index]
            found_entity = False
            if isinstance(row["coref"], str):

                if row["sentence_word_nr"] == 0:
                    if sent_contains_entity:
                        total_text += sent_text
                    else:
                        self.count_removed_sents += 1

                    sent_text = ""
                    sent_contains_entity = False

                match = re.search("\d+", row["coref"])
                if match is not None:
                    coref_num = int(match.group())
                    sent_contains_entity = True

                if "(" in row["coref"] and ")" in row["coref"] and coref_num in self.entity_dict:
                    sent_text += self.entity_dict[coref_num] + " "
                    self.count += 1
                    found_entity = True
                elif "(" in row["coref"] and coref_num in self.entity_dict:
                    tmp_entity, end_index = self.__get_entity(coref_num, index)
                    if tmp_entity:
                        sent_text += self.entity_dict[coref_num] + " "
                        index = end_index
                        self.count += 1
                        found_entity = True

                if not found_entity:
                    sent_text += row["word"] + " "

            index += 1

        total_text = "\n".join(nltk.sent_tokenize(total_text))
        total_text = total_text.replace("-RRB-", ")")
        total_text = total_text.replace("-LRB-", "(")

        return total_text

    def get_orig_text(self):
        text = ""
        for index, row in self.df.iterrows():
            text += row["word"] + " "

        return text

    def print_df(self):
        print(self.df[["word", "coref"]].to_string())
