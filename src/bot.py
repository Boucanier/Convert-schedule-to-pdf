import discord, scraper, toXLSX, toPDF, time, elementSchedule, dbOperations
from discord.ext import tasks, commands

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

toPing = '<@&1185252532717637682>'
defaultGroup = 'IUT'
precisedGroup = 'INF2-FI-A'
defaultChannel = 1185252325170892891

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=5)
async def refresh_db():
    message_channel = bot.get_channel(defaultChannel)
    print(f"Got channel {message_channel}")
    IUTurl, IUTtitle = scraper.getLink(True, "IUT")
    allCourse, weekDesc = elementSchedule.getFullSchedule(IUTurl, IUTtitle)
    dbOperations.overwriteDB(allCourse, weekDesc)
    print(f'Got schedule {defaultGroup} at {time.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]", time.localtime())}\n')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    refresh_db.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!edt '):
        print(f'\n{message.author} asked for staff schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

        if len(message.content.split(' ')) != 3 :
            print(f'{message.author} asked a wrong request ({message.content}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
            await message.channel.send(content = f'Veuillez préciser le type de l\'élément (staff ou room) et l\'élément en question')
            return
        
        if message.content.split(' ')[1] not in ['staff', 'room'] :
            print(f'{message.author} asked a wrong request ({message.content}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
            await message.channel.send(content = f'Élément indisponible, veuillez choisir entre **staff** et **room**')
            return

        type = message.content.split(' ')[1]
        element = message.content.split(' ')[2]

        courseList, weekDesc = dbOperations.getCourseByElement(type, element)

        courseList = elementSchedule.checkEquals(courseList)
        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent)
        toPDF.convertToPdf("schedule.xlsx", False)

        if type == 'staff' :
            await message.channel.send(content = f'Voici l\'emploi de {courseList[0][0].profContent} :', file = discord.File('schedule.pdf'))
        
        elif type == 'room' :
            await message.channel.send(content = f'Voici l\'emploi de la salle {courseList[0][0].roomContent} :', file = discord.File('schedule.pdf'))


    elif message.content.startswith('!edt'):
        print(f'\n{message.author} asked for schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
        
        url, title = scraper.getLink(True, precisedGroup)
        response = scraper.getSchedule(url)
        courseList, weekDesc = scraper.parseSchedule(response)
        courseList, overCourse = scraper.sortCourse(courseList)

        toXLSX.createXlsx(courseList, overCourse, weekDesc, title)
        toPDF.convertToPdf("schedule.xlsx", False)

        await message.channel.send(content = f'Voici l\'emploi du temps du groupe {precisedGroup} :', file = discord.File('schedule.pdf'))
    
    else :
        await message.channel.send(content = f'***{message.author}***, tu racontes quoi mon reuf ?!')


bot.run(token)