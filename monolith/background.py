from celery import Celery
import requests
from stravalib import Client
from monolith.database import db, User, Run


BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)


@celery.task
def background_task(url):
    return requests.head(url).headers['Last-Modified']


def get_runs(user):
    if user.strava_token is None:
        raise ValueError("No Token")

    client = Client(access_token=user.strava_token)

    for activity in client.get_activities(limit=10):
        if activity.type != 'Run':
            continue

        q = db.session.query(Run).filter(Run.strava_id == activity.id)
        run = q.first()

        if run is None:
            _run = Run()
            _run.runner = user
            _run.strava_id = activity.id
            _run.name = activity.name
            _run.distance = activity.distance
            _run.elapsed_time = activity.elapsed_time.total_seconds()
            _run.average_speed = activity.average_speed
            _run.average_heartrate = activity.average_heartrate
            _run.total_elevation_gain = activity.total_elevation_gain
            _run.start_date = activity.start_date

            db.session.add(_run)

    db.session.commit()
    print('DONE')


if __name__ == '__main__':
    from monolith.app import app
    db.init_app(app)
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'tarek@ziade.org')
        user = q.one()
        print(get_runs(user))
