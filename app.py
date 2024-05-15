from flask import Flask, render_template, url_for, redirect, request, jsonify 
from flask_sqlalchemy import * 
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import json
import hashlib
import os
import random
import secrets


images = []
for root, directories, files in os.walk("static/img/post"):
    for filename in files:
        images.append(filename)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    picture_path2 = picture_path.split("static/")[1]
    #output_size = (1280, 720)
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i.save(picture_path)

    return picture_path2

def giveme():
    random.shuffle(images)
    try:
        return random.choice(images)
    except:
        return False

with open("templates/config.json", "r") as c:
    para = json.load(c)["para"]

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['SECRET_KEY'] = 'blue123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)


class Posts(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(600), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    author = db.Column(db.String(200), default=para['user'])
    image = db.Column(db.String(30), default=giveme())

    def __repr__(self):
        return '<post %r>' % self.id

class Projecto(db.Model):
    __tablename__='projecto'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.String(80), nullable=False)
    materiales = db.relationship("Material", back_populates="projecto")

    def __repr__(self):
        return '<Projecto %r>' % self.id

class Material(db.Model):
    __tablename__='material'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    id_projecto = db.Column(db.Integer, db.ForeignKey('projecto.id'))
    ub = db.Column(db.String(20), nullable=False)
    projecto = db.relationship("Projecto",back_populates="materiales")

    def __repr__(self):
        return '<Material %r>' % self.id




def check(s):
    z = s.encode('ascii')
    return hashlib.sha256(z).hexdigest() == str(para['key'])


def isalready(s):
    return s in images


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/error')

@app.route('/')
def blu():
    return render_template('blue.html')

@app.route('/about2')
def about2():
    return render_template('about2.html')

@app.route('/tarot')
def tarot():
    imagenes = Material.query.filter_by(id_projecto=2).all()
    return render_template('tarot.html', imagenes=imagenes)

@app.route('/murales')
def murales():
    imagenes = Material.query.filter_by(id_projecto=5).all()
    leng = len(imagenes)
    return render_template('murales.html', imagenes=imagenes, Len=leng, corte=1)

@app.route('/ceramica')
def ceramica():
    imagenes = Material.query.filter_by(id_projecto=4).all()
    leng = len(imagenes)
    return render_template('ceramica.html', imagenes=imagenes, Len=leng, corte=4)

@app.route('/diablxs')
def cuyo():
    imagenes = Material.query.filter_by(id_projecto=1).all()
    return render_template('diablxs.html', imagenes=imagenes)

@app.route('/error')
def error():
    return render_template('404.html')

@app.route('/priv')
def priv():
    return render_template('priv.html')

@app.route('/animaciones')
def animaciones():
    return render_template('animaciones.html')

"""@app.route('/admin')
def index():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    tp = para['nofpost']
    last = len(posts) // tp + (len(posts) % tp != 0)
    if last == 1:
        return render_template('index.html', posts=posts, prev="#", next="#")

    page = request.args.get('page')
    try:
        page = int(page)
    except(Exception):
        page = 0

    posts = posts[page * tp:min((page + 1) * tp, len(posts))]

    prev = "?page=" + str(page - 1) if page > 0 else "#"
    next = "?page=" + str(page + 1) if page < last - 1 else "#"

    return render_template('index.html', posts=posts, prev=prev, next=next)

@app.route('/calaveras')
def calaveras():
    return render_template('calaveras.html')

@app.route('/edit')
def edit():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    return render_template('edit.html', posts=posts)


@app.route('/editor')
def editor():
    games = Games.query.all()
    return render_template('editor.html', games=games)


@app.route('/deletegame/<string:id>', methods=['GET', 'POST'])
def deletegame(id):
    try:
        game = Games.query.get_or_404(id)
    except(Exception):
        return redirect('/error')

    if request.method == 'POST':
        password = request.form['password']
        if check(password):
            try:
                try:
                    os.remove(os.path.join(
                        'static/img/games/', game.nick + '.png'))
                    os.remove(os.path.join(
                        'static/js/games/', game.nick + '.js'))
                except(Exception):
                    return redirect('/error')

                db.session.delete(game)
                db.session.commit()
                return redirect('/editor')

            except(Exception):
                return redirect('/error')
        else:
            return render_template('/deletegame.html', game=game, res=1)
    else:
        return render_template('deletegame.html', game=game, res=0)


@app.route('/editor/<string:id>', methods=['GET', 'POST'])
def editgame(id):
    try:
        game = Games.query.get_or_404(id)
    except(Exception):
        return redirect('/error')

    if request.method == 'POST':
        password = request.form['password']
        if check(password):
            try:
                os.remove(os.path.join(
                    'static/img/games/', game.nick + '.png'))
                os.remove(os.path.join('/static/js/games/', game.nick + '.js'))
            except(Exception):
                return redirect('/error')

            game.name = request.form['name']
            game.nick = request.form['nick']
            game.dis = request.form['discrip']

            image = request.files['imagefile']
            jsfile = request.files['jsfile']

            image.save(os.path.join('static/img/games/',
                                    secure_filename(image.filename)))
            jsfile.save(os.path.join('static/js/games/',
                                     secure_filename(jsfile.filename)))

            try:
                db.session.commit()
                return redirect('/play')
            except(Exception):
                return redirect('/error')
        else:
            return render_template('editgame.html', game=game, res=1)
    else:
        return render_template('editgame.html', game=game, res=0)


@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def editblog(id):
    try:
        post = Posts.query.get_or_404(id)
    except(Exception):
        return redirect('/error')

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content'].lstrip(' ')
        password = request.form['password']
        if check(password):
            try:
                db.session.commit()
                return redirect('/')
            except(Exception):
                return redirect('/error')
        else:
            return render_template('/editblog.html', post=post, res=1)
    else:
        return render_template('editblog.html', post=post, res=0)


@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
    try:
        post = Posts.query.get_or_404(id)
    except(Exception):
        return redirect('/error')

    if request.method == 'POST':
        password = request.form['password']
        if check(password):
            try:
                db.session.delete(post)
                db.session.commit()
                return redirect('/edit')
            except(Exception):
                return redirect('/error')
        else:
            return render_template('/delete.html', post=post, res=1)
    else:
        return render_template('delete.html', post=post, res=0)
@app.route('/about')
def about():
    return render_template('about.html')

"""
@app.route('/add', methods=['GET', 'POST'])
def addvideo():
    projectos = Projecto.query.order_by(Projecto.id.desc()).all()
    if request.method == 'POST':
        id_projecto = request.form['id_projecto']
        print(id_projecto)
        password = request.form['password']
        image =request.files['imagefile']
        pathimage = save_picture(image) 
        if check(password):
            newmaterial = Material(
            id_projecto=id_projecto , ub=pathimage)
            try:
                db.session.add(newmaterial)
                db.session.commit()
                projectos = Projecto.query.order_by(Projecto.id.desc()).all()
                return render_template('/addmaterial.html', res =0,projectos=projectos)
            except(Exception):
                print("ERROR")
                return render_template('/addmaterial.html',res = 0, projectos=projectos)
        else:
            return render_template('addmaterial.html',res = 1  ,projectos=projectos)
    else:
        return render_template('addmaterial.html',res = 0, projectos=projectos)
