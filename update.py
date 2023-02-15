from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ
from subprocess import run as srun
from dotenv import load_dotenv
from pymongo import MongoClient
from requests import get


def dw_file(url, filename):
        r = get(url, allow_redirects=True, stream=True)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return


###############------Download_Config------###############
CONFIG_FILE_URL = environ.get("CONFIG_FILE_URL", False)
if CONFIG_FILE_URL and str(CONFIG_FILE_URL).startswith("http"):
    dw_file(str(CONFIG_FILE_URL), "config.env")

load_dotenv('config.env', override=True)

ACCOUNTS_ZIP_URL = environ.get("ACCOUNTS_ZIP_URL", False)
TOKEN_PICKLE_URL = environ.get("TOKEN_PICKLE_URL", False)
if ACCOUNTS_ZIP_URL and str(ACCOUNTS_ZIP_URL).startswith("http"):
    dw_file(str(ACCOUNTS_ZIP_URL), "accounts.zip")
if TOKEN_PICKLE_URL and str(TOKEN_PICKLE_URL).startswith("http"):
    dw_file(str(TOKEN_PICKLE_URL), "token.pickle")

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        log_error('The README.md file there to be read! Exiting now!')
        exit()
except:
    pass

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = int(BOT_TOKEN.split(':', 1)[0])

DATABASE_URL = environ.get('DATABASE_URL', '')
if len(DATABASE_URL) == 0:
    DATABASE_URL = None

if DATABASE_URL:
    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    if config_dict := db.settings.config.find_one({'_id': bot_id}):  #retrun config dict (all env vars)
        environ['UPSTREAM_REPO'] = config_dict['UPSTREAM_REPO']
        environ['UPSTREAM_BRANCH'] = config_dict['UPSTREAM_BRANCH']
    conn.close()

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
   UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if UPSTREAM_REPO:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email jmdkh007@gmail.com \
                     && git config --global user.name jmdkh \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        log_info('Successfully updated with latest commit from UPSTREAM_REPO')
    else:
        log_error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')