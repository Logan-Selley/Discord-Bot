var Discord = require('discord.io');
var axios = require('axios');
var logger = require('winston');
var auth = require('./auth.json');
var ytpl = require('ytpl');
const { YTSearcher } = require('ytsearcher');
var spotify = require('node-spotify-api');
const fs = require('fs');
const ytdl = require('ytdl-core');


// logger settings
logger.remove(logger.transports.Console);
logger.add(new logger.transports.Console, {
    colorize: true
});
logger.level = 'debug';
// init discord bot

var bot = new Discord.Client({
    token: auth.token,
    autorun: true
});
bot.on('ready', function(evt) {
    logger.info('Connected');
    logger.info('Logged in as: ')
    logger.info(bot.username+'-('+bot.id+')');
});

bot.on('message', function(user, userID, channelID, message, evt){
    if(message.substring(0,1)=='!'){
        var args = message.substring(1).split('');
        var cmd = args[0];

        args=args.splice(1);
        switch(cmd){
            //!ping
            case 'ping':
                bot.sendMessage({
                    to:ChannelSplitterNode,
                    message:'Pong!'
                });

            // Spotify API

            //!play[link / search] / !p
            //!queue / !q
            //!skip / !s
            //!back / !b
            //!clear / !c
            //!jump[track position/title] /!j
            //!loop / !l
            //!lyrics / !ly / !lyrics[query]
            //!pause / !ps
            //!resume / !r
            //!remove[track position or title] / !re
            //!removerange[start], [end] / !rr
            //!reset
            //!shuffle / !sh
            //!song / !nowplaying / !np !song[song]
            //!volume[new volume] / !v
            //!search[queury] / !se
            //!stop / !st
            //!seek[position]
            //!playlist[name] / !pl


            //!prefix / !prefix[new prefix]
            //!perms[role/user]
            //!commands / !co
            break
        }
    }
});
