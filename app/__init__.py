from flask import Flask, Blueprint
from flask import redirect, url_for, request, render_template, jsonify
from .config.config import configuration
import time, json, sys, os, random
from os.path import abspath, dirname
from celery import Celery
from modules import LoginForm, SignupForm

celery = Celery(__name__)
celery.config_from_object('tasks.celconfig')

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(configuration[config_name])

    from stats.stats import stats_app
    app.register_blueprint(stats_app)

    app.template_folder = app.config["TEMPLATE_FOLDER"]
    app.static_folder = app.config["STATIC_FOLDER"]

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(500)
    def interal_server_error(e):
        return render_template("error/500.html"), 500

    @app.context_processor
    def check_status():
        auth_user = {
            "login": False,
            "profile": {}
        }
        return dict(auth_user=auth_user)

    @app.route("/")
    def home_page():
        return render_template("home.html")

    @app.route("/login")
    def login():
        form = LoginForm()
        return render_template("login.html",form=form)

    @app.route("/signup")
    def signup():
        form = SignupForm()
        return render_template("signup.html",form=form)

    @app.route("/check/<tid>")
    def get_bg_res(tid):
        from celtest import celery
        state = celery.AsyncResult(id=tid).status
        if state =="PENDING":
            return "Fetch in Process"
        elif state == "SUCCESS":
            game_log = celery.AsyncResult(id=tid).get()
            return {player['Name']:player for player in game_log}

            # return str(game_log)
        elif state =="FAILED":
            return "Fetch Failed"

    @app.route('/static/favicon.ico', methods=['GET'])
    def favicon():
        return app.send_static_file('favicon.ico')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js'), 200, {"Content-Type":"text/javascript"}

    @app.route('/offline', methods=['GET'])
    def offline():
        return render_template("offline.html")


    return app

