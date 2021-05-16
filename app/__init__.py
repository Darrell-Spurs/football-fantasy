from flask import Flask, Blueprint
from flask import redirect, url_for, request, render_template
from .config.config import configuration
from stats.stats import stats_app
import time, json, sys, os, random
from os.path import abspath, dirname



def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(configuration[config_name])
    app.register_blueprint(stats_app)

    app.template_folder = app.config["TEMPLATE_FOLDER"]
    app.static_folder = app.config["STATIC_FOLDER"]

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(500)
    def interal_server_error(e):
        return render_template("error/500.html"), 500

    @app.route("/")
    def home_page():
        return render_template("home.html")

    @app.route("/activate")
    def activate_fc():
        from celtest import playerstats_fetch
        playerstats_sig = playerstats_fetch.s()
        bg_task = playerstats_sig.apply_async(serializer='json')
        return redirect(f"/check/{bg_task.id}")

    @app.route("/check/<tid>")
    def get_bg_res(tid):
        from celtest import celery
        state = celery.AsyncResult(id=tid).status
        if state =="PENDING":
            return "Fetch in Process"
        elif state == "SUCCESS":
            return {i:j for i,j in enumerate(celery.AsyncResult(id=tid).get())}
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
