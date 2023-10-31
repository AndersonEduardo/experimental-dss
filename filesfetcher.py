import requests
import csv
import os

from bs4 import BeautifulSoup
from urllib.parse import unquote

from parameters import *


class FilesFetcher:

    def __init__(self):
        
        self.url = self.__set_url()
        self.narrative_keyword = self.__set_narrative_keyword()
        self.topicname_keyword = self.__set_topic_keyword()
        self.panelname_keyword = self.__set_panelname_keyword()
        self.soup = self.__set_soup()

    
    def __set_soup(self):

        response = requests.get(self.url + '/list')

        return BeautifulSoup(response.text, 'html.parser')


    def __set_topic_keyword(self) -> str:

        return TOPICNAME_KEYWORD


    def __set_panelname_keyword(self) -> str:

        return  PANELNAME_KEYWORD


    def __set_narrative_keyword(self) -> str:

        return NARRATIVE_KEYWORD


    def __set_url(self) -> str:

        return ACR_GUIDELINES_LIST_URL


    def fetch_file_links(self) -> list:

        links = list()
        links_raw = self.soup.select('a')

        for link in links_raw:

            link_class = link.get('class')

            if link_class is None:
    
                continue

            elif not isinstance(link_class, list):
    
                link_class = link_class.lower()
    
            else:

                link_class = ' '.join(link_class).lower()

            link_href = link.get('href').lower()

            if 'wordwrap downloadlink' in link_class and\
            'litsearch' not in link_href and \
            (self.panelname_keyword.lower() in link_href or \
             self.topicname_keyword.lower() in link_href or \
             self.narrative_keyword.lower() in link_href):

                links.append(link)

        return links


    def fetch_extant_files(self) -> list:

        output = list()
        item = dict()
        found_narrative = False
        found_panel = False
        found_topic = False

        links = self.fetch_file_links()

        for link in links:

            if found_narrative == False and self.narrative_keyword.lower() in link.get('href').lower():
                
                found_narrative = True

                item[self.narrative_keyword.lower()] = (
                    link.get('href') 
                    if 'http' in link.get('href') 
                    else self.url + link.get('href')
                )

            elif found_topic == False and self.topicname_keyword.lower() in link.get('href').lower():
                
                found_topic = True

                item['topic'] = link.get('href').split(f'{self.topicname_keyword}=')[1].replace('%20', ' ').strip()

            elif found_panel == False and self.panelname_keyword.lower() in link.get('href').lower():
                
                found_panel = True

                item['panel'] = link.get('href').split(f'{self.panelname_keyword}=')[1].replace('%20', ' ').strip()

            else:

                raise TypeError('Inconsistent data found.')
            
            if (found_narrative == True) and (found_panel == True) and (found_topic == True):
                
                output.append(item)

                item = dict()

                found_narrative = False
                found_panel = False
                found_topic = False

        return output


    @staticmethod
    def to_csv(output:list, filename:str="acr_guidelines_data.csv") -> None:

        keys = output[0].keys()
        
        with open(filename, "w") as file:

            csvwriter = csv.DictWriter(file, keys)
            csvwriter.writeheader()
            csvwriter.writerows(output)


    def _fetch_pdf(self, url:str, filename:str) -> None:

        filename = unquote(filename)
        filename = filename.replace(':','--')
        filepath = os.path.join(PDF_PATH,  filename + '.pdf')

        print('[STATUS] Downloading file:', filename, '...')
        response = requests.get(url)
        print('[STATUS] ...download finished.')

        pdf = open(filepath, 'wb')
        pdf.write(response.content)
        pdf.close()


    def fetch_pdfs(self, topic_key:str = None, panel_key:str = None) -> None:
        
        urls = self.fetch_extant_files()

        for item in urls:

            (narrative, topic, panel) = item.values()

            if topic_key is not None:

                if topic_key.strip().lower() in topic.strip().lower():

                    self._fetch_pdf(
                        url = narrative,
                        filename = topic.strip().lower().replace(' ', '_')
                    )
            
            if panel_key is not None:

                if panel_key.strip().lower() in panel.strip().lower():

                    self._fetch_pdf(
                        url = narrative,
                        filename = topic.strip().lower().replace(' ', '_')
                    )
