import aiohttp
import json
import os
import re
from datetime import datetime
import discord
from bs4 import BeautifulSoup

CHANNEL_ID = 'UC-_M1D2hCFVUi_sLdc-0W-Q'
RSS_URL = f'https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}'
COMMUNITY_URL = f'https://www.youtube.com/channel/{CHANNEL_ID}/community'
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/last_update.json')
UPDATE_CHANNEL_ID = 1374191294892736512

async def check_youtube(bot):
      print('[YOUTUBE] Checking for updates...')

    last_data = {'lastVideoId': '', 'lastPostId': ''}
    if os.path.exists(DATA_PATH):
              try:
                            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                                              last_data = json.load(f)
                                      except: pass

          channel = bot.get_channel(UPDATE_CHANNEL_ID)
    if not channel:
              try:
                            channel = await bot.fetch_channel(UPDATE_CHANNEL_ID)
                        except:
            print(f'[YOUTUBE] Error: Channel {UPDATE_CHANNEL_ID} not found.')
            return

    async with aiohttp.ClientSession() as session:
              await check_videos(session, channel, last_data)
        await check_community(session, channel, last_data)

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
              json.dump(last_data, f, indent=2)

async def check_videos(session, channel, last_data):
      try:
                async with session.get(RSS_URL, timeout=10) as resp:
                              xml = await resp.text()
                              video_ids = re.findall(r'<yt:videoId>(.*?)</yt:videoId>', xml)
                              titles = re.findall(r'<title>(.*?)</title>', xml)

            if not video_ids: return

            latest_id = video_ids[0]
            latest_title = titles[1] if len(titles) > 1 else "Unknown Title"

            if not last_data.get('lastVideoId'):
                              last_data['lastVideoId'] = latest_id
                              return

            if last_data['lastVideoId'] != latest_id:
                              print(f'[YOUTUBE] New video: {latest_title}')
                              await channel.send(
                                  content=f"New YouTube Video!\n\n**{latest_title}**\nhttps://www.youtube.com/watch?v={latest_id}"
                              )
                              last_data['lastVideoId'] = latest_id
                  except: pass

async def check_community(session, channel, last_data):
      headers = {'User-Agent': 'Mozilla/5.0'}
    try:
              async with session.get(COMMUNITY_URL, headers=headers, timeout=10) as resp:
                            html = await resp.text()
                            match = re.search(r'var ytInitialData = (.*?);</script>', html)
                            if not match: return
                                          data = json.loads(match.group(1))
            tabs = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
               community_tab = next((t for t in tabs if t.get('tabRenderer', {}).get('title') in ['Community', 'Community Tab']), None)
            if not community_tab: return
                          content = community_tab['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]
            post_renderer = content.get('backstagePostRenderer') or content.get('sharedPostRenderer')
            if not post_renderer: return
                          post_id = post_renderer['postId']
            runs = post_renderer.get('contentText', {}).get('runs', [])
            text = "".join([r['text'] for r in runs])
            if not last_data.get('lastPostId'):
                              last_data['lastPostId'] = post_id
                              return
                          if last_data['lastPostId'] != post_id:
                                            print(f'[YOUTUBE] New community post: {post_id}')
                                            summary = text[:500] + ('...' if len(text) > 500 else '')
                                            await channel.send(
                                                content=f"New YouTube Community Post!\n\n{summary}\n\nhttps://www.youtube.com/post/{post_id}"
                                            )
                                            last_data['lastPostId'] = post_id
                                except: pass
