Monolithic Version
==================

**DISCLAIMER** This repository is part of Runnerly, an application made for
the Python Microservices Development. It was made for educational
purpose and not suitable for production. It's still being updated.
If you find any issue or want to talk with the author, feel free to
open an issue in the issue tracker.

The monolith app is a Flask app and a Celery worker.


How to run the Flask app
------------------------


For this application to work, you need to create a Strava API application
see https://strava.github.io/api/#access and https://www.strava.com/settings/api

Once you have an application, you will have a "Client Id" and "Client Secret".
You need to export them as environment variables::

    export STRAVA_CLIENT_ID=<ID>
    export STRAVA_CLIENT_SECRET=<SECRET>

Make sure you have virtualenv installed, then you can create a
development environment::

    $ virtualenv .
    $ bin/pip install -r requirements.txt
    $ bin/python setup.py develop

You can then run your application with::

    $ bin/python monolith/app.py
    * Running on http://127.0.0.1:5000/

Go to your browser at http://127.0.0.1:5000/ - you can log in with these
credentials:

- email: tarek@ziade.org
- password: ok

Once you are logged in, click on "Authorize Strava Access" -- this will
perform an OAuth trip to Strava.

Once authorized, you will be able to see your last 10 runs.
But for this, we need to ask the Celery worker to fetch them.


How to run the Celery worker
----------------------------

Make sure you have a redis servier running locally on port 6379 then,
open another shell and run::

    $ bin/celery worker -A monolith.background

This will run a celery microservice that can fetch runs.
To invoke it, visit http://127.0.0.1:5000/fetch.

Once the runs are retrieved, you should see your last ten runs
on http://127.0.0.1:5000


