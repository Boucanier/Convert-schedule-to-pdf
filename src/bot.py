import discord, scraper, toXLSX, toPDF, time, elementSchedule, dbOperations
from discord.ext import tasks, commands

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

TO_PING = '<@&1185252532717637682>'
DEFAULT_GROUP = 'IUT'
PRECISED_GROUP = 'INF2-FI-A'
DEFAULT_CHANNEL = 1185252325170892891


def byGroupSchedule(group, message):
    """
        Get the schedule of a given group if it exists

        - Args :
            - group (str) : name of the group to get schedule from
            - message (discord.Message) : message that triggered the function

        - Returns :
            - group (str) : name of the group to get schedule from (None if group does not exist)
    """
    url, title = scraper.getLink(True, group.upper())

    # If the group exists
    if url != None and title != None :
        response = scraper.getSchedule(url)
        courseList, weekDesc = scraper.parseSchedule(response)
        courseList, overCourse = scraper.sortCourse(courseList)

        scraper.clearFiles()
        print(f'Found {group} as group') 
        toXLSX.createXlsx(courseList, overCourse, weekDesc, title, group.replace(' ', '_'))
        toPDF.convertToPdf(group.replace(' ', '_') + '.xlsx', False)

        return group
    
    else :
        print(f'Group {group} not found')
        group = None
    
    return group


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=5)
async def refresh_db():
    """
        Refresh the database every 5 minutes
    """
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

    if message.content.startswith('!edt') and len(message.content) >= 4 and len(message.content.split(' ')) <= 3 :

        # Staff or room schedule with 1 space in the name
        if len(message.content.split(' ')) == 3 :
            type = ['staff', 'staff', 'room', 'room']
            element = message.content.split(' ')[1] + ' ' + message.content.split(' ')[2]
            
            print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

            cpt = 0
            courseList = None

            while (not courseList) and (cpt < 4) :
                courseList, weekDesc = dbOperations.getCourseByElement(type[cpt], element)
            
                if not courseList :
                    element = element.split(' ')[1] + ' ' + element.split(' ')[0]
                    cpt += 1
                    if cpt == 2 :
                        print(f'Staff {element} not found')
                    elif cpt == 4 :
                        print(f'Room {element} not found')
                else :
                    print(f'Found {element} as {type[cpt]}')                


            if courseList :
                courseList = elementSchedule.checkEquals(courseList)
                courseList, overCourse = scraper.sortCourse(courseList)
                
                scraper.clearFiles()

                if type[cpt] == 'staff' :
                    toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent, element.replace(' ', '_'))
                    toPDF.convertToPdf(element.replace(' ', '_') + '.xlsx', False)
                    await message.channel.send(content = f'Voici l\'emploi du temps de ***{courseList[0][0].profContent}*** :', file = discord.File(element.replace(' ', '_') + '.pdf'))
                
                elif type[cpt] == 'room' :
                    toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent, element.replace(' ', '_'))
                    toPDF.convertToPdf(element.replace(' ', '_') + '.xlsx', False)
                    await message.channel.send(content = f'Voici l\'emploi du temps de la ***salle {courseList[0][0].roomContent}*** :', file = discord.File(element.replace(' ', '_') + '.pdf'))
            
            else :
                print(f'Element {element} not found')
                await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')


        # Group, staff or room schedule with no space in the name
        elif len(message.content.split(' ')) in (1, 2) :
            if message.content == '!edt' :
                element = PRECISED_GROUP
            else :
                element = message.content.split(' ')[1]

            print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
            
            confGroup = byGroupSchedule(element, message)

            if confGroup :
                await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :', file = discord.File(element + '.pdf'))

            else :
                type = ['staff', 'room']
                courseList = None
                
                cpt = 0
                while (not courseList) and (cpt < 2) :
                    courseList, weekDesc = dbOperations.getCourseByElement(type[cpt], element)
                    
                    if not courseList :
                        cpt += 1
                        if cpt == 1 :
                            print(f'Staff {element} not found')
                        elif cpt == 2 :
                            print(f'Room {element} not found')
                    else :
                        print(f'Found {element} as {type[cpt]}') 

                if courseList :
                    courseList = elementSchedule.checkEquals(courseList)
                    courseList, overCourse = scraper.sortCourse(courseList)

                    scraper.clearFiles()

                    if type[cpt] == 'staff' :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent, element)
                        toPDF.convertToPdf(element + '.xlsx', False)
                        await message.channel.send(content = f'Voici l\'emploi du temps de ***{courseList[0][0].profContent}*** :', file = discord.File(element + '.pdf'))

                    elif type[cpt] == 'room' :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent, element)
                        toPDF.convertToPdf(element + '.xlsx', False)
                        await message.channel.send(content = f'Voici l\'emploi du temps de la ***salle {courseList[0][0].roomContent}*** :', file = discord.File(element + '.pdf'))

                else :
                    await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')


    else :
        await message.channel.send(content = f'***{message.author.mention}***, tu racontes quoi mon reuf ?!')


bot.run(token)