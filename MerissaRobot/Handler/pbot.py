from pyrogram import Client
from config import *
from pytgcalls import PyTgCalls
from pyromod import listen  # ignore

pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=dict(root="MerissaRobot.Modules"),
    workers=min(32, os.cpu_count() + 4),
    sleep_threshold=60,
    in_memory=True,
)

user = Client(
    "MerissaMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=str(STRING_SESSION),
)

pytgcalls = PyTgCalls(user)
