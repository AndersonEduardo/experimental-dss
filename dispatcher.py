# import requests
import smtplib
import pickle
import boto3

# import datetime as dt

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from parameters import *


class Dispatcher:

    def __init__(self):
        
        self.html_template = self.set_html_template()
        self.__creds = self.__set_creds()
        self.__bucket = self.__set_bucket()


    def __set_bucket(self):

        return BUCKET_NAME


    def __set_creds(self):

        return CREDS_FILENAME


    def set_html_template(self):

        return HTML_TEMPLATE


    def __load_creds(self) -> dict:

        # with open(CREDS_PATH, 'rb') as f:
            
        #     creds = pickle.load(f)

        # return creds

        return self.__fetch_creds()


    def send_email(self, data:dict) -> None:
        '''Configura e executa, automaticamente, todo o 
        procedimento para envio de e-mail.'''

        creds = self.__load_creds()
        t = data.get('checkpoint')
        c = [
            f'   <tr>\n    <th>{i}</th>\n    <td>{t}</td>\n    <td><a href={l}>{l}</a></td>\n   </tr>\n' 
            for (i, l) in enumerate(data.get('contents'))
        ]
        output_html = self.html_template.replace('#contents#', ''.join(c))

        message = MIMEMultipart()
        message['Subject'] = "[ACR guidelines Bot] Update status"
        message['From'] = creds.get('sender')
        message['To'] = ','.join(creds.get('recipient'))

        html = MIMEText(output_html, "html")
        message.attach(html)

        with smtplib.SMTP("smtp.office365.com", 587) as server:

            server.starttls()
            server.login(creds.get('sender'), creds.get('password'))
            server.sendmail(creds.get('sender'), creds.get('recipient'), message.as_string())


    def __fetch_creds(self) -> dict:

        try:

            file_name = self.__creds
            bucket_name = self.__bucket
            s3 = boto3.resource('s3')
            obj = s3\
                .Bucket(bucket_name)\
                .Object(file_name)\
                .get()['Body']\
                .read()
            creds = pickle.loads(obj)

        except:

            raise FileNotFoundError('`creds.pickle` not found.')

        return creds


    def __save_creds(self, creds:dict) -> None:

        file_name = self.__creds
        bucket_name = self.__bucket
        s3 = boto3.resource('s3')
        obj = pickle.dumps(creds)
        s3.Object(bucket_name, file_name).put(Body=obj)


    def add_email(self, email:str) -> bool:

        creds = self.__fetch_creds()
        recipient = creds.get('recipient')

        if recipient is not None:

            if email not in recipient:

                creds['recipient'].append(email)
                status = True

            else:

                status = False

        else:

            creds['recipient'] = [email]
            status = True

        self.__save_creds(creds)

        return status


    def remove_email(self, email:str) -> bool:

        creds = self.__fetch_creds()
        recipient = creds.get('recipient')

        if email.strip() in recipient:

            creds['recipient'].remove(email)
            self.__save_creds(creds)

            return True
        
        else:

            return False
