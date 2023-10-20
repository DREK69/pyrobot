import json
import traceback

from pyrogram.enums import ParseMode

from MerissaRobot import pbot as app
from MerissaRobot.helpers import subscribed
from MerissaRobot.Utils.Helpers.inlinefuncs import *

__MODULE__ = "Inline"
__HELP__ = """See inline for help related to inline"""


@app.on_inline_query()
async def inline_query_handler(client, query):
    try:
        text = query.query.strip().lower()
        answers = []
        if text.strip() == "":
            answerss = await inline_help_func(answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "about":
            answerss = await about_function(answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "tr":
            if len(text.split()) < 3:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Translator | tr [LANG] [TEXT]",
                    switch_pm_parameter="inline",
                )
            lang = text.split()[1]
            tex = text.split(None, 2)[2].strip()
            answerss = await translate_func(answers, lang, tex)
            await client.answer_inline_query(
                query.id,
                results=answerss,
            )
        elif text.split()[0] == "ud":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Urban Dictionary | ud [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await urban_func(answers, tex)
            await client.answer_inline_query(
                query.id,
                results=answerss,
            )
        elif text.split()[0] == "google":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Google Search | google [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await google_search_func(answers, tex)
            await client.answer_inline_query(
                query.id,
                results=answerss,
            )

        elif text.split()[0] == "paste":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="paste | paste [TEXT]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await paste_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "wall":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    is_gallery=True,
                    switch_pm_text="Wallpapers Search | wall [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await wall_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "saavn":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Saavn Search | saavn [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await saavn_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "ytdl":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Youtube Video Download | ytdown [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await ytdown_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "ymdl":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Youtube Music Download | ymdl [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await ytmdown_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "ymlink":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Youtube Music Search | ytmlink [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await ytmusic_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "spotify":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Spotify Music Search | spotify [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await spotify_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "torrent":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Torrent Search | torrent [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await torrent_func(answers, tex)
            await client.answer_inline_query(
                query.id,
                results=answerss,
            )

        elif text.split()[0] == "anime":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Anime Search | anime [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await anime_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "ytlink":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="YouTube Search | yt [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await youtube_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "ph":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="PornHub | ph [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await ph_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "lyrics":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Lyrics Search | lyrics [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await lyrics_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "search":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Global Message Search. | search [QUERY]",
                    switch_pm_parameter="inline",
                )
            user_id = query.from_user.id
            tex = text.split(None, 1)[1].strip()
            answerss = await tg_search_func(answers, tex, user_id)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "music":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Music Search | music [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await ytmdown_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "wiki":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Wikipedia | wiki [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await wiki_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "github":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="github | github [repo]",
                    switch_pm_parameter="inline",
                )
            results = []
            tex = text.split(None, 1)[1]
            item = requests.get(
                f"https://api.github.com/search/repositories?q={tex}"
            ).json()["items"]
            results = []
            for sraeo in item:
                title = sraeo.get("full_name")
                link = sraeo.get("html_url")
                deskripsi = sraeo.get("description")
                lang = sraeo.get("language")
                message_text = f"🔗: {sraeo.get('html_url')}\n│\n└─🍴Forks: {sraeo.get('forks')}    ┃┃    🌟Stars: {sraeo.get('stargazers_count')}\n\n"
                message_text += f"<b>Description:</b> {deskripsi}\n"
                message_text += f"<b>Language:</b> {lang}"
                results.append(
                    InlineQueryResultArticle(
                        title=f"{title}",
                        input_message_content=InputTextMessageContent(
                            message_text=message_text,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=False,
                        ),
                        url=link,
                        description=deskripsi,
                        thumb_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="Open Github Link", url=link)]]
                        ),
                    )
                )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "ping":
            answerss = await ping_func(answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "webss":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="webss | webss [url]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await webss(tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "pypi":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="pypi | pypi [query]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1]
            search_results = requests.get(f"https://yasirapi.eu.org/pypi?q={tex}")
            srch_results = search_results.json()
            answers = []
            for sraeo in srch_results["result"]:
                title = sraeo.get("name")
                link = sraeo.get("url")
                deskripsi = sraeo.get("description")
                version = sraeo.get("version")
                message_text = f"<a href='{link}'>{title} {version}</a>\n"
                message_text += f"Description: {deskripsi}\n"
                answers.append(
                    InlineQueryResultArticle(
                        title=f"{title}",
                        input_message_content=InputTextMessageContent(
                            message_text=message_text,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=False,
                        ),
                        url=link,
                        description=deskripsi,
                        thumb_url="https://raw.githubusercontent.com/github/explore/666de02829613e0244e9441b114edb85781e972c/topics/pip/pip.png",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="Open Link", url=link)]]
                        ),
                    )
                )
            await client.answer_inline_query(query.id, results=answers, cache_time=2)

        elif text.split()[0] == "info":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="User Info | info [USERNAME|ID]",
                    switch_pm_parameter="inline",
                )
            tex = text.split()[1].strip()
            answerss = await info_inline_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "imdb":
            if len(text.split()) < 2:
                answerss = await tmdb_func(answers, "")
                return await client.answer_inline_query(
                    query.id,
                    results=answerss,
                    switch_pm_text="IMDB Search | imdb [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split()[1].strip()
            search_results = requests.get(
                f"https://yasirapi.eu.org/imdb-search?q={tex}"
            )
            res = json.loads(search_results.text).get("result")
            answers = []
            for midb in res:
                title = midb.get("l", "")
                description = midb.get("q", "")
                stars = midb.get("s", "")
                imdb_url = f"https://imdb.com/title/{midb.get('id')}"
                year = f"({midb.get('y', '')})"
                image_url = (
                    midb.get("i").get("imageUrl").replace(".jpg", "._V1_UX360.jpg")
                    if midb.get("i")
                    else "https://te.legra.ph/file/e263d10ff4f4426a7c664.jpg"
                )
                caption = f"<a href='{image_url}'>🎬</a>"
                caption += f"<a href='{imdb_url}'>{title} {year}</a>"
                answers.append(
                    InlineQueryResultPhoto(
                        title=f"{title} {year}",
                        caption=caption,
                        description=f" {description} | {stars}",
                        photo_url=image_url,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="Get IMDB details",
                                        callback_data=f"imdbinl#{inline_query.from_user.id}#{midb.get('id')}",
                                    )
                                ]
                            ]
                        ),
                    )
                )
            await client.answer_inline_query(query.id, results=answers, cache_time=2)

        elif text.split()[0] == "pokedex":
            if len(text.split()) < 2:
                await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Pokemon [text]",
                    switch_pm_parameter="pokedex",
                )
                return
            pokedex = text.split(None, 1)[1].strip()
            Pokedex = await pokedexinfo(answers, pokedex)
            await client.answer_inline_query(query.id, results=Pokedex, cache_time=2)
        elif text.split()[0] == "paste":
            tex = text.split(None, 1)[1]
            answerss = await paste_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "fakegen":
            results = []
            fake = Faker()
            name = str(fake.name())
            fake.add_provider(internet)
            address = str(fake.address())
            ip = fake.ipv4_private()
            cc = fake.credit_card_full()
            email = fake.ascii_free_email()
            job = fake.job()
            android = fake.android_platform_token()
            pc = fake.chrome()
            res = f"<b><u> Fake Information Generated</b></u>\n<b>Name :-</b><code>{name}</code>\n\n<b>Address:-</b><code>{address}</code>\n\n<b>IP ADDRESS:-</b><code>{ip}</code>\n\n<b>credit card:-</b><code>{cc}</code>\n\n<b>Email Id:-</b><code>{email}</code>\n\n<b>Job:-</b><code>{job}</code>\n\n<b>android user agent:-</b><code>{android}</code>\n\n<b>Pc user agent:-</b><code>{pc}</code>"
            results.append(
                InlineQueryResultArticle(
                    title="Fake infomation gathered",
                    description="Click here to see them",
                    input_message_content=InputTextMessageContent(
                        res, parse_mode="HTML", disable_web_page_preview=True
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "image":
            if len(text.split()) < 2:
                return await client.answer_inline_query(
                    query.id,
                    results=answers,
                    is_gallery=True,
                    switch_pm_text="Image Search | image [QUERY]",
                    switch_pm_parameter="inline",
                )
            tex = text.split(None, 1)[1].strip()
            answerss = await image_func(answers, tex)
            await client.answer_inline_query(
                query.id, results=answerss, cache_time=3600
            )

        elif text.split()[0] == "exec":
            await execute_code(query)

        elif text.strip() == "tasks":
            user_id = query.from_user.id
            answerss = await task_inline_func(user_id)
            await client.answer_inline_query(query.id, results=answerss, cache_time=1)

    except Exception as e:
        e = traceback.format_exc()
        print(e, " InLine")
