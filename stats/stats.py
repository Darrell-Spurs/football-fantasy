from flask import Blueprint
from flask import render_template
import os, json


stats_app = Blueprint("stats_app",__name__,
                      url_prefix="/stats",
                      template_folder=os.getcwd()+r"\static\stats\templates"
                      )

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(os.getcwd() + "\static\golden_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@stats_app.route("/")
def stats_default():
    doc = db.collection(u'roster').document(u'Paulo_Dybala').get()

    player = {
        "nation": u"Argentina",
        "position": u"CF",
        "team": u"Juventus FC"
    }

    update = {
        u"position": u"RW"
    }
    # db.collection(u'roster').document(u'Paulo_Dybala').set(player)
    db.collection(u'roster').document(u'Paulo_Dybala').update(update)

    return doc.to_dict()



@stats_app.route("/roster")
def show_roster():
    return render_template("roster.html")
