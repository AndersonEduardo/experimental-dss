from parameters import *
from decisiontable import *
from invertedindex import *


class Autocomplete:

    def autocomplete_category(self, query:str = None, **kwargs) -> dict:

        if query is None:

            return {
            'adherent_category_labels': None
        }

        else:

            if not isinstance(query, str):

                raise TypeError('`query` must be a python str.')


        lbii_category = LevenshteinBasedInvertedIndex()
        category_corpus = set()


        dtab = DecisionTable(PARAMETERS)
        dtab.build()


        for i in range(len(dtab.rules)):

            category_corpus.update({dtab.rules[i][f'rule {i+1}'].get('CATEGORY')})


        lbii_category.get_inverted_index(category_corpus)

        query_output_category = lbii_category.search(query, search_mode=1, full_output=False)

        query_output_category['score'] = query_output_category['score'].astype(float)

        query_output_category = query_output_category.pivot_table(
            index = 'label',
            columns = 'query_token',
            values = 'score',
            # fill_value = 0
            fill_value = 1e10,  # atencao aqui, se mudar o modo de computar o score
            aggfunc = min  # atencao aqui, se mudar o modo de computar o score
        )

        category_idx = query_output_category\
            .apply(
                # lambda x: all(x.values >= THESHOLD4LBII),  
                lambda x: all(x.values <= SCORE_THESHOLD),  # atencao aqui, se mudar o modo de computar o score
                axis=1
            )\
            .values

        query_output_category = query_output_category[category_idx]

        query_output_category = query_output_category\
            .mean(axis=1)\
            .reset_index(drop=False)\
            .rename(columns={0:'score'})\
            .sort_values(by='score', ascending=False)

        category_label = query_output_category["label"].tolist()

        return {
            'adherent category labels': category_label,
        }


    def autocomplete_subcategory(self, query:str = None, selected_category:str = None) -> dict:

        print('- query', query)
        print('- selected_category', selected_category)
        print('- type(query)', type(query))
        print('- type(selected_category)', type(selected_category))
        print('-selected_category is None:', selected_category is None)

        if selected_category is None or not isinstance(selected_category, str):

                raise TypeError('`selected_category` must be a python str.')
        
        else:

            selected_category = selected_category.strip().lower()

        if query is not None:

            if not isinstance(query, str):

                raise TypeError('`query` must be a python str.')


        lbii_subcategory = LevenshteinBasedInvertedIndex()
        subcategory_corpus = set()


        dtab = DecisionTable(PARAMETERS)
        dtab.build()


        for i in range(len(dtab.rules)):

            if dtab.rules[i][f'rule {i+1}'].get('CATEGORY') == selected_category:

                subcategory_corpus.update({dtab.rules[i][f'rule {i+1}'].get('SUBCATEGORY')})


        lbii_subcategory.get_inverted_index(subcategory_corpus)


        if query is None:

            full_output = set()

            for value in lbii_subcategory.inverted_index.values():

                full_output.update(value)

            return {
                'adherent subcategory labels': list(full_output)
            }

        query_output_subcategory = lbii_subcategory.search(query, search_mode=1, full_output=False)

        query_output_subcategory['score'] = query_output_subcategory['score'].astype(float)

        query_output_subcategory = query_output_subcategory.pivot_table(
            index = 'label',
            columns = 'query_token',
            values = 'score',
            # fill_value = 0
            fill_value = 1e10,  # atencao aqui, se mudar o modo de computar o score
            aggfunc = min   # atencao aqui, se mudar o modo de computar o score
        )

        subcategory_idx = query_output_subcategory\
            .apply(
                # lambda x: all(x.values >= THESHOLD4LBII),
                lambda x: all(x.values <= SCORE_THESHOLD),  # atencao aqui, se mudar o modo de computar o score
                axis=1
            )\
            .values

        query_output_subcategory = query_output_subcategory[subcategory_idx]

        query_output_subcategory = query_output_subcategory\
            .mean(axis=1)\
            .reset_index(drop=False)\
            .rename(columns={0:'score'})\
            .sort_values(by='score', ascending=False)

        subcategory_label = query_output_subcategory["label"].tolist()


        return {
            'adherent subcategory labels': subcategory_label
        }
