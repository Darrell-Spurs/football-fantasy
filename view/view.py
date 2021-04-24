from flask import Flask, Blueprint
from flask import render_template, abort

view = Blueprint('view', __name__, template_folder="templates/view")


@view.route('/')
def home():
    return render_template("view.html")


@view.route('/intro')
def intro():
    return render_template("view.html")
