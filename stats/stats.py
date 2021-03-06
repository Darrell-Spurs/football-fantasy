from flask import Blueprint
from flask import render_template, current_app, url_for
import os, json

stats_app = Blueprint("stats_app",__name__,
                      url_prefix="/stats",
                      template_folder=os.getcwd()+r"/static/stats/templates"
                      )


@stats_app.route("/")
def stats_default():
    db = current_app.config["DB"]
    doc = db.collection(u'roster').document(u'Paulo_Dybala').get()

    player = {
        "nation": u"Argentina",
        "position": u"CF",
        "team": u"Juventus FC"
    }

    update = {
        u"position": u"RW"
    }
    db.collection(u'roster').document(u'Paulo_Dybala').set(player)

    return doc.to_dict()


@stats_app.route("/roster")
def show_roster():
    return render_template("roster.html")
    # return render_template("maintenance.html")

@stats_app.route("/transactions")
def transactions_list():
    return render_template("tran.html")
    # return "Transaction"