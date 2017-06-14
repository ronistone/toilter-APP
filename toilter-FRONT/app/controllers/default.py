from flask import render_template, flash, url_for, redirect, g,abort,request, send_from_directory
from app import app, db, lm, mail, cache
from flask_login import login_user,logout_user, login_required, current_user
from flask_mail import Message
from app.models.forms import LoginForm, RegisterForm, TwitForm, SearchForm
from app.models.tables import User, Post
from app.models.decorators import is_user
import requests
import json

ip = "http://localhost:5000"

@lm.user_loader
def user_loader(id):
    header = {"Content-Type":"application/json; charset=utf-8"}
    req = requests.get(ip+"/api/v1/users/"+str(id[0]), headers=header, auth=(id[1],''))
    if req.status_code == 200:
        user = User(**(json.loads(req.text)['data']))
        user.token = id[1]
        print(json.loads(req.text))
        return user
    return None

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        payload = { 'name':form.name.data,
                    'email':form.email.data,
                    'password': form.password.data}
        header = {"Content-Type":"application/json; charset=utf-8"}
        req = requests.post(ip+"/api/v1/users", headers=header, data=json.dumps(payload))
        if req.status_code == 200:
            flash("Registered !!")
            return redirect(url_for('login'))
        else:
            flash("Ocorreu um erro!")
            return redirect(url_for('register'))
    return render_template('register.html', form=form)


@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        payload = { 'name':form.username.data,
                    'password': form.password.data}
        header = {"Content-Type":"application/json; charset=utf-8"}
        req = requests.get(ip+"/api/v1/tokens", headers=header, auth=(form.username.data,form.password.data))
        if req.status_code == 200:
            user = User(**(json.loads(req.text)['user']))
            user.token = json.loads(req.text)['token']
            login_user(user,remember=form.remember_me.data)
            return redirect(url_for('dashboard'))
        else:
            flash("Login Inválido")

    elif form.errors:
        print(form.errors)
    return render_template('login.html',form=form)

@app.route("/logout",endpoint='logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route('/search',endpoint='search',methods=["POST","GET"])
@login_required
def search(users=None):
    search = SearchForm()
    users = request.args.get('users')
    entrou = None
    if users:
        entrou = True
        req = requests.get(ip+"/api/v1/users?name="+users, auth=(current_user.token,''))
        if req.status_code == 200:
            users = json.loads(req.text)['data']
    return render_template('search.html', form1=search,search=users,entrou=entrou)

@app.route("/dashboard", methods=["GET","POST"],endpoint='dashboard')
@login_required
def dashboard():
    form = TwitForm()
    search = SearchForm()
    if form.submit.data and form.validate_on_submit():
        new_twit = {'content':form.content.data,'user_id':current_user.id}
        header = {"Content-Type":"application/json; charset=utf-8"}
        req = requests.post(ip+"/api/v1/post", headers=header, data=json.dumps(new_twit), auth=(current_user.token,''))
        if req.status_code == 200:
            flash("Post feito com sucesso!")
            return redirect(url_for('dashboard'))
    header = {"Content-Type":"application/json; charset=utf-8"}
    req = requests.get(ip+"/api/v1/dashboard?update=true&num=100", headers=header, auth=(current_user.token,''))
    twits = []
    if req.status_code == 200:
        t = json.loads(req.text)
        t = t['data']
        for u in t:
            twits += [Post(u['content'],u['user']['name'],u['time'],u['user']['id'])]
    return render_template('dashboard.html',twits=twits[::-1], form=form, form1=search)

@app.route("/twitero/<int:id>",endpoint='twitero')
@login_required
def profile(id):
    search = SearchForm()
    if search.submit.data and search.validate_on_submit():
        req = requests.get(ip+"/api/v1/users?"+search.search.data, auth=(current_user.token,''))
        if req.status_code == 200:
            return redirect(url_for('search',users=json.loads(req.text)))

    req = requests.get(ip+"/api/v1/users/"+str(id), auth=(current_user.token,''))
    user = None
    following = None
    twits = []
    if req.status_code == 200:
        js = json.loads(req.text)['data']
        user = User(**js)
        req = requests.get(ip+"/api/v1/post/"+str(id), auth=(current_user.token,''))
        t = json.loads(req.text)['data']
        req = requests.get(ip+"/api/v1/follow/"+str(id)+"?follower="+str(current_user.id), auth=(current_user.token,''))
        if req.status_code == 200:
            following = json.loads(req.text)['data']
        for u in t:
            twits += [Post(u['content'],u['user']['name'],u['time'],u['user']['id'])]
    else:
        abort(404)

    return render_template('profile.html',user=user,twits=twits,following=following,form1=search)
@app.route("/down/",endpoint='down')
def download():
    return send_from_directory(app.config.get('MEDIA_ROOT'),'001.png')

@app.route("/follow/<id>",endpoint='follow')
@login_required
def follow(id):
    req = requests.post(ip+"/api/v1/follow/"+str(id),auth=(current_user.token,''))
    if req.status_code == 200:
        flash("Seguindo...")
    else:
        flash("Aconteceu um problema...")
    return redirect('/twitero/'+str(id))
    #msg = Message("New Follower!!", sender=app.config["MAIL_USERNAME"],recipients=[u.email])
    #msg.body = "You have new follower: @{0}".format(current_user.username)
    #mail.send(msg)


@app.route("/unfollow/<int:id>",endpoint='unfollow')
@login_required
def unfollow(id):
    req = requests.delete(ip+"/api/v1/follow/"+str(id), auth=(current_user.token,''))
    if req.status_code == 200:
        flash("Deixar de Seguir...")
    else:
        flash("Aconteceu um problema...")
    return redirect('/twitero/'+str(id))
