from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        "SELECT * from articles"
    ).fetchall()
    db.commit()
    return render_template('blog/index.html', posts=posts)



@bp.route('/views')
def views():
    db = get_db()
    posts = db.execute(
        "SELECT * from articles"
    ).fetchall()
    db.commit()
    return render_template('blog/index.html', posts=posts)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/load', methods=('GET', 'POST'))
@login_required
def load():
    if request.method == 'POST' or request.method=="GET":
        db = get_db()
        db.execute("DELETE FROM ARTICLES")
        db.commit()
        print("DELETING")
        articles = get_links_and_title()
        print(articles)
        for (title,link_content) in articles.items():
            content = link_content['contents']
            link = link_content['link']
            db.execute(
            'INSERT INTO articles (title, contents,link)'
            ' VALUES (?, ?,?)',
            (title, content,link))
        print("HELLO")
        db.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/load.html')



def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))



url = 'https://www.theverge.com/film'

result = {}
def get_content(title,link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    # contents = soup.find_all("div", {"class": "c-entry-content"})
    for a in soup.find_all("div", {"class": "c-entry-content"}):
        return a.text

def get_links_and_title():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print("HERE")
    links = soup.findAll('a')
    mydivs = soup.find_all("h2", {"class": "c-entry-box--compact__title"})
    for div in mydivs[1:9]:
        # print(div.findAll("a")[1])
        link = (div.find("a")['href'])
        title = (div.find("a").text)
        content = get_content(title,link)
        link_contents = {}
        link_contents["link"] = link
        link_contents["contents"] = content
        result[title]=link_contents
    return result    
        

