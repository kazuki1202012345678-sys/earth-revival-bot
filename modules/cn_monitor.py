import os
import aiohttp
import json
import re
from datetime import datetime
import google.generativeai as genai
import discord

# Constants
OFFICIAL_BILIBILI_MID = '1943410799'
OFFICIAL_WEIBO_UID = '7566510819'
WEIBO_CONTAINER_ID = '1076037566510819'

LEAKER_MIDS = [
      '2076169472',
      '527002336',
      '10468087'
]

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/cn_sns_state.json')
SUMMARY_CHANNEL_NAME = 'cn-news'

# Gemini Setup
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

async def check_chinese_sns(bot, force=False):
      print('[CN_SNS] Updating Chinese SNS info...')
      state = {'lastBiliId': '', 'lastWeiboId': '', 'lastLeakerIds': {}}
      if os.path.exists(DATA_PATH):
                try:
                              with open(DATA_PATH, 'r', encoding='utf-8') as f:
                                                state = json.load(f)
                                                if 'lastLeakerIds' not in state: state['lastLeakerIds'] = {}
                                                          except: pass
                                                                updates = []
            async with aiohttp.ClientSession() as session:
                      bili_post = await fetch_bilibili(session, OFFICIAL_BILIBILI_MID)
                      if bili_post and (force or bili_post['id'] != state['lastBiliId']):
                                    result = await summarize_with_gemini(bili_post['text'], 'Official Bilibili')
                                    updates.append({'source': 'Official Bilibili', **result, 'link': bili_post['link']})
                                    state['lastBiliId'] = bili_post['id']
                                weibo_post = await fetch_weibo(session)
        if weibo_post and (force or weibo_post['id'] != state['lastWeiboId']):
                      result = await summarize_with_gemini(weibo_post['text'], 'Official Weibo')
            updates.append({'source': 'Official Weibo', **result, 'link': weibo_post['link']})
            state['lastWeiboId'] = weibo_post['id']
        for mid in LEAKER_MIDS:
                      post = await fetch_bilibili(session, mid)
            if post and (force or post['id'] != state['lastLeakerIds'].get(mid)):
                              result = await summarize_with_gemini(post['text'], 'Leak Info', is_leak=True)
                              updates.append({'source': 'Leak', **result, 'link': post['link']})
                              state['lastLeakerIds'][mid] = post['id']
                  if updates:
                            guild = bot.guilds[0]
                            channel = discord.utils.get(guild.channels, name=SUMMARY_CHANNEL_NAME)
                            if channel:
                                          for update in updates:
                                                            is_leak = update['source'] == 'Leak'
                                                            embed = discord.Embed(
                                                                title=f"CN Monitor ({update['source']})",
                                                                url=update['link'],
                                                                description=f"### Summary\n{update['summary']}",
                                                                color=0xcc00ff if is_leak else 0xff4500,
                                                                timestamp=datetime.now()
                                                            )
                                                            if update['rumors']:
                                                                embed.add_field(name='Rumors', value=update['rumors'], inline=False)
                                                                              await channel.send(embed=embed)
                                                                  if not force:
                                                                            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
                                                                            with open(DATA_PATH, 'w', encoding='utf-8') as f:
                                                                                          json.dump(state, f, indent=2)

                                                                    async def fetch_bilibili(session, mid):
                                                                          url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={mid}"
                                                                          headers = {
                                                                              'User-Agent': 'Mozilla/5.0',
                                                                              'Referer': f'https://space.bilibili.com/{mid}/dynamic'
                                                                          }
                                                                          try:
                                                                                    async with session.get(url, headers=headers, timeout=10) as resp:
                                                                                                  data = await resp.json()
                                                                                                  items = data.get('data', {}).get('items', [])
                                                                                                  if not items: return None
                                                                                                                latest = items[0]
                                                                                                  desc = latest.get('modules', {}).get('module_dynamic', {}).get('desc', {})
                                                                                                  major = latest.get('modules', {}).get('module_dynamic', {}).get('major', {})
                                                                                                  text = desc.get('text') or major.get('article', {}).get('desc') or major.get('archive', {}).get('title') or ""
                                                                                                  return {'id': latest['id_str'], 'text': text, 'link': f"https://t.bilibili.com/{latest['id_str']}"}
                                                                                          except: return None

                                                                      async def fetch_weibo(session):
                                                                            url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={OFFICIAL_WEIBO_UID}&containerid={WEIBO_CONTAINER_ID}"
                                                                            headers = {'User-Agent': 'Mozilla/5.0'}
                                                                            try:
                                                                                      async with session.get(url, headers=headers, timeout=10) as resp:
                                                                                                    data = await resp.json()
                                                                                                    cards = data.get('data', {}).get('cards', [])
                                                                                                    post_card = next((c for c in cards if c.get('card_type') == 9 and c.get('mblog')), None)
                                                                                                    if not post_card: return None
                                                                                                                  blog = post_card['mblog']
                                                                                                    text = re.sub(r'<[^>]+>', '', blog['text'])
                                                                                                    return {'id': blog['id'], 'text': text, 'link': f"https://weibo.com/{OFFICIAL_WEIBO_UID}/{blog['bid']}"}
                                                                                            except: return None

                                                                        async def summarize_with_gemini(text, source, is_leak=False):
                                                                              if not text: return {'summary': 'No info', 'rumors': ''}
                                                                                    prompt = f"Summarize this Chinese SNS post ({source}) about survival game Earth Revival. Use emojis. 1. Summary (3 points), 2. Rumors (1-2 points). Output: Summary: ... Rumors: ..."
                                                                              try:
                                                                                        response = await model.generate_content_async(prompt + f"\n\n{text}")
        full_text = response.text
        summary_match = re.search(r'Summary:\s*([\s\S]*?)(?=Rumors:|$)', full_text)
        rumors_match = re.search(r'Rumors:\s*([\s\S]*)', full_text)
        return {
                      'summary': summary_match.group(1).strip() if summary_match else full_text,
                      'rumors': rumors_match.group(1).strip() if rumors_match else ""
        }
    except: return {'summary': 'Error', 'rumors': ''}
