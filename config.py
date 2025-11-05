import os
from os import getenv

TOKEN = os.environ.get("TOKEN", "8343128787:AAEaR_z_N5KZt8u983jQhQYgBLipgrtUnHg")
INFOPIC = bool(os.environ.get("INFOPIC", True))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "MerissaRobot")
EVENT_LOGS = os.environ.get("EVENT_LOGS", "-1002846516370")
WEBHOOK = bool(os.environ.get("WEBHOOK", False))
URL = os.environ.get("URL", "")  # Does not contain token
PORT = int(os.environ.get("PORT", 5000))
CERT_PATH = os.environ.get("CERT_PATH")
API_ID = os.environ.get("API_ID", "25723056")
ERROR_LOG = os.environ.get("ERROR_LOG", "-1002846516370")
API_HASH = os.environ.get("API_HASH", "cbda56fac135e92b755e1243aefe9697")
STRING_SESSION = getenv(
    "STRING_SESSION",
    "BAF1s6cAE2WAy1nlvQltzexh2CZGWrN8QW_DH7U_jm2_PsZwFntvid_rghGPfcAc77iKXgZL_5LSvxQH_luHmLO9YOcxQ3ZZOQvI9RORRUhZFp_g--qnsU4DkHS1HA3nAnNSeF6bT3ajpUPkLiQ4chJalHmA1bpZHgNMdOskYVgvJUoV4rKk48GuR7c-aiea--I1qdXCPsRL4QxmI362wEKlIp3wVaGFOIXpuRZvH6BZ7ovxfgSppPKKqdGy64PmozFHXTyIQP46-tEAnUMQxRYSe68L0MRH_PdZz6_t5lUia-EirmLb6pGUalQvL4TOWiqwjx9M-fltRKSr_CMM4XNZVGhezgAAAAGD1WQBAA",
)
MERISSA_TOKEN = os.environ.get("MERISSA_TOKEN", "nZWMiKdkDvSJMmSm")
OWNER_ID = int(os.environ.get("OWNER_ID", "7110457701"))
BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split())
DEMONS = set(int(x) for x in os.environ.get("DEMONS", "").split())
DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split())
DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "2030709195").split())
WOLVES = set(int(x) for x in os.environ.get("WOLVES", "").split())
TIGERS = set(int(x) for x in os.environ.get("TIGERS", "").split())
JOIN_LOGGER = os.environ.get("JOIN_LOGGER", "-1002846516370")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "DEPSTEY")
FORCE_CHANNEL = int(os.environ.get("FORCE_CHANNEL", "-1001703270696"))
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://sahil_user:sahil123@localhost:5432/sahil",
)
DB_URI = DB_URL.replace("postgres://", "postgresql://", 1)
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", "")
MONGO_DB_URI = os.environ.get(
    "MONGO_DB_URI",
    "mongodb+srv://drek:drek@cluster0.hjcba3x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)
DONATION_LINK = os.environ.get("DONATION_LINK", "https://t.me/noobxcoder")
LOAD = os.environ.get("LOAD", "").split()
HEROKU_API_KEY = os.environ.get(
    "HEROKU_API_KEY", "3311eb9b-8901-4919-b291-b8af7999c6a6"
)
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", "merissarobot")
REDIS_URL = os.environ.get(
    "REDIS_URL",
    "redis://:lOefDkX6KmJ1qy5MrlIKTxfZrq4BJzUC@redis-17983.c240.us-east-1-3.ec2.cloud.redislabs.com:17983/Merissadb",
)
STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", True))
STRICT_GMUTE = bool(os.environ.get("STRICT_GMUTE", True))
TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")
OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", "")
VIRUS_API_KEY = os.environ.get("VIRUS_API_KEY", "")
NO_LOAD = os.environ.get("NO_LOAD", "").split()
DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
WORKERS = int(os.environ.get("WORKERS", 1))
BAN_STICKER = os.environ.get("BAN_STICKER", "CAADAgADOwADPPEcAXkko5EB3YGYAg")
ALLOW_EXCL = os.environ.get("ALLOW_EXCL", False)
BOT_API_URL = os.environ.get("BOT_API_URL", "https://api.telegram.org/bot")
CASH_API_KEY = os.environ.get("CASH_API_KEY", "")
TIME_API_KEY = os.environ.get("TIME_API_KEY", "")
WALL_API = os.environ.get("WALL_API", "")
IBM_WATSON_CRED_PASSWORD = os.environ.get(
    "IBM_WATSON_CRED_PASSWORD", "UQ1MtTzZhEsMGK094klnfa-7y_4MCpJY1yhd52MXOo3Y"
)
IBM_WATSON_CRED_URL = os.environ.get(
    "IBM_WATSON_CRED_URL",
    "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/bd6b59ba-3134-4dd4-aff2-49a79641ea15",
)
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "MerissaxLogs")
SPAMWATCH_SUPPORT_CHAT = os.environ.get("SPAMWATCH_SUPPORT_CHAT", "")
SPAMWATCH_API = os.environ.get(
    "SPAMWATCH_API", "Vcri8SKQ98A_Lw9qvf6pBzv1IRL3uQAhFj871XTvnfqi2tKjNgDaSRViPFQbs06x"
)
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY", "")
CF_API_KEY = os.environ.get("CF_API_KEY", None)
WELCOME_DELAY_KICK_SEC = os.environ.get("WELCOME_DELAY_KICL_SEC", "")
BOT_ID = int(os.environ.get("BOT_ID", "5294959338"))
ARQ_API_URL = os.environ.get("ARQ_API_URL", "https://arq.hamker.in")
ARQ_API_KEY = os.environ.get("ARQ_API_KEY", "IXJDNK-GURMUL-HPGZYX-TPJKKT-ARQ")
BACKUP_PASS = os.environ.get("BACKUP_PASS", None)
ALLOW_CHATS = os.environ.get("ALLOW_CHATS", True)
