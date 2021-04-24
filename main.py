from app import create_app
from flask import Flask, render_template
from celery import Celery
import requests, json, os


web_app = create_app("development")

if __name__ =="__main__":
    web_app.run()