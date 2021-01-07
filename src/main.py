import os

import discord
from mongo import MongoHelper
import datetime

print(os.getcwd())
mongoHelper = MongoHelper("infoDB")
collectionName = 'events'
token = open("../token.txt", "r").read()
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(ctx):
    if ctx.author == client.user:
        return

    if str(ctx.content).startswith("!add "):
        event_info = str(ctx.content).split("!add ", 1)[1]
        event_info = event_info.split(",")
        if len(event_info) < 6:
            await ctx.channel.send("Enter a valid add event message!")
            return
        try:
            date_string = list(map(int, event_info[5].split(".")))
            date = datetime.datetime(day=date_string[0], month=date_string[1], year=date_string[2])
            print(date)
        except:
            await ctx.channel.send("Enter a valid date (ex: 07.01.2021)")
        event = {"category": event_info[0],
                 "sub-category": event_info[1],
                 "description": event_info[2],
                 "name": event_info[3],
                 "type": event_info[4],
                 "deadline": date}
        mongoHelper.insertOne(collectionName, event)
        await ctx.channel.send("Event Added! :white_check_mark:")

    if str(ctx.content).startswith("!show"):
        upcoming_events = mongoHelper.findMany(collectionName, {})
        for event in upcoming_events:
            event_description = "-------------------------------------------------\n"
            event_description += f"Category: {event['category']}\n"
            event_description += f"Sub-category: {event['sub-category']}\n"
            event_description += f"Description: {event['description']}\n"
            event_description += f"Name: {event['name']}\n"
            event_description += f"Type: {event['type']}\n"
            event_description += f"Deadline: {event['deadline'].strftime('%d/%m/%Y')}\n"
            event_description += "-------------------------------------------------\n"
            await ctx.channel.send(event_description)


client.run(token)
