import discord, scraper, toXLSX, toPDF

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

toPing = '<@&1185252532717637682>'
defaultGroup = 'INF2-FI-A'

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
        print(f'\n{message.author} asked for schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
        
        url, title = scraper.getLink(True, defaultGroup)
        response = scraper.getSchedule(url)
        courseList, weekDesc = scraper.parseSchedule(response)
        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, title)
        toPDF.convertToPdf("schedule.xlsx", False)

        await message.channel.send(content = f'{toPing}\nVoici l\'emploi du temps du groupe {defaultGroup} :', file = discord.File('schedule.pdf'))

client.run(token)