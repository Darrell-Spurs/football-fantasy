from app import create_app
from flask import Flask, render_template
from celery import Celery
import requests, json, os
import firebase_admin
from firebase_admin import credentials, firestore


web_app = create_app("testing")

cred = credentials.Certificate(web_app.config["FCBOGNDFKIYG"])
firebase_admin.initialize_app(cred)
db = firestore.client()
web_app.config["DB"] = db

if __name__ =="__main__":
    web_app.run(host=web_app.config["HOST"],port=web_app.config["PORT"])