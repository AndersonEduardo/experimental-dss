import random
import pandas as pd
from locust import HttpUser, task, between, SequentialTaskSet


global df
df = pd.read_excel('../data/dataset/knowledge_base.xlsx')


class UserBehavior(SequentialTaskSet):

    # def __init__(self) -> None:

    #     df = pd.read_excel('./data/dataset/knowledge_base.xlsx')

    @task
    def api_autocomplete_category(self):

        n = random.randint(1, df.shape[0])

        text_cat = df['category'].sample(n).values[0]
        # self.client.get(f'autocomplete-category?query={text_cat}', name='autocomplete-category?query=[category]')
        self.client.get(
            f'autocomplete-category?query={text_cat}', 
            name='autocomplete-category'
        )


    @task
    def api_autocomplete_subcategory(self):

        n1 = random.randint(1, df.shape[0])
        text_cat = df['category'].sample(n1).values[0]

        n2 = random.randint(1, df.query(f'category == "{text_cat}"').shape[0])
        text_sub = df.query(f'category == "{text_cat}"')['subcategory'].sample(n2).values[0]

        # self.client.get(
        #     f'autocomplete-subcategory?query={text_sub}&selected-category={text_cat}',
        #     name='autocomplete-category?query=[subcategory]'
        # )
        self.client.get(
            f'autocomplete-subcategory?query={text_sub}&selected-category={text_cat}',
            name='autocomplete-subcategory'
        )


    @task
    def api_query(self):

        n1 = random.randint(1, df.shape[0])
        text_cat = df['category'].sample(n1).values[0]

        n2 = random.randint(1, df.query(f'category == "{text_cat}"').shape[0])
        text_sub = df.query(f'category == "{text_cat}"')['subcategory'].sample(n2).values[0]

        # self.client.get(
        #     f'query?category={text_cat}&subcategory={text_sub}', 
        #     name='query?category=[category]&subcategory=[subcategory]'
        # )
        self.client.get(
            f'query?category={text_cat}&subcategory={text_sub}', 
            name='query'
        )



# class UserBehavior(SequentialTaskSet):
    
#     @task
#     def api_autocomplete(self):
#         self.client.get('autocomplete-subcategory?query=acute&selected-category=acute nonspecific chest pain-low probability of coronary artery disease')

#     @task
#     def api_query(self):
#         self.client.get('query?category=acute nonspecific chest pain-low probability of coronary artery disease&subcategory=Variant 1: Acute nonspecific chest pain; low probability of coronary artery disease. Initial Imaging.')


class WebsiteUser(HttpUser):

   tasks = [UserBehavior]
   wait_time = between(30, 60)