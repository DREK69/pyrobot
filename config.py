import os
TOKEN = os.environ.get("TOKEN", "5294959338:AAEL49jv6ALz_5c6zDDGUMq-Al4q2WmsNf8")
INFOPIC = bool(os.environ.get("INFOPIC", True))
BOT_USERNAME = os.environ.get("BOT_USERNAME", "MerissaRobot")
EVENT_LOGS = os.environ.get("EVENT_LOGS", "-1001325865052")
WEBHOOK = bool(os.environ.get("WEBHOOK", False))
URL = os.environ.get("URL", "")  # Does not contain token
PORT = int(os.environ.get("PORT", 5000))
CERT_PATH = os.environ.get("CERT_PATH")
API_ID = os.environ.get("API_ID", "8673250")
ERROR_LOG = os.environ.get("ERROR_LOG", "-1001446814207")
API_HASH = os.environ.get("API_HASH", "bab0eb3130eb4930cc40112635b2dc4d")
STRING_SESSION = os.environ.get(
    "STRING_SESSION",
    "1BVtsOHsBu4_11VWDHJNWs4zed74r7oR0KuZCCYjt9yLO2KXMvbdCM5I3_yHczhbKsupvV0heVK9-ckA6ngtexzxZjvM5RmXTSMATHVzzOW_pqfADAA4C90RiEsCe_HGN_T4Z44HrZFFmejbvRvxffmRgqc7lUw5vzInyluckBkvzVBnOtmLvTf-RfrbHp5YlV1Xqht4lLfF_Lr3mZx4JCkDL5q4ClFC7yhs530fNCmiDtz32bOGMiFS_4FJM9W0Svr5yR1_DWduC4whw1rxVJm1L6vE3iEGl1C79Gen5LX8DRhfzn6B1S7umBB8WSwI_MNxmdA49J7wgon4NnK0ZoPcXReXjrNg=",
)
MERISSA_TOKEN = os.environ.get("MERISSA_TOKEN", "nZWMiKdkDvSJMmSm")
OWNER_ID = int(os.environ.get("OWNER_ID", "2030709195"))
BL_CHATS = set(int(x) for x in os.environ.get("BL_CHATS", "").split())
DEMONS = set(int(x) for x in os.environ.get("DEMONS", "").split())
DRAGONS = set(int(x) for x in os.environ.get("DRAGONS", "").split())
DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "2030709195").split())
WOLVES = set(int(x) for x in os.environ.get("WOLVES", "").split())
TIGERS = set(int(x) for x in os.environ.get("TIGERS", "").split())
JOIN_LOGGER = os.environ.get("JOIN_LOGGER", "-1001325865052")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "NoobxCoder")
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgres://prince:prince1234@ls-e6c4b74049f7e42d52874d434d6c15f85c25c82a.cmcksriktjsm.ap-south-1.rds.amazonaws.com:5432/merissa",
)
DB_URI = DB_URL.replace("postgres://", "postgresql://", 1)
REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", "")
MONGO_DB_URI = os.environ.get(
    "MONGO_DB_URI",
    "mongodb+srv://merissa:merissa@cluster0.tuhlo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
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
NO_LOAD = os.environ.get("NO_LOAD", "translation").split()
DEL_CMDS = bool(os.environ.get("DEL_CMDS", False))
STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", False))
WORKERS = int(os.environ.get("WORKERS", 8))
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
