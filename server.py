"""
A server that lets the user type in a sql query and if it is a select statement,
generates a json file using jinja 2.

Then it displays the json file using d3 graphics


"""
import psycopg2
import psycopg2.extras
import time
from construct_json import constructJson
import sys
from flask import Flask,jsonify, render_template,url_for,g
from jinja2 import FileSystemLoader,Environment
import flask_sijax
import os
import sijax
path = os.path.join('.', os.path.dirname(__file__), 'static/sijax/js/new')

app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/sijax/js/json2.js'
flask_sijax.Sijax(app)


# Functions registered with @flask_sijax.route can use Sijax
@flask_sijax.route(app, '/hello')
def hello():
    #Executed when submit button is pushed
    def query_execute(obj_response,query_text:str):
        #prepare text
        print(obj_response.__class__)
        text = query_text.strip().lower()
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
            Make a json object where the nested layers are determined by this rule:
            Columns with less unique values are further toreward the outside
            '''
            jso = constructJson(records,columns)
            saveToFile(jso, 'query.json')

        else:
            obj_response.alert("Please write a select query.")
            return
    def get_data():
        return open('query.json','r').read()
    g.sijax.register_callback('query_execute', query_execute)
    g.sijax.register_callback('get_data', get_data)
    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it

        return g.sijax.process_request()
    #Display using jinja
    loader = FileSystemLoader('templates')
    env = Environment(loader=loader)
    template = env.get_template('HomePage.html')
    # get template from available templates
    return (template.render(g=g))
@flask_sijax.route(app, '/query',methods=['GET','POST'])
def query():
    return open('query.json','r').read()
def get_credentials(filename):
    keys = loadfile(filename)
    db_userName= keys[0]
    db_passWord= keys[1]
    db_host= keys[2]
    db_name = keys[3]
    return db_userName,db_passWord,db_host,db_name

def loadfile(filename):
    with open(filename) as f:
        items = f.readline().strip().split(',')
        return items

def saveToFile(content,fileName):

    with open(fileName,'w') as f:
        f.write(content)
def getAstCols(text):
    tableSchema = text.split('from')[1]
    keys = ['where', 'group', 'order', 'limit']
    for key in keys:
        tableSchema = tableSchema.split(key)[0]
    print(tableSchema)
    table = tableSchema.split('.')[1].strip()
    schema = tableSchema.split('.')[0].strip()
    queryText = "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = '"+table+"'"
    cursor.execute(queryText)
    records = cursor.fetchall()
    records = [x[0] for x in records]
    return records

t = time.time()


# i = sys.argv.index('server:app')
i = 0
def connect():
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
# Extend BaseResponse
class SijaxJson(sijax.response.BaseResponse):
    def json(self, data):
        #return data
        params = {"json": data}
        return self._add_command("json", params)

cursor = connect()
print("Time elapsed: " + str(time.time() - t) + " s.")
app.run(host='0.0.0.0', port=5001)

