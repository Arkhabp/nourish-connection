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

@app.route('/admin',methods=['GET'])
def admin():
    return render_template('admin.html')

@app.route('/tentang_nourish',methods=['GET'])
def tentang_nourish():
   
    return render_template('tentang-nourish.html')

@app.route('/umkm_list',methods=['GET'])
def umkm_list():
   
    return render_template('umkm-list.html')

@app.route('/diskusi',methods=['POST'])
def diskusi():
   
    return render_template('diskusi.html')

@app.route('/register',methods=['GET'])
def register():
    return render_template("register.html")

@app.route('/login',methods=['GET'])
def login():
   
    return render_template('login.html')

@app.route('/profil/<username>',methods=['GET'])
def user(username):
   
    return render_template('profil.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)