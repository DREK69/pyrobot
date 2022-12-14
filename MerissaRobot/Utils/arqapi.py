from aiohttp import ClientSession
from Python_ARQ import ARQ

from MerissaRobot import ARQ_API_KEY, ARQ_API_URL, OWNER_ID, aiohttpsession, pbot

ARQ_API = "WZQUBA-PFAZQJ-OMIINH-MIVHYM-ARQ"
ARQ_API_KEY = ARQ_API
SUDOERS = OWNER_ID
ARQ_API_URL = "https://thearq.tech"

# Aiohttp Client
print("[INFO]: INITIALZING AIOHTTP SESSION")
aiohttpsession = ClientSession()
# ARQ Client
print("[INFO]: INITIALIZING ARQ CLIENT")
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

app = pbot
