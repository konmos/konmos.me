import os
import time
from datetime import datetime

from flask import Flask, render_template, abort, request, jsonify, Response, session
from flask_cors import CORS
from htmlmin.main import minify

import config
import database

app = Flask(__name__)
app.config.from_object(config)

CORS(app)  # enable CORS because I have no reason not to


def format_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%b %d, %Y').replace(' 0', ' ')


app.jinja_env.filters['str'] = str
app.jinja_env.filters['datetimeformat'] = format_timestamp
app.jinja_env.globals['year_exists'] = database.Posts.check_year_exists


@app.after_request
def response_minify(response):
    '''Minify the HTML response before returning it.'''
    if response.content_type in ['text/html', 'text/html; charset=utf-8']:
        response.set_data(
            minify(response.get_data(as_text=True))
        )

    return response


@app.before_request
def assign_session_id():
    if session.get('session_id') is None:
        session['session_id'] = os.urandom(16).hex()


# analytics
# based on http://charlesleifer.com/blog/saturday-morning-hacks-building-an-analytics-app-with-flask/
@app.route('/a.gif', methods=['GET'])
def analytics_gif():
    if not request.args.get('u'):
        abort(404)

    database.PageViews.add_from_request()

    response = Response(config.ANALYTICS_GIF, mimetype='image/gif')
    response.headers['Cache-Control'] = 'private, no-cache'
    return response


@app.route('/')
def index():
    return render_template('home.html', location='home')


@app.route('/rss.xml')
def rss_feed():
    current_year = time.localtime().tm_year

    return Response(
        render_template('rss.xml', year=current_year, posts=database.Posts.peek(current_year)),
        mimetype='text/xml'
    )


@app.route('/posts')
def posts():
    current_year = time.localtime().tm_year

    return render_template(
        'posts.html', location='posts', year=current_year, posts=database.Posts.peek(current_year)
    )


@app.route('/posts/<int:year>')
def posts_for_year(year):
    return render_template('posts.html', location='posts', year=year, posts=database.Posts.peek(year))


@app.route('/posts/<int:year>/<post_id>')
def get_post(year, post_id):
    post = database.Posts.get_post(year, post_id)

    if post is None:
        abort(404)

    return render_template('post.html', post=post, location='posts')


@app.route('/api/email', methods=['GET'])
def email():
    return config.EMAIL


@app.route('/api/heart-post', methods=['POST'])
def heart_post():
    database.Posts.heart_post(request.json['post_id'][:24])
    return jsonify(status='ok')


@app.route('/api/unheart-post', methods=['POST'])
def unheart_post():
    database.Posts.unheart_post(request.json['post_id'][:24])
    return jsonify(status='ok')


if __name__ == '__main__':
    app.run()
