# import pickle

from flask import Flask, jsonify, request #, send_file, send_from_directory
from flask_csv import send_csv
# import io

from filesfetcher import *
from updatechecker import *
from dispatcher import *
from decisiontable import *
from invertedindex import *
from datasetbuilder import *
from autocomplete import *

# import zipfile

print('[STATUS] - Instantiating Flask app...')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# app.config["LABELS_FOLDER"] = "./labels/"
print('[STATUS] - ...done.')

print('[STATUS] - Buiding Decision Table...')
dtab = DecisionTable(PARAMETERS)
dtab.build()
print('[STATUS] - ...done.')

print('[STATUS] - Instantiating Files Fetcher System...')
file_fetcher_system = FilesFetcher()
print('[STATUS] - ...done.')

print('[STATUS] - Instantiating Autocomplete System...')
atcp = Autocomplete()
print('[STATUS] - ...done.')


@app.route('/', methods=['GET'])
def home():

    return jsonify(
        {
            'status': 200,
            'info': 'This is the Decision Support System. Use `/updatedata` to fecth extant \
guidelines data. Use `/autocomplete-category` or `autocomplete-subcategory` to search for \
clinical category and subcategory, respectively. Use `/query` to search for prescription \
suggestions. Use the endpoint `/example` for a query example.'
        }
    )


@app.route('/updatedata', methods=['GET'])
def updatedata():

    topic_key = request.args.get('topic', None, type=str)
    panel_key = request.args.get('panel', 'cardiac', type=str)

    print('[STATUS] - User inputs:')
    print('[STATUS]       topic:', topic_key)
    print('[STATUS]       panel:', panel_key)    

    print('[STATUS] - Fetching PDFs...')
    file_fetcher_system.fetch_pdfs(topic_key = topic_key, panel_key = panel_key)
    print('[STATUS] - ...done.')

    print('[STATUS] - DatasetBuilder setup...')
    dataset_builder_system = DatasetBuilder()
    print('[STATUS] - ...done.')

    print('[STATUS] - building tabular dataset from PDF files...')
    dataset_dict = dataset_builder_system.run()
    dataset = dataset_builder_system.consolidate(dataset_dict)
    dataset['category'] = dataset['category'].str.replace('_', ' ')
    print('[STATUS] - ...done.')

    print('[STATUS] - Saving...')
    dataset.to_excel(PARAMETERS, index=False)
    print('[STATUS] - ...done.')

    return jsonify({'status': 200})


@app.route('/autocomplete-category', methods=['GET'])
def autocomplete_category():

    query = request.args.get('query', None, type=str)

    print('[STATUS] - User inputs:', query)

    output = atcp.autocomplete_category(query)

    output = output['adherent category labels']

    return jsonify(output)


@app.route('/autocomplete-subcategory', methods=['GET'])
def autocomplete_subcategory():

    query = request.args.get('query', default=None, type=str)
    selected_category = request.args.get('selected-category', default=None, type=str)

    query = None if query == '' else query
    selected_category = None if selected_category == '' else selected_category

    print('[STATUS] - User inputs:')
    print('[STATUS]       query:', query)
    print('[STATUS]       selected_category:', selected_category)

    output = atcp.autocomplete_subcategory(query, selected_category=selected_category)

    output = output['adherent subcategory labels']

    return jsonify(output)


@app.route('/example', methods=['GET'])
def example():

    return jsonify('XXXX/query?category=breast%20pain&subcategory=Variant%202:%20Female%20with%20clinically%20significant%20breast%20pain%20(focal%20and%20noncyclical).%20Age%20less%20than%2030.%20Initial%20imaging.')


@app.route('/query', methods=['GET'])
def query():

    category = request.args.get('category', '', type=str)
    subcategory = request.args.get('subcategory', '', type=str)
    top_n = request.args.get('top_n', 1, type=int)

    user_query = {
        'CATEGORY': category,
        'SUBCATEGORY': subcategory,
    }

    print('[STATUS] - User inputs:', query)

    output = dtab.query(user_query, top_n = int(top_n))

    return jsonify(output)


@app.route('/fetch', methods=['GET'])
def fetch():
    '''
    Fetch URLs for all guidelines in ACR Appropriateness 
    Criteria web site and save it as a CSV file.
    '''

    print('[STATUS] - Fetching extant files...')
    output = file_fetcher_system.fetch_extant_files()
    print('[STATUS] - ...done.')
    
    print('[STATUS] Output:\n', output, '\n')

    keys = output[0].keys()

    return send_csv(
        output,
        "acr_guidelines_data.csv", 
        keys
    )


# @app.route('/add', methods=['GET'])
# def add_email():

#     print('[STATUS] - Instantiating Dispatcher...')
#     dispatcher = Dispatcher()
#     print('[STATUS] - ...done.')

#     print('[STATUS] - Checking for e-mail consistency...')
#     email = request.args.get('email', None)
#     print('[STATUS] - ...done.')
    
#     if email is not None and '@' in email:

#         print('[STATUS] - Adding the new e-mail...')
#         status = dispatcher.add_email(email)
#         print('[STATUS] - ...done.')

#         if status is True:

#             print('[STATUS] Email added successfully.')

#             return jsonify({ 
#                 'status': 200,
#                 'message': 'Email added successfully.'
#             })

#         else:

#             print('[STATUS] This email already exists in the database.')

#             return jsonify({ 
#                 'status': 204,
#                 'message': 'The provided email already exists in the database.'
#             })

#     else:

#         print('WARNING: The provided email is inconsistent.')

#         return jsonify({ 
#             'status': 400,
#             'message':'The provided email is inconsistent.'
#         })


# @app.route('/remove', methods=['GET'])
# def remove_email():

#     print('[STATUS] - Instantiating Dispatcher...')
#     dispatcher = Dispatcher()
#     print('[STATUS] - ...done.')

#     print('[STATUS] - Checking for e-mail consistency...')
#     email = request.args.get('email', None)
#     print('[STATUS] - ...done.')
    
#     if email is not None and '@' in email:
    
#         print('[STATUS] - Removing e-mail...')
#         status = dispatcher.remove_email(email)
#         print('[STATUS] - ...done.')

#         if status is True:

#             print('[STATUS] - E-mail removed.')

#             return jsonify({
#             'status': 200,
#             'message':'Email removed.'
#             })

#         else:

#             print('[STATUS] - The provided email was not found in the database.')

#             return jsonify({
#                 'status': 400,
#                 'message':'The provided email was not found in the database.'
#             })


#     else:

#         print('WARNING: The provided email is inconsistent.')

#         return jsonify({ 
#             'status': 400,
#             'message':'The provided email is inconsistent.'
#         })


if __name__ == '__main__':

    app.run(host="0.0.0.0", debug=False)
