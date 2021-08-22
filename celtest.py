# Celery imports
from celery import Celery, shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.schedules import crontab

# built-ins
import json, os, time, requests, re
from time import gmtime as lt

# Selenium crawler imports
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# for configs and making an instance
from main import web_app

# toolbox
from modules import Toolbox

# firebase db initialize
import firebase_admin
from firebase_admin import credentials, firestore
firebase_admin.get_app()

print("Fire")
# celery definition and initialize
def make_celery(app):

    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
        task_routes = app.config["TASK_ROUTES"],
        timezone = "Asia/Taipei",
        # beat_schedule = {
        #     'add-5': {
        #         'task': 'tasks.add',
        #         'schedule': 5.0,
        #         'args': (16, 4)
        #     },
        # }
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(web_app)

# celery beat settings
# @celery.on_after_configure.connect()
# def routine_setting(sender, **kwargs):
#     sender.add_periodic_task(
#         crontab(minute='*/10',hour='0,1,2,3,4,5,21,22,23'),
#         live_fetch.s(),
#         name="Live Fetch"
#     )
    # sender.add_periodic_task(
    #     crontab(minute=0,hour='0,12'),
    #     playerstats_fetch.s("WC QUAL. (CONMEBOL) 2021"),
    #     name="Regular Fetch"
    # )


@celery.task()
def add(a=1, b=2):
    return a + b

# @celery.task()
# def fetch_api(url):
#     res = requests.get(url)
#     return res.json()

# @celery.task()
# def cs_fetch(test=False):
#     print("GO")
#     options = webdriver.ChromeOptions()
#     SELENIUM = celery.conf['SELENIUM']
#
#     # Check current status to decide how to execute Chrome Driver
#     if SELENIUM == "LOCAL_FILE": # Development stage
#         if not test:
#             options.add_argument('--headless')
#             pass
#         driver = webdriver.Chrome(executable_path=r"C:\Users\darre\chromedriver.exe",
#                                   options=options)
#
#     elif SELENIUM == "BINARY": # Testing/Formal stage
#         print("BINARY")
#         options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#         options.add_argument('--headless')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--no-sandbox')
#         driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"),
#                                   options=options)
#
#     else:
#         raise("SELENIUM configuration error")
#
#     driver.get("https://www.footballcritic.com/#2021-3-8")
#     print(f"Getting: {driver.current_url}")
#     driver.implicitly_wait(30)
#     time.sleep(3)
#
#     # notification handler
#     if test:
#         print("test")
#         no_thanks = driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/button[2]")
#         ActionChains(driver).click(no_thanks).perform()
#         agree = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/button[2]")
#         ActionChains(driver).click(agree).perform()
#
#     # main scraper
#     def get_top_players():
#         things = driver.find_elements_by_css_selector(
#             "table[class='playerList halfList list_A']>tbody>tr>td:nth-child(3)>a"
#         )
#         for thing in things:
#             got_url = thing.get_attribute("href")
#             print(got_url+"\n" if "squad" not in got_url else "", end="")
#
#     def get_todays_games():
#
#         available_leagues=["England","Spain"]
#         game_links = []
#
#         leagues = driver.find_elements_by_css_selector("div[class~='info-block']")
#         for league in leagues:
#             league_name = league.find_element_by_css_selector("div>span:nth-child(2)>span")
#
#             if league_name.text in available_leagues:
#                 games = league.find_elements_by_css_selector('ul>li>a')
#                 for game in games:
#                     game_links.append(game.get_attribute("href").replace("match-stats","player-stats"))
#
#         return list(set(game_links))
#
#     ulrs = get_todays_games()
#     driver.implicitly_wait(80)
#
#     # closure
#     driver.close()
#     return ulrs


