from app import create_app
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from celery import Celery
import requests, json, os
import firebase_admin
from firebase_admin import credentials, firestore

web_app = create_app("testing")
# development
# testing


if __name__ == '__main__':
    # cred = credentials.Certificate(web_app.config['FCBOGNDFKIYG'])
    # firebase_admin.initialize_app(cred)
    # db = firestore.client()
    # web_app.config["DB"] = db
    port = int(os.environ.get("PORT",5555))
    web_app.run(debug=False, port=port, host=web_app.config["HOST"])

