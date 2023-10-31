import os
import unidecode
import nltk

# trazendo stopwords
nltk.download('punkt')
nltk.download('stopwords')

# URL do website onde sao publicadas os arquivos PDFs
ACR_GUIDELINES_LIST_URL = 'https://acsearch.acr.org'

# palavras chave para o web scraper
NARRATIVE_KEYWORD = 'Narrative'
TOPICNAME_KEYWORD = 'TopicName'
PANELNAME_KEYWORD = 'PanelName'

# URL do website onde sao publicadas as atualizacoes 
ACR_GUIDELINES_URL = 'https://www.acr.org/Clinical-Resources/ACR-Appropriateness-Criteria'

# palavra chave para capturar a URL das novas narrativas
NARRATIVE_KEYWORD = 'narrative'

# caminho para o pickle do last update
LAST_UPDATE_FILE_NAME = 'last_update.pickle'  # para aws s3

# nome do arquivo creds
CREDS_FILENAME = 'creds.pickle'

# caminho para as informacoes de email
CREDS_PATH = f'./{CREDS_FILENAME}'

# template do html para o email
HTML_TEMPLATE = '''<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>checkpoint</th>
      <th>contents</th>
    </tr>
  </thead>
  <tbody>\n#contents# </tbody>
</table>'''

# nome do bucket na aws
BUCKET_NAME = 'bot-acr-guidelines'

PARAMETERS_DATATYPES = {
	# 'MEDICAL_RECORD': [int],
	# 'DAYSBACK': [int],
	# 'TOP_N': [int, type(None)],

	'IDADE': [str],
	'SEXO': [str],
	'INDICAÇÃO CLÍNICA': [str],
	'SUBCATEGORIA': [str],
	'EXAME DE IMAGEM': [str],
	'GRAU DE ADEQUAÇÃO': [str],
	'CUSTO RELATIVO': [int, str],
	'DOSE RELATIVA DE RADIAÇÃO': [int, str],
	'DETALHES': [str]
}

# AGE_DICTIONARY = {
#     'até 1 ano, 11 meses e 29 dias': 	range(0,2),
#     '2 a 18, 11 meses e 29 dias': 		range(2, 19),
#     'a partir de 19 anos': 				range(19, 200),
#     'indiferente para idade': 			[None]
# }

AGE_DICTIONARY = {
    'criança': range(0, 16 + 1),
    'adulto': range(17, 50 + 1),
    'sênior': range(51, 200),
    '<30 anos': range(0,30 +1),
    '<40 e >74 anos': list(range(0, 40)) + list(range(75, 200)),
    '>25 anos': range(26, 200),
    '>30 anos': range(31, 200),
    '≥ 30 anos': range(30, 200),
    '≥25 anos': range(25, 200),
    '≥40 anos': range(40, 200),
    '30-39 anos': range(30, 39 + 1),
    '40-74 anos': range(40, 74 + 1),
	'indiferente para idade': [None]
    }

# caminho para o conjunto de dados dos parametros
PARAMETERS = './data/dataset/knowledge_base.xlsx'
# PARAMETERS = './data/dataset/example_dataset_manually.xlsx'

# caminho para pasta onde ficarao os PDFs
PDF_PATH = os.path.join('data','pdfs')
if not os.path.exists(PDF_PATH):
    os.makedirs(PDF_PATH)

# caminho para onde ficara a planilha de URLs
URL_PATH = os.path.join('data','urls')
if not os.path.exists(URL_PATH):
    os.makedirs(URL_PATH)

# colunas da base de dados que serao usadas no multi-index do dataframe
# COLUMNS_FOR_INDEX = ['IDADE', 'SEXO', 'INDICAÇÃO CLÍNICA', 'SUBCATEGORIA']
COLUMNS_FOR_INDEX = ['CATEGORY', 'SUBCATEGORY']

# colunas da base de dados que serao usadas no dataframe de output do modelo
# COLUMNS_FOR_OUTPUT_VARIABLES = ['EXAME DE IMAGEM', 'GRAU DE ADEQUAÇÃO', 
#                                 'CUSTO RELATIVO', 'DOSE RELATIVA DE RADIAÇÃO', 
#                                 'DETALHES']
COLUMNS_FOR_OUTPUT_VARIABLES = ['PROCEDURE', 'APPROPRIATENESS_CATEGORY', 
                                'RELATIVE_RADIATION_LEVEL']

