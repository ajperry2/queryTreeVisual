

"""
A server that lets the user type in a sql query and if it is a select statement,
generates a json file using jinja 2, displaying it with a d3 collapsible tree.

"""


import psycopg2
import psycopg2.extras
import time
from construct_json import constructJson
import sys
from flask import Flask,g
from jinja2 import FileSystemLoader,Environment
import flask_sijax
import os
import sijax


#instantiate server variables
path = os.path.join('.', os.path.dirname(__file__), 'static/sijax/js/new')
app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/sijax/js/json2.js'
flask_sijax.Sijax(app)


#Homepage
@flask_sijax.route(app, '/home')
def home():
    #Executed when submit button is pushed or e
    def query_execute(obj_response,query_text:str):
        #prepare text given in text field
        text = query_text.strip().lower()
        #don't allow the deletion of data
        if 'drop' in text:
            obj_response.alert("Please do no try to hurt my data!")
            return
        elif 'select' == text.split(' ')[0]:
            #execute query to get a list of tuples
            try:
                cursor.execute(text)
            except: # lost cursor
                cursor = connect()
                cursor.execute(text)
            records = cursor.fetchall()
            #failing gracefully
            if len(records) == 0:
                obj_response.alert("There were no results to show")
                return
            #get collumn names, used to label columns
            columns = text.split('select')[1].split('from')[0].split(',')
            if len(columns) == 1 and  columns[0].strip() == '*':
                columns = getAstCols(text)
            ''' 
            Save a json file where the nested layers are determined by this rule:
            Columns with less unique values are further towards the outside
            '''
            jso = constructJson(records,columns)
            saveToFile(jso, 'query.json')
        #wrong kind of query
        else:
            obj_response.alert("Please write a select query.")
            return
    #return the data when the file has been changed
    def get_data():
        return open('query.json','r').read()
    g.sijax.register_callback('query_execute', query_execute)
    g.sijax.register_callback('get_data', get_data)
    if g.sijax.is_sijax_request:
        return g.sijax.process_request()
    #Display the page
    loader = FileSystemLoader('templates')
    env = Environment(loader=loader)
    template = env.get_template('HomePage.html')
    return (template.render(g=g))

#Sijax method that returns the json file
@flask_sijax.route(app, '/query',methods=['GET','POST'])
def query():
    return open('query.json','r').read()


#helper method to input the database credentials in a secure manner
def get_credentials(filename):
    keys = loadfile(filename)
    db_userName= keys[0]
    db_passWord= keys[1]
    db_host= keys[2]
    db_name = keys[3]
    return db_userName,db_passWord,db_host,db_name


#parse a csv
def loadfile(filename):
    with open(filename) as f:
        items = f.readline().strip().split(',')
        return items


def saveToFile(content,fileName):
    with open(fileName,'w') as f:
        f.write(content)


#if * is used in query returns a list of the columnames for parsing
def getAstCols(text):
    tableSchema = text.split('from')[1]
    keys = ['where', 'group', 'order', 'limit']
    for key in keys:
        tableSchema = tableSchema.split(key)[0]
    print(tableSchema)
    table = tableSchema.split('.')[1].strip()
    schema = tableSchema.split('.')[0].strip()

    column_names = "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = '"+table+"'"
    try:
        cursor.execute(column_names)
    except:  # lost cursor
        cursor = connect()
        cursor.execute(column_names)
    records = cursor.fetchall()
    records = [x[0] for x in records]
    return records

t = time.time()


# i = sys.argv.index('server:app')
i = 0

def connect():
    '''
    A helper function to connect to the postgres database
    Returns a cursor object
    '''
    #get credentials to log into database
    cred_file_name = sys.argv[i + 1]
    user,secret,host,dbname= get_credentials(cred_file_name)
    conn_string = "host="+host+" dbname="+dbname+" user="+user+" password="+secret
    #connect
    try:
        conn=psycopg2.connect(conn_string)
        conn.set_session(readonly=True, autocommit=True)
        cursor = conn.cursor()
        return cursor
    except:
        print("I am unable to connect to the database.")

        

cursor = connect()
app.run(host='0.0.0.0', port=5001)

