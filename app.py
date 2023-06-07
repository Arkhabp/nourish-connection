from flask import Flask,redirect,url_for,render_template,request, url_for, jsonify, session
from pymongo import MongoClient
from jwt import encode as jwt_encode
from datetime import datetime, timedelta
import hashlib
import requests
import os
from werkzeug.utils import secure_filename
from os.path import join, dirname
from dotenv import load_dotenv
from functools import wraps


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
        if request.method == 'POST':
            # Handle POST Request here
            return render_template('home.html')
        if 'username' in session:
            button_text = 'Profil'
            button_url = '/profil'
        else:
            button_text = 'Masuk'
            button_url = '/login'
        return render_template('index.html', button_text=button_text, button_url=button_url)
   
@app.route('/login_admin', methods=['POST'])
def login_admin():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
            "status": "admin"
        }
    )

    if result:
        session['username'] = result['username']
        return jsonify({
            "result": "success",
            "msg": "Login successful"
        })
    else:
        return jsonify({
            "result": "fail",
            "msg": "Invalid admin credentials"
        })
    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            # Periksa apakah pengguna memiliki akses admin
            # Misalnya, dengan memeriksa status pengguna di database
            username = session['username']
            user = db.users.find_one({"username": username})
            if user and user['status'] == 'admin':
                return f(*args, **kwargs)
        # Jika pengguna tidak memiliki akses admin, arahkan ke halaman lain
        return redirect(url_for('home'))
    return decorated_function

@app.route('/admin', methods=['GET'])
@admin_required
def admin():
    users = db.users.find()
    return render_template('admin.html', users=users)

@app.route('/admin/update_status', methods=['POST'])
def update_status():
    username = request.form['username']
    status = request.form['status'] # 'active' atau 'nonactive'

    result = db.users.update_one(
        {"username": username},
        {"$set": {"status": status}}
    )

    if result.modified_count > 0:
        return jsonify({
            "result": "success",
            "msg": "User status updated"
        })
    else:
        return jsonify({
            "result": "fail",
            "msg": "Failed to update user status"
        })

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

@app.route('/go_login', methods=['GET'])
def go_login():
    msg=request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/login',methods=['POST'])
def login():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        session['username'] = result['username']
        if result['status'] == 'active':
            payload = {
                "id": username_receive,
                # the token will be valid for 24 hours
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt_encode(payload, SECRET_KEY, algorithm='HS256')

            return jsonify({
                "result": "success",
                "token": token
            })
        else:
            return jsonify({
                "result": "fail",
                "msg": "Your account is not active"
            })
    else:
        return jsonify({
            "result": "fail",
            "msg": "We could not find a user with that id/password combination"
        })

@app.route('/profil/<username>',methods=['GET'])
def user(username):
   
    return render_template('profil.html')

@app.route('/umkm_page',methods = ['GET'])
def umkm_page():
     return render_template('umkm-page.html')

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)