# colunas da base de dados e sua sequencia para ordenacao dos valores nos dataframes
# COLUMNS_FOR_SORT = \
#     ['idade', 'sexo', 'indicacao_clinica', 'subcategoria', 'exame_de_imagem',
#     'grau_de_adequacao', 'custo_relativo', 'dose_relativa_de_radiacao']
COLUMNS_FOR_SORT = \
    ['procedure', 'appropriateness_category', 'relative_radiation_level']


# colunas da base de dados que contem dados numericos
NUMERIC_COLUMNS = ['RELATIVE_RADIATION_LEVEL']

# colunas da base de dados que contem dados de texto
TEXT_COLUMNS = ['PROCEDURE', 'APPROPRIATENESS_CATEGORY', 'CATEGORY', 'SUBCATEGORY']

# nomes das colunas da base de dados adicionais
COLUMNS_FOR_ADITIONAL_DATA = []

# colunas da base de dados adicionais que serao usadas no (multi-)index do dataframe
COLUMNS_FOR_ADITIONAL_DATA_INDEX = []

# colunas da base de dados que serao usadas no dataframe de output do modelo
COLUMNS_FOR_ADITIONAL_DATA_OUTPUT_VARIABLES = []

# colunas da base de dados adicionais que contem dados de texto
TEXT_COLUMNS_ADITIONAL_DATA = []

# colunas da base de dados adicionais que contem dados numericos
NUMERIC_COLUMNS_ADITIONAL_DATA = [None]

# caminho para a pasta onde fica salvo o pickle da base de dados
KNOWLEDGE_BASE = './knowledge_base/knowledge_base_raw.pickle'

# dicionario para preenchimento de valores ausentes (ou indiferentes)
INDIFFERENT_DICT = {
    'none4age': 'Indiferente para idade',
    'none4sex': 'Indiferente para sexo',
    'none4category': 'Não possui subcategoria'
    }

# labels que devem ser enderecadas para supressao de dados da base
LABELS4SUPRESS = {
    
    'radiology': [{'column': 'GRAU DE ADEQUAÇÃO', 'labels': ['inadequado']}, ],

    'laboratory': None

    }

# dicionario para conversao de idades (numeros para labels)
# AGE_INTERVALS = {range(0, 16 + 1): 'CRIANÇA', range(17, 50 + 1): 'ADULTO', range(51, 200): 'SÊNIOR'}
AGE_INTERVALS = {
    'criança': range(0, 16 + 1),
    'adulto': range(17, 50 + 1),
    'sênior': range(51, 200),
    '<30 anos': range(0,30 +1),
    '<40 e >74 anos': list(range(0, 40)) + list(range(75, 200)),
    '>25 anos': range(26, 200),
    '>30 anos': range(31, 200),
    '≥ 30 anos': range(30, 200),
    '≥25 anos': range(25, 200),
    '≥40 anos': range(40, 200),
    '30-39 anos': range(30, 39 + 1),
    '40-74 anos': range(40, 74 + 1)
    }

# lista para a ordenação do output da API (metodo predict), de acordo com a adequabilidade
# dos exames sugesridos
ADEQUABILITY_ORDER = ['Usually Appropriate', 'May Be Appropriate', 'Usually Not Appropriate']

# colunas dos dados para montagem do output do metodo autocomplete
AUTOCOMPLETE_COLUMNS_FOR_OUTPUT = ['CATEGORY', 'SUBCATEGORY']
AUTOCOMPLETE_COLUMNS_FOR_LABORATORY_OUTPUT =  ['CATEGORY', 'SUBCATEGORY'] #['component']

# caminho para o objeto com o texto "mostravel" do autocomplete
AUTOCOMPLETE_OBJECT_PATH = './data/labels/obj4autocomplete.pickle'

# (para o autocomplete) nome do modelo SBERT para a busca semantica
SBERT_MODEL = 'distiluse-base-multilingual-cased-v1'

# nome do modelo SBERT no diretorio local
LOCAL_SBERT_MODEL = './models/distiluse-base-multilingual-cased-v1-saved'

