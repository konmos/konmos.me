import time
from typing import Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.results import UpdateResult
from bson.objectid import ObjectId
from flask import request, session
from urllib.parse import parse_qsl, urlparse
from dateutil import parser

import config
from utils import calc_reading_time

CLIENT = MongoClient(
    config.DATABASE_HOST,
    config.DATABASE_PORT,
    username=config.DATABASE_USER,
    password=config.DATABASE_PASS,
    connect=False
)


class Posts:
    collection: Collection = CLIENT.website.posts

    @staticmethod
    def create_post(title: str, desc: str, content: str, tags: list) -> str:
        r = calc_reading_time(content)

        result = Posts.collection.insert_one({
            'title': title,
            'description': desc,
            'content': content,
            'tags': ['#' + t for t in tags],
            'time_created': time.time(),
            'year_created': time.localtime().tm_year,
            'reading_time_raw': r,
            'reading_time': ('~1 minute', f'~{int(r)} minutes')[r >= 2],
            'hearts': 0
        })

        return str(result.inserted_id)

    @staticmethod
    def peek(year: Union[str, int]) -> Cursor:
        return Posts.collection.find({'year_created': int(year)}, {'content': 0}).sort('time_created')

    @staticmethod
    def check_year_exists(year: Union[str, int]) -> bool:
        return Posts.collection.find({'year_created': int(year)}, {'_id': 1}).limit(1).count(True) > 0

    @staticmethod
    def get_post(year: Union[str, int], post_id: str) -> dict:
        return Posts.collection.find_one({'year_created': int(year), '_id': ObjectId(post_id)})

    @staticmethod
    def heart_post(post_id: str) -> UpdateResult:
        return Posts.collection.update_one({'_id': ObjectId(post_id)}, {'$inc': {'hearts': 1}})

    @staticmethod
    def unheart_post(post_id: str) -> UpdateResult:
        return Posts.collection.update_one({'_id': ObjectId(post_id)}, {'$inc': {'hearts': -1}})


class PageViews:
    collection: Collection = CLIENT.website.page_views

    @staticmethod
    def add_from_request() -> str:
        parsed = urlparse(request.args['u'])
        params = dict(parse_qsl(parsed.query))

        # note that we have to strip all whitespaces
        # for some reason, certain requests contain a lot of trailing whitespace
        result = PageViews.collection.insert_one({
            'domain': parsed.netloc,
            'url': parsed.path,
            'title': request.args.get('t') or '',
            'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
            'referrer': request.args.get('ref') or '',
            'headers': dict(request.headers),
            'params': params,
            'timestamp': time.time(),
            'local_time': parser.parse(request.args.get('d')[:24]),
            'session_id': session['session_id']
        })

        return str(result.inserted_id)
