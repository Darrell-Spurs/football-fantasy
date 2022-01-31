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
    def __init__(self):
        self.cats = ['tackles', 'minutes', 'shots','passes',
                     'rating', 'duels_won', 'key_passes',
                     'goals', 'dribbles', 'fouls_drawn', 'assists',
                     'fouls', 'blocks', 'red_cards', 'conceded', 'offsides',
                     'saves', 'yellow_cards', 'dribbles_won',
                     'duels', 'shot_on_goals', 'interceptions']
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


    def get_mds_desc(self,player):
        mds = [md for md in player.keys() if "MD" in md]
        mds = [int(md[2:]) for md in mds]
        mds.sort()
        mds.reverse()
        mds = ["MD"+str(md) for md in mds]
        return mds

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
        self.league = "Premier League"
        self.id_dict = self.get_league_id()
        firebase_admin.get_app()
        self.db = firestore.client()
        # self.today = Toolbox().today_y_m_d()
        self.today = "2021-08-14"
        # self.today = Toolbox().today_y_m_d()
        self.season = "2021"
        self.nseason = "EPL2021-22" # upd: 22.01.24
        self.curr_md = "Regular Season - 2" # variable
        self.doc_md = "MD2" # variable
        self.league_id = self.id_dict[self.league] # upd: 22.01.24
        self.team_ids = self.get_team_ids() # upd: 22.01.24

    def get_league_id(self):
        id_dict = dict()
        with open("api_code.csv") as file:
            content = csv.reader(file)
            for row in content:
                id_dict[row[0]]=row[1]
            file.close()
        return id_dict

    # abandoned
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

    # abandoned, revived on 2022-01-26
    def fetch_all_player_to_db_2(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/players"

        querystring = {"league": self.league_id,
                       "season": self.season}
        headers = {
            'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        page_count = json.loads(response.text)["paging"]["total"]

        for i in range(1,page_count+1):
            querystring = {"league": self.league_id,
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
                    "team": player["statistics"][0]["team"]["name"],
                    "status": "NA"
                }
                self.db.collection(self.nseason).document(str(to_db['id']))\
                    .set({"INFO":to_db,"Season":{},"Last3":{},"Last5":{},"Last10":{}})
                print(player["player"]["name"])

        print("fetch_to_db_completed")

    # get all fixtures in a season (once a season)
    def fetch_all_fixtures(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        querystring = {"league":"39","season":"2021"}
        headers = {
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
            'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce"}

        response = requests.request("GET", url, headers=headers, params=querystring)
        fetch_data = json.loads(response.text)

        for response in fetch_data["response"]:
            date = response["fixture"]["date"][:10]
            rd = response["league"]["round"]
            to_db = {"fixture_id": response["fixture"]["id"],
                     "match_date": date,
                     "match_time": Toolbox().process_game_time(response["fixture"]["date"]),
                     "venue": response["fixture"]["venue"]["name"],
                     "status": response["fixture"]["status"]["short"],
                     "season": str(response["league"]["season"]),
                     "round": rd,
                     "home_id": response["teams"]["home"]["id"],
                     "home": response["teams"]["home"]["name"],
                     "away_id": response["teams"]["away"]["id"],
                     "away": response["teams"]["away"]["name"],
                     "goals_h": str(response["goals"]["home"]),
                     "goals_a": str(response["goals"]["away"])
                     }
            doc_id = f"{to_db['season']} - {to_db['home']} vs {to_db['away']}"
            try:
                self.db.collection(f"{self.nseason} Fixtures").document(rd)\
                    .update({doc_id:to_db})
            except Exception as e:
                self.db.collection(f"{self.nseason} Fixtures").document(rd) \
                    .set({"ok":True})
                self.db.collection(f"{self.nseason} Fixtures").document(rd) \
                    .update({doc_id:to_db})
                self.db.collection(f"{self.nseason} Fixtures").document(rd) \
                    .update({"ok":firestore.DELETE_FIELD})

    # get today's fixtures (once a day) temporarily shut down
    def get_today_fixtures_to_db(self):
        # this function is ran daily at 0:00 GMT (UTF+0)
        # fetch all the fixtures today

        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        querystring = {"date": self.today,
                       "league": self.league_id,
                       "season": self.season}
        headers = {
            'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce",
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        fetch_data = json.loads(response.text)

        print(fetch_data)
        # used to store and transfer the JSON data from api to app's db
        # the structure of db collection is:
        # fixture(col)>date(doc)>league(col)>fixture_id(doc)>details(file)
        # the  data will be saved in league collection (Premier League)
        # then iterate through fixtures
        # use f-id as doc name and save under the league collection

        for response in fetch_data["response"]:
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
                collection(self.league).document(doc_id).set(to_db)
            self.db.collection("fixtures").document("dates")\
                .update({"dates": firestore.ArrayUnion([self.today])})

    # get fixture lineup (once a game, twice if didnt get it the first time)
    def get_fixture_lineups_to_db(self):
        # this function will be operated an hour before the match
        # if lineup not found, it will be called again in 20 min before kickoff

        # fetch all players from firebase first
        players_list = [] # list for player dicts
        db_players = self.db.collection(f"{self.nseason}").get() # get all player docs
        for player in db_players:
            players_list.append(player.to_dict()) # add doc to list

        # print(players_list)

        # get all fixtures of current md
        fixtures = self.db.collection(f"{self.nseason} Fixtures").document(self.curr_md).get().to_dict()

        # iterate through fixtures and get fixture id
        for f in fixtures:
            print(fixtures[f])
            f_id = fixtures[f]["fixture_id"]
            home = fixtures[f]["home"]
            away = fixtures[f]["away"]

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
                team_players = []
                team_name = team["team"]["name"]
                # set all player in the team as "B"(bench) first
                for player in players_list: # iterate thru all players
                    try:
                        if player["INFO"]["team"] == team_name:
                            team_players.append(player["INFO"]["id"])
                            to_db = {
                                "home": home,
                                "away": away,
                                "team": team["team"]["name"],
                                "f_id": f_id,
                                "id": player["INFO"]["id"],
                                "pos": "B",
                                "status": "bench",
                                "minutes": 0,
                                "rating": 0.0,
                                "captain": None,
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
                            self.db.collection(self.nseason).document(str(player["INFO"]["id"]))\
                                .update({f"{self.doc_md}":to_db})
                    except Exception as e:
                        continue

                print(team_players)
                # set starters as starting
                for player in team["startXI"]: # iterate thru fetched lineup
                    p_id = str(player["player"]["id"])
                    if int(p_id) in team_players:
                        update_data = {f'{self.doc_md}.pos': player["player"]["pos"]}
                        self.db.collection(self.nseason).document(p_id).update(update_data)
                        update_data = {f'{self.doc_md}.status': "starting"}
                        self.db.collection(self.nseason).document(p_id).update(update_data)

                # set substitutes as sub
                for player in team["substitutes"]:
                    p_id = str(player["player"]["id"])
                    if p_id in team_players:
                        update_data = {f'{self.doc_md}.pos': player["player"]["pos"]}
                        self.db.collection(self.nseason).document(p_id).update(update_data)
                        update_data = {f'{self.doc_md}.status': "sub"}
                        self.db.collection(self.nseason).document(p_id).update(update_data)
                print(team["team"]["name"])
            print("LINEUP UPDATE COMPLETED")

    def get_fixture_stats_to_db(self):
        # this function will be operated every 30 minute in the game, until 120 minutes
        # in other words, this function will be operated five times per game

        # get all saved fixture ids league by league
        # parse all fixture id from fixture>year>league>fixture>id
        # save ids as f_ids
        fixtures = self.db.collection(f"{self.nseason} Fixtures").document(self.curr_md).get().to_dict()
        print(fixtures)
        # iterate through f_ids
        for f in fixtures:
            print(f)
            matchup = fixtures[f]
            f_id = matchup["fixture_id"]
            home = matchup["home"]
            away = matchup["away"]
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
                    status = "sub" if stats["games"]["substitute"] else "starting"
                    to_db = {
                        "f_id": f_id,
                        "home": home,
                        "away": away,
                        "team": team_name,
                        "minutes": stats["games"]["minutes"],
                        "rating": stats["games"]["rating"],
                        "captain": stats["games"]["captain"],
                        "status": status,
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
                    update_dict = {f"{self.doc_md}":to_db}
                    try:
                        self.db.collection(self.nseason).document(str(p_id)).update(update_dict)
                    except:
                        continue
                    print(p_id)
                print(team_name)

    def recalculate_recent_stats(self):
        players = self.db.collection(f"{self.leagues[0]} {self.season}").get()
        for player in players:
            player_data = player.to_dict()
            game_dates = [key for key in player_data.keys()]
            for gd in game_dates: # remove non dates keys
                if ord(gd[0])!=50:
                    game_dates.remove(gd)

            game_dates.sort(reverse=True)

            # Season
            default = {'passes': 0.0, 'minutes': 0.0, 'fouls': 0.0, 'rating': 0.0, 'duels': 0.0, 'yellow_cards': 0.0, 'shots': 0.0, 'fouls_drawn': 0.0, 'offsides': 0.0, 'conceded': 0.0, 'dribbles': 0.0, 'blocks': 0.0, 'duels_won': 0.0, 'saves': 0.0, 'shot_on_goals': 0.0, 'tackles': 0.0, 'assists': 0.0, 'dribbles_won': 0.0, 'key_passes': 0.0, 'red_cards': 0.0, 'goals': 0.0, 'interceptions': 0.0}
            temp_total = {'Season': default, 'Last10': default, 'Last5': default, 'Last3': default}
            for i in range(len(game_dates)):
                gd = game_dates[i]
                for key in player_data[gd].keys():
                    if (type(player_data[gd][key]) == int or type(player_data[gd][key]) == float) \
                            and key not in ["age","f_id","id"]:
                        temp_total["Season"][key] += player_data[gd][key]
                        if i<10: temp_total["Last10"][key] += player_data[gd][key]
                        if i<5: temp_total["Last5"][key] += player_data[gd][key]
                        if i<3: temp_total["Last3"][key] += player_data[gd][key]
            self.db.collection(f"{self.leagues[0]} {self.season}").document(str(player_data["INFO"]["id"])).update(temp_total)
            print(temp_total)
            print(player_data["INFO"]["id"])

    def testflight(self):
        pass

    def find_all_teams(self):
        # find all team ids from league, using "Teams informations" endpoint
        # Getting ids allows db to find the team current sqauds more easily
        # See: "get_team_ids" and "find_all_team_squads"
        url = "https://api-football-v1.p.rapidapi.com/v3/teams"
        querystring = {"league":self.league_id,"season":self.season}
        headers = {
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
            'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        for team in data["response"]:
            self.db.collection("Team_IDs").document(self.nseason)\
                .update({team["team"]["name"].replace(" ","_"):team["team"]["id"]})
        return "Team IDs found"

    def get_team_ids(self):
        team_ids = self.db.collection("Team_IDs").document(self.nseason).get().to_dict()
        return team_ids

    def add_all_team_squads(self):
        # find all team squads by iterating thru team ids
        url = "https://api-football-v1.p.rapidapi.com/v3/players/squads"
        for team in self.team_ids:
            querystring = {"team":self.team_ids[team]}
            headers = { 'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
                'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce"}
            response = requests.request("GET", url, headers=headers, params=querystring)
            # get response dada
            players = json.loads(response.text)
            # In response, idx 0 is the team info
            # idx 1 is a dict with "players" as key and a list of  players dicts as value
            # find player id for document id and the rest of info for the INFO value
            for plr in players["response"][0]["players"]:
                try:
                    self.db.collection(self.nseason).document(str(plr["id"]))\
                        .update({"INFO.status":"active"})
                    print(plr["id"])
                except Exception as e:
                    self.db.collection(self.nseason).document(str(plr["id"])) \
                        .set({"INFO":{"id":str(plr['id']),"name":plr["name"]}})
                    self.db.collection("new").document(str(plr["id"]))\
                        .set({"INFO":{"id":str(plr['id']),"name":plr["name"]}})

    def get_injuries(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/injuries"
        querystring = {"league":self.league_id,"season":self.season,"date":self.today}
        headers = {
            'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
            'x-rapidapi-key': "b56ffa1a8dmshda48f616f1ec5bcp1dc2b2jsn37fbb2fff2ce"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)["response"]
        self.db.collection("Injuries").document(self.today).set({"checked":True})
        for item in data:
            item.pop("league")
            print(item)
            self.db.collection("Injuries").document(self.today)\
                .update({str(item["player"]["id"]):item})
        self.db.collection("Injuries").document(self.today).update({"checked":firestore.DELETE_FIELD})

    def update_latest_stats(self):
        all_players = self.db.collection(self.nseason).get()
        for player in all_players:
            player = player.to_dict()
            p_id = str(player["INFO"]["id"])
            p_stats = self.db.collection(self.nseason).document(p_id).get().to_dict()
            tb = Toolbox()
            cats = tb.cats
            mds = tb.get_mds_desc(p_stats)
            to_db = {"Last3":{},"Last3A":{},"Last5":{},"Last5A":{},
                     "Last10":{},"Last10A":{},"Season":{},"SeasonA":{}}
            for cat in cats:
                # last 3
                games3 = len([(p_stats[md]["minutes"]) for md in mds[:3] if (p_stats[md]["minutes"])!=0])
                ttl3 = round(sum([float(p_stats[md][cat]) for md in mds[:3]]),2)
                avg3 = 0 if games3==0 else round((ttl3/games3),2)
                to_db["Last3"][cat] = ttl3
                to_db["Last3A"][cat] = avg3
    
                # last 5
                games5 = len([(p_stats[md]["minutes"]) for md in mds[:5] if (p_stats[md]["minutes"])!=0])
                ttl5 = round(sum([float(p_stats[md][cat]) for md in mds[:5]]),2)
                avg5 = 0 if games5==0 else round((ttl5/games5),2)
                to_db["Last5"][cat] = ttl5
                to_db["Last5A"][cat] = avg5
    
                # last 10
                games10 = len([(p_stats[md]["minutes"]) for md in mds[:10] if (p_stats[md]["minutes"])!=0])
                ttl10 = sum([float(p_stats[md][cat]) for md in mds[:10]])
                avg10 = 0 if games10==0 else round((ttl10/games10),2)
                to_db["Last10"][cat] = ttl10
                to_db["Last10A"][cat] = avg10
    
            # season
                gamesS = len([(p_stats[md]["minutes"]) for md in mds if (p_stats[md]["minutes"])!=0])
                ttlS = sum([float(p_stats[md][cat]) for md in mds])
                avgS = 0 if gamesS==0 else round((ttlS/gamesS),2)
                to_db["Season"][cat] = ttlS
                to_db["SeasonA"][cat] = avgS
    
            self.db.collection(self.nseason).document(p_id).update(to_db)
            print(p_id, player["INFO"]["name"])