# (para o autocomplete) threshold para similaridade por coseno (valores abaixo 
# serao descartados para os outputs do autocomplete)
SCORE_THESHOLD = 1 #0.66
THESHOLD4LBII = 0.5

# (para o autocomplete) colunas para embeddings do autocomplete object
COLUMN_FOR_CLINICAL_INDICATION_EMBEDDINGS = 'indicacao_clinica_embeddings'
COLUMN_FOR_SUBCATEGORY_EMBEDDINGS = 'subcategoria_embeddings'

COLUMN_FOR_CSPRIMARY_EMBEDDINGS = 'csprimary_embeddings'
COLUMN_FOR_COMPONENT_EMBEDDINGS = 'component_embeddings'

# (para o autocomplete) limte da distancia de Levenshtein para a busca 
# no indice invertido
LEVENSHTEIN_THRESHOLD = 3

# (para o autocomplete) lista de stopwords em portugues, para o 
# indice invertido
nltk.download('stopwords')
STOPWORDS = nltk.corpus.stopwords.words('portuguese')

# (no autocomplete) tamanho maximo para que o algoritmo do indice 
# invertido nao quebre a palavra/token em pedacoes menores
LARGETOKEN = 10

# (no autocomplete) quando a palavra/token eh muito grande, o 
# algoritmo de indice invertido ira quebrar ela neste tamanho
MICROTOKEN = 5

# (no autocomplete) maximo de keys/chaves no resultado da busca no 
# indice invertido
TOP_K = 5

# peso para o score obtido na busca (no autocomplete) - DEPRECATED
# NON_SEMANTIC_WEIGHT = 0.9

# pasta da base de dados de sinonimos
SYNONYMS_PATH = r'./data/synonymsdata'

# pytesseract
# If you don't have tesseract executable in your PATH, include the following:
# PYTESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
PYTESSERACT_PATH = r'C:\Users\drt67700\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# para o dataset builder #

CANONICAL_COLUMN_NAMES_TEMPLATE_1 = ['procedure', 'appropriateness_category', 'relative_radiation_level']
CANONICAL_COLUMN_NAMES_TEMPLATE_2 = ['radiologic_procedure', 'rating', 'comments', 'rrl*']
COLUMNS_ORDERING = ['procedure', 'appropriateness_category', 'relative_radiation_level', 'subcategory', 'category']
CANONICAL_NUMBER_OF_COLUMNS = 3
COLUMN_NAMES_THRESHOLD = 2
KEYTERM_FOR_VARIANTS = 'variant'
APPROPRIATENESS_DICTIONARY = {
    'Usually Not Appropriate': range(1,3+1), 
    'May Be Appropriate': range(4,6+1), 
    'Usually Appropriate': range(7,9+1)}
TEMPORARY_DIRECTORY = './tmpdir'
ACR_GUIDELINES_URL = 'https://acsearch.acr.org'
MAXSIZE_FOR_VARIANTS = 300
MINSIZE_FOR_VARIANTS = 10
BEGINING_VARIANT_PATTERN = 'variant'
LEVENSHTEIN_THRESHOLD = 3
THRESHOLD_FOR_VARIANT_INTEGRITY = 10
SAMPLE_SIZE_VARIANT_TOLKENS = 5
NAIVE_BAYES_CLASSIFIER_PATH = r'./models/naive_bayes_classifier.pkl'
TFIDF_PATH = r'./models/tfidf.pkl'
EXPERIMENT_METRICS = ['levenshtein', 'number_of_characters', 'percentual_error', 'time']


class DataParameters:
    
    @staticmethod
    def get_adjusted_parameter(parameter_name):
        '''
        Função para ajustar labels providas pelo usuário ('user 
        friendly') para o formato especificado para a API.
        '''
    
        if not isinstance(parameter_name, list):
    
            raise TypeError('`parameter_name` must be a list.')
    
        else:
    
            return [unidecode.unidecode(item).replace(' ', '_').lower() 
                    for item in parameter_name]


    @staticmethod
    def age2label(age:int) -> list:

        output = list()

        for (l, i) in AGE_INTERVALS.items():

            if age in list(i):

                output.append(l)

        return output
