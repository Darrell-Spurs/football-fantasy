from flask import Flask, Blueprint
from flask import redirect, url_for, request, render_template
from .config.config import configuration
from stats.stats import stats_app
import time, json, sys, os
from os.path import abspath, dirname



def create_app(config_name):
    app = Flask(__name__,
                template_folder=os.path.abspath(os.getcwd())+r"/static/templates",
                static_folder=os.path.abspath(os.getcwd())+r"/static")
    print(os.path.abspath(__file__+"/../../")+r"/static/templates")
    print(os.path.abspath(os.getcwd())+r"/static/templates")

    app.config.from_object(configuration[config_name])
    app.register_blueprint(stats_app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(500)
    def interal_server_error(e):
        return render_template("error/500.html"), 500

    @app.route("/")
    def home_page():
        return render_template("home.html")

    @app.route("/startcel")
    def startcel():
        from celtest import fetch_api
        sig = fetch_api.s("https://fly.sportsdata.io/v3/soccer/stats/json/BoxScores/2021-03-18?key=de299c30471d4f1ca5619cb2771bb408")
        task = sig.apply_async()
        return redirect(f"/getcel/{task.id}")

    @app.route("/getcel/<tid>")
    def getcel(tid):
        from celtest import celery
        return celery.AsyncResult(id=tid).get(timeout=2)[0]

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js'), 200, {"Content-Type":"text/javascript"}

    @app.route('/offline', methods=['GET'])
    def offline():
        return render_template("offline.html")

    return app

