from flask import Flask,redirect,url_for,render_template,request, url_for, jsonify
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
import requests
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname
from dotenv import load_dotenv

app=Flask(__name__)
dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

@app.route('/',methods=['GET','POST'])
def home():
   
    return render_template('index.html')

@app.route('/save_coba', methods=['POST'])
def save_data():
    nama_receive = request.form['nama_give']

    doc = {
        'nama_pemesan' : nama_receive,
    }

    db.data.insert_one(doc)
    return jsonify({
        'result' : 'success',
        'msg' : 'data was saved!!!',
    })

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)