# Flask modules
from flask import Flask, Blueprint
from flask import redirect, url_for, request, render_template, jsonify

# app config
from .config.config import configuration

# built-ins
import time, json, sys, os, random,datetime, ast
from os.path import abspath, dirname

# celery (for creating task scheduler and run background task)
from celery import Celery

# form classes
from modules import LoginForm, SignupForm, CreateLeagueForm, Toolbox

# firebase
import firebase_admin
from firebase_admin import credentials, firestore, auth

celery = Celery(__name__)
celery.config_from_object('tasks.celconfig')


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(configuration[config_name])

    from stats.stats import stats_app
    app.register_blueprint(stats_app)

    app.template_folder = app.config["TEMPLATE_FOLDER"]
    app.static_folder = app.config["STATIC_FOLDER"]

    cred = credentials.Certificate(app.config['FCBOGNDFKIYG'])
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error/404.html"), 404

    @app.errorhandler(500)
    def interal_server_error(e):
        return render_template("error/500.html"), 500

    @app.context_processor
    def check_status():
        auth_user = {
            'login': False,
            'profile': dict(),
            'info':dict()
        }
        session_cookie = request.cookies.get("uauuccu_oreo")
        try:
            profile = auth.verify_session_cookie(session_cookie,True)
            auth_user['login'] = True
            auth_user['profile'] = profile
            print(profile)
            info = db.collection("users").document(auth_user['profile']['email']).get().to_dict()
            auth_user['info'] = info
            auth_user["info"]["processed_email"] = Toolbox().email_alphabetify(auth_user['profile']['email'])
            print("Auth Successful")
        except Exception as e:
            print(e)
            print("Auth Failed")
        return dict(auth_user=auth_user)

    @app.route("/")
    def home_page():
        return render_template("home.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        form = LoginForm()
        if request.method == "POST":
            data = request.json
            id_token = data["id_token"]
            db_data = data["db_data"]
            expires_in = datetime.timedelta(days=14)
            session_cookie = auth.create_session_cookie(id_token,expires_in)
            response = jsonify({"message":"Login cookie!"})
            expires = datetime.datetime.now() + expires_in
            response.set_cookie("uauuccu_oreo",session_cookie,expires=expires,httponly=True)
            if db_data!="Login":
                db.collection("users").document(db_data["email"]).set(db_data)
            # secure = True
            return response
        return render_template("login.html",form=form)

    @app.route("/signup")
    def signup():
        form = SignupForm()
        return render_template("signup.html",form=form)

    @app.route("/logout")
    def logout():
        oreo = request.cookies.get("uauuccu_oreo")
        try:
            profile = auth.verify_session_cookie(oreo)
            auth.revoke_refresh_tokens(profile["user_id"])
            print("[Logged out]")
        except Exception as e:
            print(e)
            print("[Failed to log out]")
        return redirect("/")

    @app.route("/profile")
    def profile():
        return render_template("profile.html")

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

    # LEAGUES
    # Route for creating new league
    @app.route("/leagues", methods=["GET","POST"])
    def league():
        email = check_status()["auth_user"]["profile"]["email"]
        user = db.collection("users").document(email).get().to_dict()
        if request.method == "POST":
            league_name = ast.literal_eval(request.data.decode("utf-8"))["ln"]
            email_id = check_status()["auth_user"]["info"]["processed_email"]
            # add member to league doc
            username = user["username"]
            print(league_name, email_id, username)
            # add email to member list; set player data in league
            db.collection("leagues").document(league_name).update({"members":firestore.ArrayUnion([email])})
            db.collection("leagues").document(league_name).update({email_id:{"email":email, "name":f"{username}'s Team"}})

            # add league/ current league to user doc
            db.collection("users").document(email).update({"leagues":firestore.ArrayUnion([league_name]),
                                                           "current_league":league_name})
        my_league = {"info": {},"user":{}}
        user = db.collection("users").document(email).get().to_dict()
        try:
            for league in user["leagues"]:
                this_league = db.collection("leagues").document(league).get().to_dict()
                my_league["info"][league] = this_league["INFO"]
                my_league["user"][league] = this_league[Toolbox().email_alphabetify(email)]
        except:
            pass
        return render_template("leagues.html",user = user, my_league = my_league)

    @app.route("/create_league",methods=["GET","POST"])
    def create_league():
        auth_login = check_status()["auth_user"]["login"]
        if not auth_login:
            return redirect("/login")

        form = CreateLeagueForm()

        if form.validate_on_submit():
            to_db = form.data
            print(form.data)
            email = check_status()["auth_user"]["profile"]["email"]
            league_name = form.data["league_name"]
            # add league data to db
            to_db["draft_time"]=f'{to_db["date"].__str__()}-{to_db["time"].__str__()}'
            for e in ["csrf_token","submit","date","time","add_rostering","add_scoring"]:
                to_db.pop(e)
            db.collection("leagues").document(league_name).set({"INFO":to_db,"owned":[],"matchup":{},"standings":{}})
            # add member to league doc
            username = db.collection("users").document(email).get().to_dict()["username"]
            email_id = Toolbox().email_alphabetify(email)

            # add email to member list; set player data in league
            db.collection("leagues").document(league_name).update({"members":firestore.ArrayUnion([email])})
            db.collection("leagues").document(league_name).update({email_id:{"email":email, "name":f"{username}'s Team"}})

            # add league/ current league to user doc
            db.collection("users").document(email).update({"leagues":firestore.ArrayUnion([league_name]),
                                                           "current_league":league_name})
            return redirect("/")

        return render_template("create_league.html",form = form)

    @app.route("/news")
    def news():
        tb = Toolbox()
        # date change
        today = tb.today_y_m_d()
        inj = db.collection("Injuries").document(today).get().to_dict()
        print(inj)
        return render_template("news.html",inj = inj, today = today)

    @app.route("/bingo")
    def bingo():
        return render_template("bingo.html")

    # REQUIRED FILES
    @app.route('/static/favicon.ico', methods=['GET'])
    def favicon():
        return app.send_static_file('favicon.ico')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js'), 200, {"Content-Type":"text/javascript"}

    @app.route('/offline', methods=['GET'])
    def offline():
        return render_template("offline.html")

    from modules import ApiFetch
    api = ApiFetch()
    # api.recalculate_recent_stats()
    # api.fetch_all_player_to_db_2()
    # api.get_today_fixtures()
    # api.get_fixture_lineups_to_db()
    # api.find_all_teams()
    # api.get_injuries()
    # api.update_latest_stats()
    # api.get_today_fixtures_to_db()
    # api.add_all_team_squads()
    # api.get_fixture_lineups_to_db()
    # api.get_fixture_stats_to_db()
    return app

