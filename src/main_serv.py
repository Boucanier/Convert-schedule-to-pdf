import discord
import time

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!edt'):
        time.sleep(10)
        await message.channel.send(content='Voici le dernier emploi du temps généré :', file=discord.File('schedule.pdf'))

client.run(token)