from flask import Flask,redirect,url_for,render_template,request, url_for, jsonify, session
from pymongo import MongoClient
from jwt import encode as jwt_encode
import jwt
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
TOKEN_KEY='mytoken'
app.secret_key = 'NOURISH'
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

@app.route('/',methods=['GET','POST'])
def home():
        if 'username' in session:
                button_text = 'Profil'
                button_url = '/profil'
                user_info = db.users.find_one({'username': session['username']})
                if user_info is None:
                    # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
                    session.clear()
                    return redirect(url_for('login'))
        else:
            button_text = 'Masuk'
            button_url = '/login'
            user_info = None

        return render_template('index.html', button_text=button_text, button_url=button_url, user_info=user_info) 
    #code sebelumnya 
        # if request.method == 'POST':
        #     # Handle POST Request here
        #     return render_template('home.html')
        # if 'username' in session:
        #     button_text = 'Profil'
        #     button_url = '/profil'
        # else:
        #     button_text = 'Masuk'
        #     button_url = '/login'
        # print(session)
        # return render_template('index.html', button_text=button_text, button_url=button_url)
# baru ditambah
@app.route('/home')
def go_home():
    # Logika dan tampilan halaman home
        if 'username' in session:
            button_text = 'Profil'
            button_url = '/profil'
            user_info = db.users.find_one({'username': session['username']})
            if user_info is None:
                # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
                session.clear()
                return redirect(url_for('login'))
        else:
            button_text = 'Masuk'
            button_url = '/login'
            user_info = None

        return render_template('index.html', button_text=button_text, button_url=button_url, user_info=user_info)   
    
   
@app.route('/admin', methods=['GET'])
# @admin_required
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
        "profile_pic": "",
        "profile_pic_real": "profil_pics/profile_placeholder.jpg",
        "cover_pic": "",
        "cover_pic_real": "cover_pics/cover_placeholder.jpeg",
        "status" : "nonactive",
        "role" : "umkm"
    }
    db.users.insert_one(doc)
    return jsonify({'result':'success'})

@app.route('/sign_up/check_dup', methods=['POST']) 
def check_dup():
     username_receive = request.form.get('username_give')
     user = db.users.find_one({'username' : username_receive})
     exists = bool(user)
     return jsonify({'result':'success', 'exists' : exists})

@app.route('/register',methods=['GET'])
def register():
    return render_template("register.html")

@app.route('/tentang_nourish',methods=['GET'])
def tentang_nourish():
        if 'username' in session:
            button_text = 'Profil'
            button_url = '/profil'
            user_info = db.users.find_one({'username': session['username']})
            if user_info is None:
                # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
                session.clear()
                return redirect(url_for('login'))
        else:
            button_text = 'Masuk'
            button_url = '/login'
            user_info = None

        return render_template('tentang-nourish.html', button_text=button_text, button_url=button_url, user_info=user_info)     
    

@app.route('/umkm_list',methods=['GET'])
def umkm_list():
    if 'username' in session:
            button_text = 'Profil'
            button_url = '/profil'
            user_info = db.users.find_one({'username': session['username']})
            if user_info is None:
                # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
                session.clear()
                return redirect(url_for('login'))
    else:
        button_text = 'Masuk'
        button_url = '/login'
        user_info = None
    return render_template('umkm-list.html', button_text=button_text, button_url=button_url, user_info=user_info)   

@app.route('/login', methods=['GET'])
def login():
    msg=request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/go_login',methods=['POST'])
def go_login():
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

            # baru ditambahin
            if result['role'] == 'admin':
                return jsonify(result="success", token=token, role=result['role']) #barudiubah
            else:
                return jsonify(result="success", token=token, role=result['role']) #barudiubah

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
        # return jsonify({
        #     "result": "fail",
        #     "msg": "We could not find a user with that id/password combination"
        # })
        return jsonify(result="fail", msg="We could not find a user with that id/password combination")
    
@app.route('/logout')
def logout():
# Logika dan tampilan halaman home
    if 'username' in session:
        button_text = 'keluar'
        button_url = '/'
        user_info = db.users.find_one({'username': session['username']})
        session.clear()
        if user_info is None:
            # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
            session.clear()
            return redirect(url_for('login'))
    else:
        button_text = 'Masuk'
        button_url = '/login'
        user_info = None

    return render_template('index.html', button_text=button_text, button_url=button_url, user_info=user_info)   

@app.route('/user/<username>',methods=['GET'])
def user(username):
    button_text = 'Profil'
    button_url = '/profil'
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        status = username == payload.get('id')
        user_info = db.users.find_one(
            {'username' : username}, 
            {'_id' : False}
        )
        if user_info is None:
            user_info = {}  # Inisialisasi user_info sebagai dictionary kosong jika tidak ditemukan
        return render_template(
           'user.html', button_text=button_text, button_url=button_url, user_info=user_info, status=status
        )
        # return render_template('user.html', button_text=button_text, button_url=button_url, user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    # return render_template('profil.html')

@app.route('/update_profile', methods = ['POST'])
def update_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username = payload.get('id')

        sosialMedia_receive = request.form['sosialMedia_give']
        deskripsi_receive = request.form['deskripsi_give']
        
        new_doc = {
            'sosial_media' : sosialMedia_receive,
            'deskripsi_usaha' : deskripsi_receive
        }
        if 'sampul_give' in request.files:
            file = request.files['sampul_give']
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f'cover_pics/{username}.{extension}'
            file.save('./static/' + file_path)
            new_doc['cover_pic'] = filename
            new_doc['cover_pic_real'] = file_path

        if 'profile_give' in request.files:
            file = request.files['profile_give']
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f'profil_pics/{username}.{extension}'
            file.save('./static/' + file_path)
            new_doc['profile_pic'] = filename
            new_doc['profile_pic_real'] = file_path

        db.users.update_one(
            {'username' : username},
            {'$set' : new_doc}
        )

        return jsonify({
            'result': 'success',
            'msg' : 'Your profile has been update'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route('/umkm_page',methods = ['GET'])
def umkm_page():
     return render_template('umkm-page.html')

@app.route('/diskusi',methods=['GET'])
def diskusi():
    if 'username' in session:
            button_text = 'Profil'
            button_url = '/profil'
            user_info = db.users.find_one({'username': session['username']})
            if user_info is None:
                # Jika user_info tidak ditemukan, hapus sesi dan arahkan pengguna ke halaman login
                session.clear()
                return redirect(url_for('login'))
    else:
        button_text = 'Masuk'
        button_url = '/login'
        user_info = None
    return render_template('diskusi.html', button_text=button_text, button_url=button_url, user_info=user_info)   

@app.route('/show_preview_umkm', methods = ['GET'])
def show_preview_umkm_get():
        namaUsaha= list(db.users.find({}, {'_id': False}).sort('username', -1))
        return jsonify({
            'namausaha' : namaUsaha,
        })
         

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)