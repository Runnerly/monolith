import functools
from celery import Celery
import requests


BACKEND = BROKER = 'redis://localhost:6379'

celery = Celery(__name__, backend=BACKEND, broker=BROKER)


@celery.task
def background_task(url):
    return requests.head(url).headers['Last-Modified']
