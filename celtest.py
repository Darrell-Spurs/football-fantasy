from celery import Celery, shared_task
from celery.result import AsyncResult
import json, os, time,requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from main import web_app
from celery.exceptions import SoftTimeLimitExceeded

# https://docs.celeryproject.org/en/latest/userguide/canvas.html#chains

def make_celery(app):

    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
        # backend="redis://127.0.0.1:6379",
        # broker="redis://127.0.0.1:6379",
        task_routes = app.config["TASK_ROUTES"]
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery

celery = make_celery(web_app)

@celery.task()
def add(a, b):
    return a + b

@celery.task()
def tsum(a):
    return sum(a)

@celery.task()
def mul(a, b):
    return a * b

@celery.task()
def fetch_api(url):
    res = requests.get(url)
    return res.json()

@celery.task()
def cs_fetch(test=False):
    print("GO")
    options = webdriver.ChromeOptions()
    SELENIUM = celery.conf['SELENIUM']

    # Check current status to decide how to execute Chrome Driver
    if SELENIUM == "LOCAL_FILE": # Development stage
        if not test:
            options.add_argument('--headless')
            pass
        driver = webdriver.Chrome(executable_path=r"C:\Users\darre\chromedriver.exe",
                                  options=options)

    elif SELENIUM == "BINARY": # Testing/Formal stage
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"),
                                  options=options)

    else:
        raise("SELENIUM configuration error")

    driver.get("https://www.footballcritic.com/#2021-3-8")
    print(f"Getting: {driver.current_url}")
    driver.implicitly_wait(30)
    time.sleep(3)

    # notification handler
    if test:
        print("test")
        no_thanks = driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/button[2]")
        ActionChains(driver).click(no_thanks).perform()
        agree = driver.find_element_by_xpath("/html/body/div[1]/div/div/div/div[2]/div/button[2]")
        ActionChains(driver).click(agree).perform()

    # main scraper
    def get_top_players():
        things = driver.find_elements_by_css_selector(
            "table[class='playerList halfList list_A']>tbody>tr>td:nth-child(3)>a"
        )
        for thing in things:
            got_url = thing.get_attribute("href")
            print(got_url+"\n" if "squad" not in got_url else "", end="")

    def get_todays_games():

        available_leagues=["England","Spain"]
        game_links = []

        leagues = driver.find_elements_by_css_selector("div[class~='info-block']")
        for league in leagues:
            league_name = league.find_element_by_css_selector("div>span:nth-child(2)>span")

            if league_name.text in available_leagues:
                games = league.find_elements_by_css_selector('ul>li>a')
                for game in games:
                    game_links.append(game.get_attribute("href").replace("match-stats","player-stats"))

        return list(set(game_links))

    ulrs = get_todays_games()
    driver.implicitly_wait(80)

    # closure
    driver.close()
    return ulrs

# celery -A celtest worker --loglevel=INFO -P eventlet
