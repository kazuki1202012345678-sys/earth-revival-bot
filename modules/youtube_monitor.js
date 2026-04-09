const Parser = require('rss-parser');
const parser = new Parser();
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const CHANNEL_ID = 'UC-_M1D2hCFVUi_sLdc-0W-Q';
const RSS_URL = `https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}`;
const COMMUNITY_URL = `https://www.youtube.com/channel/${CHANNEL_ID}/community`;
const DATA_PATH = path.join(__dirname, '../data/last_update.json');
const UPDATE_CHANNEL_ID = '1374191294892736512';

async function checkYouTube(client) {
      console.log('[YOUTUBE] Checking updates...');
      let lastData = { lastVideoId: '', lastPostId: '' };
      if (fs.existsSync(DATA_PATH)) {
                try { lastData = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8')); } catch (e) {}
      }
      const channel = await client.channels.fetch(UPDATE_CHANNEL_ID).catch(() => null);
      if (!channel) return;
      await checkVideos(channel, lastData);
      await checkCommunity(channel, lastData);
      fs.writeFileSync(DATA_PATH, JSON.stringify(lastData, null, 2));
}

async function checkVideos(channel, lastData) {
      try {
                const feed = await parser.parseURL(RSS_URL);
                if (!feed.items || feed.items.length === 0) return;
                const latestVideo = feed.items[0];
                const latestId = latestVideo.id.split(':').pop();
                if (!lastData.lastVideoId) { lastData.lastVideoId = latestId; return; }
                if (lastData.lastVideoId !== latestId) {
                              await channel.send({ content: `New Video: ${latestVideo.title}\n${latestVideo.link}` });
                              lastData.lastVideoId = latestId;
                }
      } catch (e) {}
}

async function checkCommunity(channel, lastData) {
      try {
                const response = await axios.get(COMMUNITY_URL, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 });
                const match = response.data.match(/var ytInitialData = (.*?);<\/script>/);
                if (!match) return;
                const data = JSON.parse(match[1]);
                const tabs = data.contents?.twoColumnBrowseResultsRenderer?.tabs;
                const communityTab = tabs.find(t => t.tabRenderer && (t.tabRenderer.title === 'Community' || t.tabRenderer.selected));
                const items = communityTab?.tabRenderer?.content?.sectionListRenderer?.contents?.[0]?.itemSectionRenderer?.contents;
                if (!items) return;
                const latestPost = items[0].backstagePostRenderer || items[0].sharedPostRenderer;
                if (!latestPost) return;
                const postId = latestPost.postId;
                if (!lastData.lastPostId) { lastData.lastPostId = postId; return; }
                if (lastData.lastPostId !== postId) {
                              await channel.send({ content: `New Post: https://www.youtube.com/post/${postId}` });
                              lastData.lastPostId = postId;
             
                    } catch (e) {}
                    }
module.exports = { checkYouTube };
                    }
      } catc
