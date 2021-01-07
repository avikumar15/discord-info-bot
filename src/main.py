import os

import discord
from mongo import MongoHelper
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from discord.ext import tasks

print(os.getcwd())
mongoHelper = MongoHelper("infoDB")
collectionName = 'events'
token = open("../token.txt", "r").read()
client = discord.Client()
sched = BackgroundScheduler()
sched.start()

CHANNEL_ID = 796111099548270635


def schedule_alerts(event):
    date = event["deadline"]
    sched.add_job(func=send_alert, trigger='date', next_run_time=date - datetime.timedelta(minutes=5),
                  args=[":bangbang: 5 minutes left\n" + get_event_description(event)])
    sched.add_job(func=send_alert, trigger='date', next_run_time=date - datetime.timedelta(minutes=30),
                  args=[":bangbang: 30 minutes left\n" + get_event_description(event)])
    sched.add_job(func=send_alert, trigger='date', next_run_time=date - datetime.timedelta(hours=1),
                  args=[":bangbang: 1 hour left\n" + get_event_description(event)])
    sched.add_job(func=send_alert, trigger='date', next_run_time=date - datetime.timedelta(hours=6),
                  args=[":bangbang: 6 hours left\n" + get_event_description(event)])
    sched.add_job(func=send_alert, trigger='date', next_run_time=date - datetime.timedelta(days=1),
                  args=[":bangbang: 1 day left\n" + get_event_description(event)])
    print(date)


def send_alert(message):
    asyncio.run_coroutine_threadsafe(send_message(message), client.loop)


def get_event_description(event: dict):
    event_description = "-------------------------------------------------\n"
    event_description += f"Category: {event['category']}\n"
    event_description += f"Sub-category: {event['sub-category']}\n"
    event_description += f"Description: {event['description']}\n"
    event_description += f"Name: {event['name']}\n"
    event_description += f"Type: {event['type']}\n"
    event_description += f"Deadline: {event['deadline'].strftime('%d/%m/%Y')}\n"
    event_description += "-------------------------------------------------\n"
    return event_description


async def send_message(message):
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(message)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    delete_old_events.start()


@client.event
async def on_message(ctx):
    if ctx.author == client.user:
        return

    if ctx.channel.id != CHANNEL_ID:
        return

    if str(ctx.content) == "!help":
        help_string = "To add an event, type\n" \
               "'!add category,sub-category,description,name,type,dd.mm.yyyy.hh.mm'\n" \
               "To view all events, type\n" \
               "'!show'"
        ctx.channel.send(help_string)

    if str(ctx.content).startswith("!add "):
        event_info = str(ctx.content).split("!add ", 1)[1]
        event_info = event_info.split(",")
        if len(event_info) < 6:
            await ctx.channel.send("Enter a valid add event message!")
            return
        try:
            date_string = list(map(int, event_info[5].split(".")))
            date = datetime.datetime(day=date_string[0], month=date_string[1], year=date_string[2],
                                     hour=date_string[3], minute=date_string[4])
            print(date)
        except:
            await ctx.channel.send("Enter a valid date (ex: 07.01.2021.06.30)")
        event = {"category": event_info[0],
                 "sub-category": event_info[1],
                 "description": event_info[2],
                 "name": event_info[3],
                 "type": event_info[4],
                 "deadline": date}
        schedule_alerts(event)
        mongoHelper.insertOne(collectionName, event)
        await ctx.channel.send("Event Added! :white_check_mark:")

    if str(ctx.content).startswith("!show"):
        upcoming_events = mongoHelper.findMany(collectionName, {})
        for event in upcoming_events:
            await ctx.channel.send(get_event_description(event))


@tasks.loop(hours=24)
async def delete_old_events():
    mongoHelper.deleteEventsBefore(collectionName, datetime.datetime.now())


client.run(token)
