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
from bson import ObjectId


app=Flask(__name__)
dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN_KEY = os.environ.get("TOKEN_KEY")
app.secret_key = os.environ.get("app.secret_key")
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session:
            user_info = db.users.find_one({'username': session['username']})
            if user_info is None or user_info['role'] != 'admin':
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
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
        "profile_pic": "",
        "profile_pic_real": "profil_pics/profile_placeholder.jpg",
        "cover_pic": "",
        "cover_pic_real": "cover_pics/cover_placeholder.jpeg",
        "status" : "nonactive",
        "role" : "umkm",
        "registration_time": datetime.now()
    }
    db.users.insert_one(doc)
    db.users.create_index([("registration_time", -1)]) 
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
    umkm = db.users.find_one({})
    return render_template('umkm-list.html', button_text=button_text, button_url=button_url, user_info=user_info, umkm=umkm)   

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

@app.route('/get_umkm_page',methods=['GET'])
def get_umkm_page():
    namaUsaha = request.cookies.get('namaUsaha')
    umkm_data = db.users.find_one({'nama_usaha': namaUsaha}, {'_id' : False})
    return jsonify({'umkm_data':umkm_data})

@app.route('/umkm_page')
def umkm_page():
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
    nama_usaha = request.args.get('namaUsaha')
    return render_template('umkm-page.html', nama_usaha=nama_usaha, button_text=button_text, button_url=button_url, user_info=user_info)

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
        namaUsaha= list(db.users.find({}, {'_id': False}).sort('registration_time', -1))
        return jsonify({
            'namausaha' : namaUsaha,
        })
        
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username' : payload.get('id')})
        topik_receive = request.form.get('topik_give')
        date_receive = request.form.get('date_give')
        doc = {
            'username' : user_info.get('username'),
            'nama_usaha' : user_info.get('nama_usaha'),
            'topik' : topik_receive,
            'date' : date_receive,
            'profile_pic_real' : user_info.get('profile_pic_real')
        }
        db.posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg' : 'Posting successful!'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route('/get_posts', methods =['GET'])
def get_posts():
    token_receive = request.cookies.get(TOKEN_KEY)
    comments = db.comment.find({})
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username_receive = request.args.get('username_give')
        if username_receive == '':
            posts = list(db.posts.find({}).sort('date', -1).limit(20))
        else:
            posts = list(db.posts.find({'username':username_receive}).sort('date', -1).limit(20))
        for post in posts:
            post['_id'] = str(post['_id'])
            post['count_thumbsup'] = db.likes.count_documents({
                'post_id' : post['_id'],
                'type' : 'thumbsup'
            })

            post['thumbsup_by_me'] = bool(db.likes.find_one({
                'post_id' : post['_id'],
                'type' : 'thumbsup',
                'username' : payload.get('id')
            }))
        return jsonify({
            'result': 'success',
            'msg' : 'Successfuly fetched all posts',
            'posts' : posts
        })
        
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username' : payload.get('id')})
        post_id_receive = request.form.get('post_id_give')
        type_receive = request.form.get('type_give')
        action_receive = request.form.get('action_give')
        doc = {
            'post_id' : post_id_receive,
            'username' : user_info.get('username'),
            'type' : type_receive
        }
        if action_receive == 'like':
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        
        count = db.likes.count_documents({
            'post_id' : post_id_receive,
            'type' : type_receive,
            
            
        })
        return jsonify({
            'result': 'success',
            'msg' : 'updated!',
            'count' : count
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
         
@app.route('/delete_post', methods=['POST'])
def delete_post():
    username = request.form.get('username_give')
    postId = request.form.get('postId_give')
    print(postId)
    post = db.posts.find_one({'_id': ObjectId(postId)})

    
    db.posts.delete_one({'username' : username})
    db.likes.delete_many({'post_id': postId})
    db.comment.delete_many({'comment_id': postId})
    # db.examples.delete_many({'topik' : topik})
    return jsonify({
        'result' : 'success',
        'msg' : 'the topik was deleted'
    })

@app.route('/save_comment', methods=['POST'])
def save_comment():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
                token_receive,
                SECRET_KEY,
                algorithms=['HS256']
            )
        comment = request.form.get('comment')
        comment_id = request.form.get('post_id_give')
        username = request.args.get('username_give')
        date_receive = request.form.get('date_give')
        profilePhoto_receive = request.form.get('profilePhoto_give')
        user_info = db.users.find_one({'username' : payload.get('id')})
        doc = {
            'comment_id' : comment_id,
            'username' : user_info.get('username'),
            'comment' : comment,
            'date' : date_receive,
            'profile_pic_real' : profilePhoto_receive
        }
        db.comment.insert_one(doc)
        return jsonify({
            'result' : 'success',
            'msg' : f'Komentar kamu berhasil di simpan!',
            'new_comment': {
            'username': user_info.get('username'),
            'comment': comment,
            }
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    

@app.route('/get_comments', methods=['GET'])
def get_comments():
    postId = request.args.get('postId')
    comment_data = db.comment.find({'comment_id': postId})
    comments = []
    for comment in comment_data:
        comments.append({
            'username': comment.get('username'),
            'comment': comment.get('comment'),
            'date' : comment.get('date'),
            'profile_pic_real' : comment.get('profile_pic_real')
        })
    return jsonify({
        'result': 'success',
        'comments': comments
    })


if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run('0.0.0.0',port=5000,debug=True)