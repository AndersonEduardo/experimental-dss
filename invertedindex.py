import Levenshtein
import os
import pandas as pd

from nltk.tokenize import word_tokenize
from parameters import *
from decisiontable import *


class InvertedIndex:

    def __init__(self) -> None:
        
        self.inverted_index = dict()
        self.stopwords = STOPWORDS
        self.microtoken = MICROTOKEN
        self.largetoken = LARGETOKEN


    def _reset_inverted_index(self) -> None:

        self.inverted_index = dict()


    def get_inverted_index(self, corpus:list, return_output:bool = False) -> dict:

        self._reset_inverted_index()

        for sentence in corpus:

            tokens = [x.strip().lower() 
                      for x in word_tokenize(sentence.lower().strip()) 
                      if x not in self.stopwords]
            tokens = [x 
                      for x in tokens 
                      if x not in '.,;!?/\-(){}[]0123456789=+_"<>']

            for key in tokens:
                
                if key not in self.inverted_index:

                    self.inverted_index[key] = {sentence}

                else:

                    self.inverted_index[key].update({sentence})

                # if len(key) > self.largetoken:

                #     for i in range(len(key)):

                #         if (i + self.microtoken) <= len(key):

                #             self.inverted_index[ key[i:(i + self.microtoken)] ] = { sentence }

        if return_output is True:

            return self.inverted_index


    def _get_synonyms_tokenized(self, sin_list:list) -> set:

        tokenized = set()

        for s in sin_list:

            tokenized.update({
                x 
                for x in word_tokenize(s) 
                if x not in STOPWORDS
            })

        return tokenized


    def _load_synonyms(self, synonyms_path:str = None) -> dict:

        if synonyms_path is None:
            
            synonyms_path = SYNONYMS_PATH


        filepaths = [os.path.join(synonyms_path, x) 
                    for x in os.listdir(synonyms_path)]

        synonyms_raw = dict()
        synonyms = dict()


        for filepath in filepaths:

            df = pd.read_excel(
                filepath, 
                usecols=['TERMO', 'SINÔNIMOS']
            )

            df['SINÔNIMOS_SPLIT'] = df.apply(
                lambda x: [w.strip().lower() 
                        for w in x['SINÔNIMOS'].strip().split(';')], 
                axis=1
            )

            synonyms_raw.update(
                df[['TERMO', 'SINÔNIMOS_SPLIT']].\
                    set_index('TERMO').\
                    transpose().\
                    to_dict(orient='records')[0]
            )


        for (k, v) in synonyms_raw.items():

            k_splitted = k.split()

            if len(k_splitted) > 1:

                for token in k_splitted:

                    synonyms.update({token.strip().lower(): set(v)})

            else:

                synonyms.update({k.strip().lower(): set(v)})


        del synonyms_raw

        return synonyms


    def add_synonyms(self, synonyms:dict = None) -> None:
        
        if synonyms is None:

            # synonyms = self._load_synonyms()
            raise NotImplementedError('For now, only implemented for direct input using a python dict.')

        for (sin_dict_key, sin_dict_val) in synonyms.items():

            sin_dict_val_tokenized = self._get_synonyms_tokenized(sin_dict_val)

            for token in sin_dict_val_tokenized:

                ii_labels = self.inverted_index.get(token)

                if ii_labels is None:

                    self.inverted_index.update({token: {sin_dict_key}})

                else:

                    self.inverted_index[token].update({sin_dict_key})


class LevenshteinBasedInvertedIndex(InvertedIndex):

    def __init__(self) -> None:

        self.k_output = set()
        self.top_k = TOP_K
        self.levenshtein_threshold = LEVENSHTEIN_THRESHOLD
        super().__init__()


    def _mode_01(self, query:str, return_tokens:bool) -> list:

        k_output = None
        d_output = None
        query_tokenized = [x 
                           for x in word_tokenize(query.lower().strip()) 
                           if x not in self.stopwords]

        for k in self.inverted_index.keys():

            for query_token in query_tokenized:

                d = Levenshtein.distance(query_token, k)

                if k_output is None:

                    k_output = [k]
                    d_output = [d]
                    q_output = [query_token]

                else:

                    # este `top_k` eh para chaves do indice invertido, 
                    # e NAO para o output (i.e., `labels` no output).
                    if len(k_output) < self.top_k: 

                        k_output.append(k)
                        d_output.append(d)
                        q_output.append(query_token)

                    else:

                        if d <= max(d_output):

                            d_output.append(d)
                            k_output.append(k)
                            q_output.append(query_token)

                            idx_max = d_output.index(max(d_output))

                            d_output.pop(idx_max)
                            k_output.pop(idx_max)
                            q_output.pop(idx_max)

        if k_output is None:

            return pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])
        
        elif len(k_output) == 0:
            
            return pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])

        else:

            k_output_sorted = [(i,j,k) 
                for (i,j,k) in sorted(zip(d_output, k_output, q_output), reverse=False)]

            output_raw = [(self.inverted_index[j], i, j, k) 
                          for (i,j,k) in k_output_sorted]

            output = pd.DataFrame(columns=['label', 'score', 'key', 'query_token'])

            for (l,s,k,q) in output_raw:

                for l_ in l:

                    output = output.append({'label': l_, 
                                            'score': s,
                                            'key': k,
                                            'query_token': q}, ignore_index=True)

            # eliminando outputs duplicados e resetando o indice do dataframe
            output = output\
                        .reset_index(drop=True)\
                        # .drop_duplicates(subset='label')


        if return_tokens is True:

            return (query_tokenized, output)

        else:

            return output.reset_index(drop=True)


    def _mode_02(self, query:str, full_output:bool = False) -> list:

        output = set()
        query_tokenized = [x.strip().lower()
                           for x in word_tokenize(query.lower().strip()) 
                           if x not in self.stopwords]

        # print('self.inverted_index:\n', self.inverted_index)

        for (k, v) in self.inverted_index.items():

            similarity = Levenshtein.seqratio([k.strip().lower()], query_tokenized)

            # print('- k', k)
            # print('- v', v)
            # print('- similarity', similarity)

            if similarity >= SCORE_THESHOLD:

                if full_output == False:

                    output.update(v)
                
                elif full_output == True:

                    output.add((tuple(v), similarity))
                
                else:

                    raise Exception('`full_output` must be a python bool (either True or False).')

        return list(output)


    def search(self, query:str, return_tokens:bool = None, 
               search_mode:int = 2, **kwargs) -> list:

        if search_mode == 1:

            return self._mode_01(query=query, return_tokens=return_tokens)

        elif search_mode == 2:

            full_output = kwargs.get('full_output')
            full_output = False if full_output is None else full_output

            return self._mode_02(query=query, full_output=full_output)

        else:

            raise Exception('`search_mode` must be a python int, either 1 or 2.')
