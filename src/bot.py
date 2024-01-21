import discord, scraper, toXLSX, toPDF, time, elementSchedule, dbOperations
from discord.ext import tasks, commands

with open('data/token.txt', 'r') as fl :
    token = fl.readline()

TO_PING = '<@&1185252532717637682>'
DEFAULT_GROUP = 'IUT'
PRECISED_GROUP = 'INF2-FI-A'
DEFAULT_CHANNEL = 1185252325170892891


def byGroupSchedule(group : str) :
    """
        Get the schedule of a given group if it exists

        - Args :
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
        NoGroup = None
    
    return NoGroup


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=5)
async def refresh_db() -> None:
    """
        Refresh the database every 5 minutes

        - Args :
            - None

        - Returns :
            - None
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
async def on_message(message : discord.Message) -> None :
    """
        Triggered when a message is sent in a channel

        - Args :
            - message (discord.Message) : message that triggered the function

        - Returns :
            - None
    """
    if message.author == bot.user:
        return
    
    if message.content.startswith('!edt'):
        if len(message.content) >= 4 and len(message.content.split(' ')) <= 3 and message.content.split(' ')[0] == '!edt':
            weekDesc = list()
            courseList = None
            type = ['staff', 'staff', 'room', 'room']
            cpt = 0
            confGroup = False

            if len(message.content.split(' ')) == 3 :
                element = message.content.split(' ')[1] + ' ' + message.content.split(' ')[2]
                
                print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

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
            
            else :
                if message.content == '!edt' :
                    element = PRECISED_GROUP
                else :
                    element = message.content.split(' ')[1]

                print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
                
                confGroup = byGroupSchedule(element)

                if confGroup :
                    await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :', file = discord.File(element + '.pdf'))

                else :
                    while (not courseList) and (cpt < 2) :
                        courseList, weekDesc = dbOperations.getCourseByElement(type[cpt * 2], element)
                        
                        if not courseList :
                            cpt += 1
                            if cpt == 1 :
                                print(f'Staff {element} not found')
                            elif cpt == 2 :
                                print(f'Room {element} not found')
                        else :
                            print(f'Found {element} as {type[cpt]}')
                            cpt *= 2

            if courseList :
                toSendMsg = None
                courseList = elementSchedule.checkEquals(courseList)
                courseList, overCourse = scraper.sortCourse(courseList)
                
                scraper.clearFiles()

                if type[cpt] == 'staff' :
                    if dbOperations.countElement('staff', element) > 1 :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent.split(" ")[0], element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps des ***{element}*** :'
                    else :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent, element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps de ***{courseList[0][0].profContent.split(",")[0]}*** :'
                
                elif type[cpt] == 'room' :
                    if dbOperations.countElement('room', element) > 1 :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent.split(" ")[0], element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps des ***salles {element}*** :'
                    else :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent, element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps de la ***salle {courseList[0][0].roomContent.split(",")[0]}*** :'

                toPDF.convertToPdf(element.replace(' ', '_') + '.xlsx', False)
                await message.channel.send(content = toSendMsg, file = discord.File(element.replace(' ', '_') + '.pdf'))
            
            elif not confGroup and not courseList :
                print(f'Element {element} not found')
                await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')

        else :
            await message.channel.send(content = f'***{message.author.mention}***, tu racontes quoi mon reuf ?!')


bot.run(token)