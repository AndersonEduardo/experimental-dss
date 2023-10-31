import pylightxl as xl
from operator import itemgetter
from parameters import *


class DecisionTable():

    def __init__(self, filepath:str) -> None:

        self.rules = list()
        self.actions = list()
        self.conditions = set()
        self.__filepath = filepath
        self.datatypes = self.__set_parameters_datatypes()


    def _rank(self, x, top_n=1):
        '''Rank the scored outputs, considering the User query.'''
        
        counter = 0
        output = list()
        last_score = None

        x = sorted(x, key=itemgetter('ADHERECE_SCORE'), reverse=True)
            
        for i, d_i in enumerate(x):

            if i == 0:

                output.append(d_i)
                last_score = d_i.get('ADHERECE_SCORE')
                counter += 1

            else:

                if last_score == d_i.get('ADHERECE_SCORE'):

                    output.append(d_i)

                else:

                    if counter < top_n:

                        output.append(d_i)
                        last_score = d_i.get('ADHERECE_SCORE')
                        counter += 1

                    else:

                        break

        return output


    def __set_parameters_datatypes(self) -> dict:

        return PARAMETERS_DATATYPES


    def set_datatype(self, parameter, value:list) -> list:

        if not isinstance(parameter, str) and \
           not isinstance(value, list):

            raise TypeError('`parameter` must be a python str, and `value` must be a python list.')

        datatype = self.datatypes.get(parameter)

        if datatype[0] == int:

            return [int(float(v)) for v in value]
        
        elif datatype[0] == float:

            return [float(v) for v in value]

        elif datatype[0] == str:

            return [str(v) for v in value]

        else:

            raise TypeError('The only supported datatypes are: int, float and str.')


    def load_xlsx(self) -> None:

        xlsx_file = xl.readxl(fn=self.__filepath)
        sheet_names = xlsx_file.ws_names

        # COLUMNS_FOR_INDEX = [str(x).strip().upper() for x in COLUMNS_FOR_INDEX]
        # COLUMNS_FOR_OUTPUT_VARIABLES = [str(x).strip().upper() for x in COLUMNS_FOR_OUTPUT_VARIABLES]

        for sheet_name in sheet_names:

            sheet_data = xlsx_file.ws(ws=sheet_name)

            # condition_keys = [str(x).strip().upper() for x in sheet_data.row(1)][3:]
            # action_keys = [str(x).strip().upper() for x in sheet_data.row(1)][:3]
            # condition_keys = [
            #     str(x).strip().upper() 
            #     for x in sheet_data.row(1)
            #     if str(x).strip().upper() in [str(y).strip().upper() for y in COLUMNS_FOR_INDEX]
            # ]
            conditions = {x for x in sheet_data.row(1) if str(x).strip().upper() in COLUMNS_FOR_INDEX}
            self.conditions.update(conditions)

            # action_keys = [
            #     str(x).strip().upper() 
            #     for x in sheet_data.row(1)
            #     if str(x).strip().upper() in [str(y).strip().upper() for y in COLUMNS_FOR_OUTPUT_VARIABLES]
            # ]
            action_keys = [i for (i, x) in enumerate(sheet_data.row(1)) if str(x).strip().upper() in COLUMNS_FOR_OUTPUT_VARIABLES]


            # print('condition_keys:', condition_keys) # TODO: apagar
            # print('action_keys:', action_keys) # TODO: apagar
            # print('sheet_data.col(col=1):', sheet_data.col(col=1)) # TODO: apagar

            sheet_columns = sheet_data.row(1)
            sheet_columns = [x.strip().upper() for x in sheet_columns]

            for i in range(2, len(sheet_data.col(col=1)) + 1):

                rule = dict()
                action = dict()

                for j in range(len(sheet_columns)):

                    row_data = [str(x).strip() for x in sheet_data.row(i)]
                    # rule_data = row_data[i] for i in condition_keys
                    # action_data = row_data[i] for i in action_keys

                    # rule = {
                    #     k:(row_data[i] 
                    #         if not isinstance(row_data[i], str) 
                    #         else row_data[i].lower()) 
                    #        for (i,k) in enumerate(condition_keys)
                    # }
                    # action = {
                    #     k:row_data[i+4]
                    #     for (i,k) in enumerate(action_keys)
                    # }

                    if sheet_columns[j] in COLUMNS_FOR_INDEX:
                        rule.update(
                            {sheet_columns[j]:row_data[j]}
                        )
                    elif sheet_columns[j] in COLUMNS_FOR_OUTPUT_VARIABLES:
                        action.update(
                            {sheet_columns[j]:row_data[j]}
                        )
                    else:
                        raise ColumnException('Sheet column names must be either a rule our an action.')

                self.rules.append({f'rule {i-1}': rule})
                self.actions.append({f'action for rule {i-1}': action})

            # self.conditions.update(condition_keys)

        if (len(self.rules) == 0) or (len(self.actions) == 0) or (len(self.rules) != len(self.actions)):

            raise IndexError("`rules` and `actions` must have the same length.")


    def build(self) -> None:

        self.load_xlsx()


    def query(self, x:dict, top_n:int = None, **kwargs) -> list:

        full_output = kwargs.get('full_output')

        if not isinstance(x, dict):

            raise TypeError("`x` must be a python dict.")

        if not all(k in ['CATEGORY', 'SUBCATEGORY'] for k in x.keys()):

            raise Exception(
                'User query must be a python dict with the keys `CATEGORY` and `SUBCATEGORY`'
            )

        print('-x:', x)

        # if len(x['CATEGORY']) > 1:

        #     raise AssertionError('Only one value must be provided at CATEGORY.')

        # if len(x['SUBCATEGORY']) > 1:

        #     raise AssertionError('Only one value must be provided at SUBCATEGORY.')

        user_input = x.values()

        # user_input_raw = x.copy()
        # user_input = list()

        # for l in user_input_raw.values():

        #     if len(l) == 0:

        #         user_input.extend([''])
            
        #     else:

        #         user_input.extend(l)

        top_n = (top_n if top_n is not None else len(self.actions))

        output_actions = self.actions.copy()


        for i in range(len(self.rules)):

            score = 0

            rule_i = [x.strip().lower() for x in self.rules[i][f'rule {i+1}'].values()]

            score = sum([value.strip().lower() in rule_i for value in user_input])

            output_actions[i][f'action for rule {i+1}']['ADHERECE_SCORE'] = score


        if full_output:

            return output_actions
        
        else:

            output_actions = [x[f'action for rule {i+1}'] for (i,x) in enumerate(output_actions)]

            return self._rank(output_actions, top_n)