"""
@app.route('/basep')
def basep():
    imagenes = Material.query.filter_by(id_projecto=2).all()
    return render_template('basep.html', imagenes=imagenes)

@app.route('/projecto')
def projectos():
    projectos = Projecto.query.order_by(Projecto.id.desc()).all()
    imagenes = Material.query.order_by(Material.id.desc()).all()
    coso = dict() 
    for p in projectos:
        imagenes = Material.query.filter_by(id_projecto=p.id).all()
        try:
            coso[p] = imagenes[0].ub
        except:
            coso[p] = ""
    return render_template('projecto.html', projectos=coso)


@app.route('/editvideo')
def editvideo():
    videos = Videos.query.order_by(Videos.id.desc()).all()
    return render_template('editvideo.html', videos=videos)


@app.route('/deletevideo/<string:id>', methods=['GET', 'POST'])
def deletevideo(id):
    try:
        video = Videos.query.get_or_404(id)
    except(Exception):
        return redirect('/error')

    if request.method == 'POST':
        password = request.form['password']
        if check(password):
            try:
                db.session.delete(video)
                db.session.commit()
                return redirect('/editvideo')
            except(Exception):
                return redirect('/error')
        else:
            return render_template('/deletevideo.html', video=video, res=1)
    else:
        return render_template('deletevideo.html', video=video, res=0)


@app.route('/play')
def menu():
    games = Games.query.all()
    return render_template('play.html', games=games)
"""

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        password = request.form['password']
        title = request.form['name']
        desc = request.form['discrip']

        if check(password):
            try:
                new_project = Projecto(title=title,desc=desc)
                db.session.add(new_project)
                db.session.commit()
                return redirect('/projecto')
            except Exception:
                print("error")
                return redirect('/error')
        else:
            return render_template('upload.html', res=1)
    else:
        return render_template('upload.html', res=0)

"""
@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        password = request.form['password']
        random_check = request.form.get('random')
        if check(password):
            content = content.lstrip(' ')
            if not random_check:
                try:
                    image = request.files['postimage']
                    if isalready(image.filename):
                        return render_template('/postblog.html', res=0, res2=1)

                    image.save(os.path.join('static/img/post/',
                                            secure_filename(image.filename)))
                except(Exception):
                    return redirect('/error')

                newpost = Posts(title=title, content=content,
                                image=image.filename)
            else:
                newpost = Posts(title=title, content=content)

            try:
                db.session.add(newpost)
                db.session.commit()
                return redirect('/')
            except(Exception):
                return redirect('/error')
        else:
            return render_template('/postblog.html', res=1, res2=0)
    else:
        return render_template('/postblog.html', res=0, res2=0)


@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/projectoview/<int:id>')
def play(id):
    #try:
    imagenes = Material.query.filter_by(id_projecto=id).all()
    print(imagenes)
    #except(Exception):
    #    return redirect('/error')

    return render_template('projectoview.html', imagenes=imagenes)


@app.route('/play/full/<int:id>')
def playfull(id):
    try:
        game = Games.query.get_or_404(id)
    except(Exception):
        return redirect('/404.html')

    return render_template('games/fullsc.html', game=game)


@app.route("/js/<string:file>")
def index_js(file):
    with open("static/js/" + file, "r") as f:
        data = f.read()

    return data
"""
if __name__ == '__main__':
    #db.drop_all()
    #db.create_all()
    app.run(debug=True)
