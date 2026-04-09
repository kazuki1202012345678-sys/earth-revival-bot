require('dotenv').config();
const { Client, Collection, Events, GatewayIntentBits } = require('discord.js');
const fs = require('node:fs');
const path = require('node:path');
const cron = require('node-cron');
const { checkYouTube } = require('./modules/youtube_monitor');
const { checkChineseSNS } = require('./modules/cn_sns_monitor');
const express = require('express');

const client = new Client({ 
                              intents: [
                                        GatewayIntentBits.Guilds,
                                        GatewayIntentBits.GuildMembers
                                    ] 
});

client.commands = new Collection();

const commandsPath = path.join(__dirname, 'commands');
if (fs.existsSync(commandsPath)) {
      const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
      for (const file of commandFiles) {
                const filePath = path.join(commandsPath, file);
                const command = require(filePath);
                if ('data' in command && 'execute' in command) {
                              client.commands.set(command.data.name, command);
                } else {
            console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
                }
      }
}

client.once(Events.ClientReady, c => {
      console.log(`Ready! Logged in as ${c.user.tag}`);

                checkYouTube(client);
      setInterval(() => checkYouTube(client), 1000 * 60 * 60);

                cron.schedule('0 8 * * *', () => {
                          const now = new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" });
                          console.log(`[${now}] CRON: Starting daily Chinese SNS summary...`);
                          checkChineseSNS(client).catch(err => {
                                        console.error(`[${now}] CRON ERROR:`, err);
                          });
                }, {
                          scheduled: true,
                          timezone: "Asia/Tokyo"
                });

                console.log('[SYSTEM] Automation scheduler is active (8:00 AM JST)');
});

client.on(Events.GuildMemberAdd, async member => {
      const configPath = path.join(__dirname, 'data/welcome_config.json');
      if (!fs.existsSync(configPath)) return;

              try {
                        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                        const channel = await member.guild.channels.fetch(config.channelId);

          if (channel) {
                        const welcomeMsg = config.message.replace('{user}', `<@${member.id}>`);
                        await channel.send(welcomeMsg);
                        console.log(`[WELCOME] Sent welcome message to ${member.user.tag}`);
          }
              } catch (error) {
                                                  console.error('[WELCOME] Error sending message:', error);
              }
                                     });

client.on(Events.InteractionCreate, async interaction => {
      if (!interaction.isChatInputCommand()) return;

              const command = interaction.client.commands.get(interaction.commandName);

              if (!command) {
                                  console.error(`No command matching ${interaction.commandName} was found.`);
                        return;
                            }

              try {
                        await command.execute(interaction);
              } catch (error) {
                        console.error(error);
                        if (interaction.replied || interaction.deferred) {
                                      await interaction.followUp({ content: 'There was an error while executing this command!', ephemeral: true });
                        } else {
              await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
                        }
              }
});

client.login(process.env.DISCORD_TOKEN);
