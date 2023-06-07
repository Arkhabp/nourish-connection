from flask import Flask,redirect,url_for,render_template,request, url_for, jsonify
from pymongo import MongoClient
import jwt as pyjwt
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

SECRET_KEY = 'NOURISH'
app.secret_key = 'NOURISH'
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

@app.route('/register_save', methods=['POST'])
def register_save():
    username_receive = request.form["username_give"]
    namaUsaha_receive = request.form["namaUsaha_give"]
    password_receive = request.form["password_give"]
    sosialMedia_receive = request.form["sosialMedia_give"]
    kategori_receive = request.form["kategori_give"]
    daerah_receive = request.form["daerah_give"]
    deskripsiUsaha_receive = request.form["deskripsiUsaha_give"]
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    doc = {
        "username" : username_receive,
        "nama_usaha" : namaUsaha_receive,
        "password" : password_hash,
        "sosial_media" : sosialMedia_receive,
        "kategori" : kategori_receive,
        "daerah" : daerah_receive,
        "deskripsi_usaha" : deskripsiUsaha_receive,
        "status" : "nonactive"
    }
    db.users.insert_one(doc)
    return jsonify({'result':'success'})

@app.route('/register',methods=['GET'])
def register():
    return render_template("register.html")

@app.route('/tentang_nourish',methods=['GET'])
def tentang_nourish():
   
    return render_template('tentang-nourish.html')

@app.route('/umkm_list',methods=['GET'])
def umkm_list():
   
    return render_template('umkm-list.html')

@app.route('/diskusi',methods=['POST'])
def diskusi():
   
    return render_template('diskusi.html')

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/profil/<username>',methods=['GET'])
def user(username):
   
    return render_template('profil.html')

@app.route('/umkm_page',methods = ['GET'])
def umkm_page():
     return render_template('umkm-page.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)