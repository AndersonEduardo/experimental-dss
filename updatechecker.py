import requests
import pickle
import boto3

import datetime as dt
from bs4 import BeautifulSoup

from parameters import *

class UpdateChecker:

    def __init__(self):

        self.__soup = self.__set_soup()
        self.__keyword = self.__set_narrative_keyword()
        self.__last_update_file_name = self.__set_last_update_file_name()
        self.__bucket = self.__set_bucket()
        self.__last_update = self.__set_last_update()


    def __set_bucket(self):

        return BUCKET_NAME

    
    def __set_last_update_file_name(self):

        return LAST_UPDATE_FILE_NAME


    def __set_soup(self) -> BeautifulSoup:
        '''Instancia e retorna um objeto `BeautifulSoup`.'''

        response = requests.get(ACR_GUIDELINES_URL)

        return BeautifulSoup(response.text, 'html.parser')


    def __set_narrative_keyword(self) -> str:
        '''Retorna a string contendo a palavra-chave para a 
        busca do campo das URLs de atualização no website do
        ACR guidelines.'''

        return NARRATIVE_KEYWORD


    def __set_last_update(self) -> list:
        '''Retorna a lista com as URLs das últimas 
        narrativas atualizadas.'''

        try:
            # with open(LAST_UPDATE_PATH, 'rb') as f:

            #     last_update = pickle.load(f)

            file_name = self.__last_update_file_name
            bucket_name = self.__bucket
            s3 = boto3.resource('s3')
            # obj = s3.Object(self.__bucket, self.__last_update_file_name)
            obj = s3\
                .Bucket(bucket_name)\
                .Object(file_name)\
                .get()['Body']\
                .read()
            last_update = pickle.loads(obj)

        except:

            last_update = list()

        return last_update


    def _get_narratives_url(self, section) -> list:
        '''Dada uma seção do website (extraída através do 
        BeautifulSoup), encontra a lista de URLs das narrativas.'''

        output = list()

        for a_tag in section.find_all('a', recursive=True):

            if a_tag is not None:

                a_text = a_tag.get('href')

                if a_text is not None:
                    
                    if self.__keyword in a_text.lower():

                        output.append(a_text)

        return output


    def _get_narratives(self) -> list:
        '''Encontra a lista de atualizações na seção (extraída do website
        do ACR guidelines) fornecida como input.'''

        sections = self.__soup.find_all('section')

        if len(sections) > 0:

            for section in sections:

                if section is not None:

                    a_tags = section.find_all('a', recursive = True)

                    if len(a_tags) > 0:

                        for a_tag in a_tags:

                            if a_tag is not None and a_tag.get('id') is not None:

                                if a_tag.get('id').lower() == 'new':

                                    return self._get_narratives_url(section)

            return []

        else:

            return []


    def _build_lastest_update(self, contents:list) -> None:
        '''Se encotradas novas atualizações no website do ACR
        guidelines, atualiza os dados de updates mais recentes.'''

        # with open(LAST_UPDATE_PATH, 'wb') as f:
            
        #     pickle.dump(contents, f)

        file_name = self.__last_update_file_name
        bucket_name = self.__bucket
        s3 = boto3.resource('s3')
        obj = pickle.dumps(contents)
        s3.Object(bucket_name, file_name).put(Body=obj)

        self.__last_update = self.__set_last_update()


    def check_for_updates(self) -> dict:
        '''Método principal da classe. Compara a lista de narrativas
        obtidas mais recentemente com a lista de narrativas obtida na
        última checagem por atualizações.'''

        contents = list()

        current_update = self._get_narratives()

        for x in current_update:

            if x not in self.__last_update:

                contents.append(x)

        if len(contents) > 0:

            self._build_lastest_update(current_update)

        else:

            contents = ['No updates for now.']


        checkpoint = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        output = {
            'checkpoint': checkpoint,
            'contents': contents
        }

        print(f'[{checkpoint} :: UPDATE-CHECKER STATUS] Outputs found:\n {output}\n')

        return output