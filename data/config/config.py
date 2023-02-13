from environs import Env
from utils.getProjectPath import get_project_path

env = Env()

env.read_env(get_project_path() + '/data/config/PRIVATE_KEYS.env')

BOT_TOKEN = env.str('BOT_TOKEN')
API_KEY = env.str('API_KEY')

if BOT_TOKEN == 'token':
    raise Exception("BOT_TOKEN isn't set")

if API_KEY == 'api_key':
    raise Exception("API_KEY isn't set")

ADMINS_ID = {}
