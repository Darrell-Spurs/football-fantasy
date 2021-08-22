from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, SelectMultipleField, BooleanField
from wtforms.fields.html5 import DateField, TimeField, IntegerField
from wtforms import widgets
from wtforms.validators import DataRequired, NumberRange, length
import csv, json, time
import firebase_admin
from firebase_admin import firestore
import requests


class Toolbox:
    def today_y_m_d(self):
        from time import gmtime as gm
        gm = gm()
        pre_z = lambda pre_z: str(pre_z).rjust(2, "0")
        return f"{gm.tm_year}-{pre_z(gm.tm_mon)}-{pre_z(gm.tm_mday)}"

    def yesterday(self):
        from time import localtime as lt
        pre_z = lambda a: str(a).rjust(2, "0")
        months=[31,28,31,30,31,30,31,31,30,31,30,31]
        y,m,d = lt().tm_year,lt().tm_mon,lt().tm_mday-1
        [m,d] = [m-1, months[m-2]+d] if d<1 else [m, d]
        [y,m,d] = [y-1,(m+11)%12+1,d] if m<1 else [y,m,d]
        return "-".join(map(pre_z,(y,m,d)))

    def parsing_stats(self,tds,note=False):
        date = self.yesterday()
        keys = ['Name', 'Team', 'Position', 'Minutes', 'Goals', 'Assists', 'Shots',
                'Shots on Target', 'Yellow Cards','Red Cards', 'Tackles', 'Steals',
                'Total Passes', 'Pass%', 'Saves', 'Fouls Committed', 'Fouls Suffered']
        value_indexes = [0,1,2,3,4,6,12,13,7,8,15,16,17,18,20,21,22]
        r_vlaue={'Update Time': date}
        if not note:
            for i in range(len(keys)):
                r_vlaue[keys[i]] = tds[value_indexes[i]].text
        else:
            for i in range(len(keys)):
                value_indexes[i]=value_indexes[i]+1 if i>2 else value_indexes[i]
                r_vlaue[keys[i]] = tds[value_indexes[i]].text
        return r_vlaue

    def process_game_time(self,date):
        game_day = date[:10]
        game_time = date[11:19]
        return game_time

    def email_alphabetify(self,string):
        string = string.replace(".","dot").replace("_","uscore").split("@")[0]
        return string


# customize MultiCheckboxField (from github)
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiInputField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.TextInput()

class LoginForm(FlaskForm):
    email = StringField("Email: ",validators=[DataRequired(message="Please enter you email"),length(max=16)])
    password = PasswordField("Password: ",validators=[DataRequired(message="Please enter you password"),length(max=16)])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    email = StringField("Email: ",validators=[DataRequired(message="Please enter you username"),length(max=16)])
    username = StringField("Username: ", validators=[DataRequired(message="Please enter you username"), length(max=16)])
    password = PasswordField("Password: ",validators=[DataRequired(message="Please enter you password"), length(max=16)])
    fav_nation = StringField("Favorite Nation: ", validators=[length(max=40)])
    fav_club = StringField("Favorite Club: ", validators=[length(max=40)])
    submit = SubmitField("Sign Up")