@celery.task()
def playerstats_fetch(tar_league):
    options = webdriver.ChromeOptions()
    SELENIUM = celery.conf['SELENIUM']

    # Check current status to decide how to execute Chrome Driver
    if SELENIUM == "LOCAL_FILE":  # Development stage
        options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=r"C:\Users\darre\cd.exe",
                                  options=options)

    elif SELENIUM == "BINARY":  # Testing/Formal stage
        print("BINARY")
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"),
                                  options=options)

    else:
        raise ("SELENIUM configuration error")

    driver.get('https://www.playmakerstats.com/ultimos_resultados.php')
    driver.implicitly_wait(30)
    time.sleep(1)

    links_dict = {}
    boxes = driver.find_elements_by_css_selector('div[id="page_main"]>div[class="box"]')[1:]
    game_date = ""
    for box in boxes:
        comp_name = box.find_element_by_class_name("smallheader").text
        links_dict[comp_name]=[]
        game_date = box.find_element_by_css_selector("td[class='date']").text
        links = box.find_elements_by_css_selector("td[class='result']>a")
        links_dict[comp_name].extend([link.get_attribute("href").replace("jogo","match_performance") for link in links])
    print(links_dict)

    game_log = []
    for link in links_dict[tar_league]:
        driver.get(link)
        rows = driver.find_elements_by_css_selector("tbody>tr[role='row']")
        for row in rows:
            try:
                tds = row.find_elements_by_tag_name("td")
                if tds[0].text == '':
                    continue
                wanted = {
                        "Name":tds[0].text,
                        "Team":tds[1].text,
                        "Position":tds[2].text,
                        "Minutes":tds[3].text,

                        "Goals":tds[4].text, #S1
                        "Assists":tds[6].text, #S2
                        "Shots": tds[12].text,  # S3
                        "Shots on Target": tds[13].text,  # S3

                        "Yellow Cards":tds[7].text, #S4
                        "Red Cards":tds[8].text, #S4

                        "Tackles": tds[15].text,  # S5
                        "Steals": tds[16].text,  # S6

                        "Total Passes": tds[17].text,  # S7
                        "Passes": tds[18].text, #S7

                        "Saves": tds[20].text, #S8

                        "Fouls Committed":tds[21].text,
                        "Fouls Suffered":tds[22].text,

                        "Update Time": f"{lt().tm_year}-{lt().tm_mon}-{lt().tm_mday-1}"
                        }
                game_log.append(wanted)
            except Exception as e:
                print(e)
                continue
        time.sleep(1)
        print(game_log)
    driver.close()

    db = firestore.client()

    def update_firebase(d,date,name,league):
        try:
            existed = db.collection(league).document(name).get({date}).to_dict()
            if existed!=d:
                raise("Update again")
            return
        except:
            try:
                db.collection(league).document(name).update({date: d})
            except:
                db.collection(league).document(name).set({date: d})
            try:
                doc = db.collection(league).document(name).get().to_dict()
                for cat in d.keys():
                    single_cat = sum([j[cat] if i != "total" else 0 for i, j in doc.items()])
                    db.collection(league).document(name).update({f"Total.{cat}": single_cat})
            except:
                db.collection(league).document(name).update({"Total":d})

    for player in game_log:
        update_firebase(player,game_date,player["Name"],tar_league)
        # db.collection("roster").document(player["Name"]).set(player)
        print(player["Name"])
        print(player)

    return game_log

# @celery.task()
# def live_fetch():
#     options = webdriver.ChromeOptions()
#     SELENIUM = celery.conf['SELENIUM']
#
#     # Check current status to decide how to execute Chrome Driver
#     if SELENIUM == "LOCAL_FILE":  # Development stage
#         options.add_argument('--headless')
#         driver = webdriver.Chrome(executable_path=r"C:\Users\darre\cd.exe",
#                                   options=options)
#
#     elif SELENIUM == "BINARY":  # Testing/Formal stage
#         print("BINARY")
#         options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#         options.add_argument('--headless')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--no-sandbox')
#         driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"),
#                                   options=options)
#
#     else:
#         raise ("SELENIUM configuration error")
#
#     driver.get('https://www.playmakerstats.com/zzlivescore.php')
#     driver.implicitly_wait(30)
#     time.sleep(1)
#
#     toolbox = Toolbox()
#     links_dict = {}
#     boxes = driver.find_elements_by_css_selector('div[id="page_main"]>div[class="box"]')[1:]
#     to_collect = ["European Championship"]
#     for box in boxes:
#         comp_name = box.find_element_by_class_name("smallheader").text
#         if comp_name[2:] not in to_collect:
#             continue
#         links_dict[comp_name[2:]]=[]
#         matchup = box.find_elements_by_css_selector("table>tbody>tr>td[class*='text']")
#         links = box.find_elements_by_css_selector("table>tbody>tr>td[class*='result']>a")
#         for link in links:
#             print(link.text)
#             link = link.get_attribute("href").replace("match_live","match_performance").replace("jogo","match_performance")
#             links_dict[comp_name[2:]].append(link)
#     print(links_dict)
#
#     game_log = []
#     for league, link_list in links_dict.items():
#         print(league,link_list)
#         for link in link_list:
#             driver.get(link)
#             rows = driver.find_elements_by_css_selector("tbody>tr[role='row']")
#             for row in rows:
#                 try:
#                     tds = row.find_elements_by_tag_name("td")
#                     if tds[0].text=='':
#                         continue
#                     wanted = toolbox.parsing_stats(tds, False)
#                     game_log.append(wanted)
#                 except Exception as e:
#                     print(e)
#                     continue
#             time.sleep(1)
#             print(game_log)
#         driver.close()
#
#         db = firestore.client()
#
#         def update_firebase(d,date,name,league):
#             try:
#                 existed = db.collection(league).document(name).get({date}).to_dict()
#                 if existed!=d:
#                     raise("Update again")
#                 return
#             except:
#                 try:
#                     db.collection(league).document(name).update({date: d})
#                 except:
#                     db.collection(league).document(name).set({date: d})
#                 try:
#                     doc = db.collection(league).document(name).get().to_dict()
#                     for cat in d.keys():
#                         single_cat = sum([j[cat] if i != "total" else 0 for i, j in doc.items()])
#                         db.collection(league).document(name).update({f"Total.{cat}": single_cat})
#                 except:
#                     db.collection(league).document(name).update({"Total":d})
#
#         for player in game_log:
#             update_firebase(player,toolbox.yesterday(),player["Name"],league)
#             # db.collection("roster").document(player["Name"]).set(player)
#             print(player["Name"])
#             print(player)
#
#     return game_log

@celery.task()
def live_fetch():
    return "0"


