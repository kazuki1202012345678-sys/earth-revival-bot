const axios = require('axios');
const { GoogleGenerativeAI } = require("@google/generative-ai");
const fs = require('fs');
const path = require('path');
require('dotenv').config();
const OFFICIAL_BILIBILI_MID = '1943410799'; 
const OFFICIAL_WEIBO_UID = '7566510819';    
const WEIBO_CONTAINER_ID = '1076037566510819';
const LEAKER_MIDS = ['2076169472', '527002336', '10468087'];
const DATA_PATH = path.join(__dirname, '../data/cn_sns_state.json');
const SUMMARY_CHANNEL_NAME = 'China_Updates';
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

async function checkChineseSNS(client) {
      console.log('[CN_SNS] Updating info...');
      let state = { lastBiliId: '', lastWeiboId: '', lastLeakerIds: {} };
      if (fs.existsSync(DATA_PATH)) {
                try { state = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8')); } catch (e) {}
      }
      console.log('[CN_SNS] Monitor active.');
      fs.writeFileSync(DATA_PATH, JSON.stringify(state, null, 2));
}
module.exports = { checkChineseSNS };