class CreateLeagueForm(FlaskForm):
    # Basic
    league_name = StringField("League Name: ",validators=[DataRequired(message="Enter League Name"), length(max=25)])
    score_choices = [("H2H", "Head to Head (Categories)"), ("Points", "Head to Head (Points)"), ("Roto", "Roto")]
    score_type = SelectField("Score Type: ",choices =score_choices)
    invite_choices = [("Com", "Commissioner Only"),("All", "All Members Can Invite")]
    invite = SelectField("Invite Permissions: ",choices =invite_choices)
    draft_choices = [("Standard","Live Standard Draft"), ("Salary", "Live Salary Cap Draft"), ("Offline","Offline Draft")]
    draft = SelectField("Darft Type: ",choices = draft_choices)
    members_choices = [(4, "4"),(6,"6"),(8,"8"),(10,"10"),(12,"12"),(14,"14"),(16,"16"),(20,"20")]
    members = SelectField("Maximum Members: ",choices =members_choices)
    date = DateField("Draft Date: ", validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField("Draft Time: ", validators=[DataRequired()], format='%H:%M')
    add_scoring = SubmitField("Next")

    # Categories
    roster_choices = \
        [('assists', 'Assists'),('blocks', 'Blocks'),
         ('conceded', 'Conceded'), ('dribbles', 'Dribbles'), ('dribbles_won', 'Dribbles won'),
         ('duels', 'Duels'), ('duels_won', 'Duels won'), ('fouls', 'Fouls'),
         ('fouls_drawn', 'Fouls Drawn'), ('goals', 'Goals'), ('interceptions', 'Interceptions'),
         ('key_passes', 'Key Passes'), ('minutes', 'Minutes'), ('offsides', 'Offsides'),
         ('passes', 'Passes'), ('rating', 'Rating'), ('red_cards', 'Red cards'),
         ('saves', 'Saves'), ('shot_on_goals', 'Shot On Goals'), ('shots', 'Shots'),
         ('tackles', 'Tackles'), ('yellow_cards', 'Yellow Cards')]
    rosters = MultiCheckboxField("Scoring Categories", choices = roster_choices, validators=[DataRequired()])
    add_rostering = SubmitField("Next")

    # Roster
    vali = [DataRequired()]
    pos_choices = [("2","Goalkeepers:"),("5","Defenders:"),("5","Midfielders:"),("5","Attackers:"),("3","Utility:"),("5","Bench:")]
    positions = MultiInputField("Roster Positions",choices=pos_choices, validators=vali)
    submit = SubmitField("Create League")


class ApiFetch:
    def __init__(self):
        # set class parameters
        # leagues/db/id_dict etc. are const params that can be used thruout the class
        # roster dict will be filled once a before the season
        # dict full_data is used to save fixture data after fetch (daily 0:00 operation)
        self.leagues = ["Premier League"]
                        # "La Liga"
                        # "Serie A",
                        # "Bundesliga",
                        # "Champions League"
        self.id_dict = self.get_league_id()
        firebase_admin.get_app()
        self.db = firestore.client()
        # self.today = Toolbox().today_y_m_d()
        self.today = Toolbox().today_y_m_d()
        self.season = "2021"
        self.full_data = {}

    def get_league_id(self):
        id_dict = dict()
        with open("api_code.csv") as file:
            content = csv.reader(file)
            for row in content:
                id_dict[row[0]]=row[1]
            file.close()
        return id_dict

    def fetch_all_player_to_db(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/players"
        for league in self.leagues:
            league_start = {"INTRO":{
                                "name": league,
                                "season": self.season,
                                "start_date": self.today}}
            self.db.collection("roster").document(f"{league} {self.season}").set(league_start)
            querystring = {"league": self.id_dict[league],
                           "season": self.season}
            headers = {
                'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
                'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            page_count = json.loads(response.text)["paging"]["total"]

            for i in range(1,page_count+1):
                querystring = {"league": self.id_dict[league],
                               "season": self.season,
                               "page": str(i)}
                headers = {
                    'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
                    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
                }
                response = requests.request("GET", url, headers=headers, params=querystring)
                data_page = json.loads(response.text)

                for player in data_page["response"]:
                    to_db = {
                        "id": player["player"]["id"],
                        "name": player["player"]["name"],
                        "full_name": f'{player["player"]["firstname"]} {player["player"]["lastname"]}',
                        "age": player["player"]["age"],
                        "injured": player["player"]["injured"],
                        "nationality": player["player"]["nationality"],
                        "photo": player["player"]["photo"],
                        "team": player["statistics"][0]["team"]["name"]
                    }
                    info_update = {f"{to_db['id']}.INFO": to_db}
                    self.db.collection("roster").document(f"{league} {self.season}").update(info_update)
                    print(player["player"]["name"])

        print("fetch_to_db_completed")

    # def add_to_ids_list(self, league, team, id):
    #     # add this list under each team collection for js client to fetch
    #     # because no function in the js SDK is able to fetch subcollections
    #     old_list = self.db.collection("roster").document(self.season) \
    #         .collection(league).document(team) \
    #         .get()
    #
    #     if old_list.to_dict() is None:
    #         new_list = []
    #     else:
    #         new_list = old_list.to_dict()["ids"]
    #
    #     new_list.append(id)
    #
    #     self.db.collection("roster").document(self.season) \
    #         .collection(league).document(team) \
    #         .set({"ids": new_list})

    def get_today_fixtures(self):
        # this function is ran daily at 0:00 GMT (UTF+0)
        # fetch all the fixtures today in all available leagues(5 in total)
        # return a dict with key: league name/ value: fetch data
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        for league in self.leagues:
            querystring = {"date": self.today,
                           "league": self.get_league_id()[league],
                           "season": self.season}
            headers = {
                'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
                'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)
            fetch_data = json.loads(response.text)
            self.full_data[league] = fetch_data

    def fixtures_to_db(self):
        # this function is ran daily after get_today's_fixture
        # used to store and transfer the JSON data from api to app's db
        # the structure of db collection is:
        # fixture(col)>date(doc)>league(col)>fixture_id(doc)>details(file)
        # on the outer part, iterate through leagues
        # the following data will be saved in the league collection
        # then iterate through fixtures
        # use f-id as doc name and save under the league collection
        for league in self.leagues:
            for response in self.full_data[league]["response"]:
                to_db = {"fixture_id": response["fixture"]["id"],
                         "match_date": self.today,
                         "match_time": Toolbox().process_game_time(response["fixture"]["date"]),
                         "venue": response["fixture"]["venue"]["name"],
                         "status": response["fixture"]["status"]["short"],
                         "season": str(response["league"]["season"]),
                         "round": response["league"]["round"],
                         "home_id": response["teams"]["home"]["id"],
                         "home": response["teams"]["home"]["name"],
                         "away_id": response["teams"]["away"]["id"],
                         "away": response["teams"]["away"]["name"],
                         "goals_h": str(response["goals"]["home"]),
                         "goals_a": str(response["goals"]["away"])
                         }
                doc_id = f"{to_db['season']} - {to_db['home']} vs. {to_db['away']}"
                self.db.collection("fixtures").document(self.today).\
                    collection(league).document(doc_id).set(to_db)

    def get_fixture_lineups_to_db(self):
        # this function will be operated an hour before the match
        # if lineup not found, it will be called again in 20 min before kickoff
        for league in self.leagues:
            # get all saved fixture ids league by league

            # parse all fixture ids from fixture>year>league>fixture>id
            # save ids as f_ids
            fixtures = self.db.collection("fixtures").document(self.today)\
                .collection(league).get()

            # iterate through f_ids
            for e in fixtures:
                e = e.to_dict()
                f_id = e["fixture_id"]
                home = e["home"]
                away = e["away"]
                # fetch lineup with f_id
                url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/lineups"
                querystring = {"fixture":str(f_id)}
                headers = {
                    'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
                    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
                }
                response = requests.request("GET", url, headers=headers, params=querystring)
                lineup = json.loads(response.text)

                # iterate through the two teams in api response

                for team in lineup["response"]:
                    team_name = team["team"]["name"]
                    # parse player ids from team roster doc
                    players = self.db.collection("roster").document(f"{league} {self.season}").get().to_dict()
                    p_ids = list(players.keys())
                    p_ids.remove("INTRO")
                    # set all player in the team as "B"(bench) first
                    for p_id in p_ids:
                        if players[f"{p_id}"]['INFO']["team"] == team_name:
                            to_db = {
                                "home": home,
                                "away": away,
                                "team": team_name,
                                "f_id": f_id,
                                "id": p_id,
                                "pos": "B",
                                "status": "bench",
                                "minutes": 0,
                                "rating": 0.0,
                                "captain": None,
                                "sub": None,
                                "offsides": 0,
                                "shots": 0,
                                "shot_on_goals": 0,
                                "goals": 0,
                                "assists": 0,
                                "saves": 0,
                                "conceded": 0,
                                "passes": 0,
                                "key_passes": 0,
                                "tackles": 0,
                                "blocks": 0,
                                "interceptions": 0,
                                "duels": 0,
                                "duels_won": 0,
                                "dribbles": 0,
                                "dribbles_won": 0,
                                "fouls": 0,
                                "fouls_drawn": 0,
                                "yellow_cards": 0,
                                "red_cards": 0
                            }
                            update_data = {f"{p_id}.{self.today}": to_db}
                            self.db.collection("roster").document(f"{league} {self.season}").update(update_data)

                    # set starters as sub
                    for player in team["startXI"]:

                        p_id =  player["player"]["id"]
                        update_data = {f'{p_id}.{self.today}.pos': player["player"]["pos"]}
                        self.db.collection("roster").document(f"{league} {self.season}").update(update_data)
                        update_data = {f'{p_id}.{self.today}.status': "starting"}
                        self.db.collection("roster").document(f"{league} {self.season}").update(update_data)

                    # set substitutes as sub
                    for player in team["substitutes"]:

                        p_id = player["player"]["id"]
                        update_data = {f'{p_id}.{self.today}.pos': player["player"]["pos"]}
                        self.db.collection("roster").document(f"{league} {self.season}").update(update_data)
                        update_data = {f'{p_id}.{self.today}.status': "sub"}
                        self.db.collection("roster").document(f"{league} {self.season}").update(update_data)

                    print(team_name)
                print("LINEUP UPDATE COMPLETED")

    def get_fixture_stats_to_db(self):
        # this function will be operated every 30 minute in the game, until 120 minutes
        # in other words, this function will be operated five times per game
        for league in self.leagues:
            # get all saved fixture ids league by league
            # parse all fixture id from fixture>year>league>fixture>id
            # save ids as f_ids

            fixtures = self.db.collection("fixtures").document(self.today) \
                .collection(league).get()
            # iterate through f_ids
            for e in fixtures:
                e = e.to_dict()
                # f_id = e.to_dict()["fixture_id"]
                f_id = e["fixture_id"]
                home = e["home"]
                away = e["away"]
                url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/players"
                querystring = {"fixture": f_id}
                headers = {
                    'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
                    'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
                }
                response = requests.request("GET", url, headers=headers, params=querystring)
                player_stats = json.loads(response.text)

                # iterate through two teams
                for team_player_stats in player_stats["response"]:
                    team_name = team_player_stats["team"]["name"]

                    # iterate through all players
                    for player in team_player_stats["players"]:
                        p_id = str(player["player"]["id"])
                        stats = player["statistics"][0]
                        status = "substitute" if stats["games"]["substitute"] else "starting"
                        to_db = {
                            "f_id": f_id,
                            "home": home,
                            "away": away,
                            "team": team_name,
                            "minutes": stats["games"]["minutes"],
                            "rating": stats["games"]["rating"],
                            "captain": stats["games"]["captain"],
                            "sub": status,
                            "offsides": stats["offsides"],
                            "shots": stats["shots"]["total"],
                            "shot_on_goals": stats["shots"]["on"],
                            "goals": stats["goals"]["total"],
                            "assists": stats["goals"]["assists"],
                            "saves": stats["goals"]["saves"],
                            "conceded": stats["goals"]["conceded"],
                            "passes": stats["passes"]["total"],
                            "key_passes": stats["passes"]["key"],
                            "tackles": stats["tackles"]["total"],
                            "blocks": stats["tackles"]["blocks"],
                            "interceptions": stats["tackles"]["interceptions"],
                            "duels": stats["duels"]["total"],
                            "duels_won": stats["duels"]["won"],
                            "dribbles": stats["dribbles"]["attempts"],
                            "dribbles_won": stats["dribbles"]["success"],
                            "fouls": stats["fouls"]["committed"],
                            "fouls_drawn": stats["fouls"]["drawn"],
                            "yellow_cards": stats["cards"]["yellow"],
                            "red_cards": stats["cards"]["red"]
                        }
                        for key, val in to_db.items():
                            if val is None:
                                to_db[key] = 0
                        update_dict = {f"{p_id}.{self.today}":to_db}
                        print(p_id)
                        self.db.collection("roster").document(f"{league} {self.season}").update(update_dict)
                    print(team_name)
            print(f"{league} GAME STATS UPDATE COMPLETED")

    def testflight(self):
        pass