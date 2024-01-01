import discord, scraper, toXLSX, toPDF, time, elementSchedule, dbOperations, subprocess, platform
from discord.ext import tasks, commands

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

TO_PING = '<@&1185252532717637682>'
DEFAULT_GROUP = 'IUT'
PRECISED_GROUP = 'INF2-FI-A'
DEFAULT_CHANNEL = 1185252325170892891


def clearFiles() :
    if platform.system() == "Linux" :
        subprocess.run('rm *.pdf *.xlsx', shell = True)
    elif platform.system() == "Windows" :
        subprocess.run('del *.pdf *.xlsx', shell = True)


def byGroupSchedule(group, message):

    print(f'\n{message.author} asked for schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
    url, title = scraper.getLink(True, group)

    # If the group exist
    if url != None and title != None :
        response = scraper.getSchedule(url)
        courseList, weekDesc = scraper.parseSchedule(response)
        courseList, overCourse = scraper.sortCourse(courseList)

        clearFiles()

        toXLSX.createXlsx(courseList, overCourse, weekDesc, title, group.replace(' ', '_'))
        toPDF.convertToPdf(group.replace(' ', '_') + '.xlsx', False)

        return group
    
    else :
        print(f'Group {group} not found')
        return (url != None and title != None)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=5)
async def refresh_db():
    message_channel = bot.get_channel(DEFAULT_CHANNEL)
    print(f"Got channel {message_channel}")
    IUTurl, IUTtitle = scraper.getLink(True, "IUT")
    allCourse, weekDesc = elementSchedule.getFullSchedule(IUTurl, IUTtitle)
    dbOperations.overwriteDB(allCourse, weekDesc)
    print(f'Got schedule {DEFAULT_GROUP} at {time.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]", time.localtime())}\n')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    refresh_db.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!edt ') and len(message.content) > 5 :
        print(f'\n{message.author} asked for staff schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

        if len(message.content.split(' ')) == 2 :
            toFindGroup = message.content.split(' ')[1]
            
            byGroupSchedule(toFindGroup, message)
        
            confGroup = byGroupSchedule(toFindGroup, message)

            if confGroup :
                await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{toFindGroup}*** :', file = discord.File(toFindGroup + '.pdf'))

            else :
                await message.channel.send(content = f'***{message.author.mention}*** : groupe **{toFindGroup}** introuvable')


        elif (len(message.content.split(' ')) != 3) and not (message.content.split(' ')[1] == 'staff' and len(message.content.split(' ')) == 4) :
            print(f'{message.author} asked a wrong request ({message.content}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
            await message.channel.send(content = f'Veuillez préciser le type de l\'élément (staff ou room) et l\'élément en question')
            return
        

        elif message.content.split(' ')[1] not in ['staff', 'room'] :
            print(f'{message.author} asked a wrong request ({message.content}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
            await message.channel.send(content = f'Élément indisponible, veuillez choisir entre **staff** et **room**')
            return

        else :
            type = message.content.split(' ')[1]
            element = message.content.split(' ')[2]

            if len(message.content.split(' ')) == 4 :
                element += ' ' + message.content.split(' ')[3]

            courseList, weekDesc = dbOperations.getCourseByElement(type, element)
            
            if not courseList and len(message.content.split(' ')) == 4 :
                courseList, weekDesc = dbOperations.getCourseByElement(type, element.split(' ')[1] + ' ' + element.split(' ')[0])

            if courseList :
                courseList = elementSchedule.checkEquals(courseList)
                courseList, overCourse = scraper.sortCourse(courseList)
                
                clearFiles()

                toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent, element.replace(' ', '_'))
                toPDF.convertToPdf(element.replace(' ', '_') + '.xlsx', False)

                if type == 'staff' :
                    await message.channel.send(content = f'Voici l\'emploi de ***{courseList[0][0].profContent}*** :', file = discord.File(element.replace(' ', '_') + '.pdf'))
                
                elif type == 'room' :
                    await message.channel.send(content = f'Voici l\'emploi de la ***salle {courseList[0][0].roomContent}*** :', file = discord.File(element.replace(' ', '_') + '.pdf'))
            
            else :
                print(f'Element {element} not found')
                await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')


    elif message.content.startswith('!edt'):
        print(f'\n{message.author} asked for schedule at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
        
        confGroup = byGroupSchedule(PRECISED_GROUP, message)

        if confGroup :
            await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{PRECISED_GROUP}*** :', file = discord.File(PRECISED_GROUP.replace(' ', '_') + '.pdf'))

        else :
            await message.channel.send(content = f'***@{message.author}*** : groupe **{PRECISED_GROUP}*** introuvable')
    

    else :
        await message.channel.send(content = f'***{message.author.mention}***, tu racontes quoi mon reuf ?!')


bot.run(token)