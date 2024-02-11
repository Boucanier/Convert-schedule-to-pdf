import discord, time, json
from discord.ext import tasks, commands
from datetime import date, timedelta, datetime
from functions import toPDF, toXLSX, scraper, elementSchedule, dbOperations, drawing

with open('config/token.json', 'r') as fl :
    token = json.load(fl)['token']

with open('config/bot_config.json', 'r') as fl :
    obj = json.load(fl)
    TO_PING = obj['to_ping']
    DEFAULT_GROUP = obj['default_group']
    PRECISED_GROUP = obj['precised_group']
    DEFAULT_CHANNEL = int(obj['default_channel'])
    OUTPUT_DIR = obj['output_dir']
    SEND_TIME = obj['send_time']


def byGroupSchedule(group : str, toDate : date = date.today(), short : bool = False) :
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
        print(f'Found {group} as group')

        if not short :
            toPDF.clearFiles(OUTPUT_DIR, 'xlsx', 'pdf', 'png')
            
            toXLSX.createXlsx(courseList, overCourse, weekDesc, title, OUTPUT_DIR + group.replace(' ', '_'))
            toPDF.convertToPdf(OUTPUT_DIR + group.replace(' ', '_') + '.xlsx', False)

        elif short :
            drawing.createScheduleImage(courseList, weekDesc, OUTPUT_DIR + group.replace(' ', '_'), toDate)

        return group
    
    else :
        print(f'Group {group} not found')
        NoGroup = None
    
    return NoGroup


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def schedule_img() -> None:
    """
        Create the schedule image of the default precised group and send it to the default channel

        - Args :
            - None

        - Returns :
            - None
    """
    days = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
    tmDate = date.today() + timedelta(days = 1)
    byGroupSchedule(PRECISED_GROUP, tmDate, short = True)
    message_channel = bot.get_channel(DEFAULT_CHANNEL)
    await message_channel.send(content = f'Voici l\'emploi du temps du groupe ***{PRECISED_GROUP}*** pour **{days[tmDate.weekday()]} {tmDate.strftime("%d/%m/%Y")}** :', file = discord.File(OUTPUT_DIR + PRECISED_GROUP + '.png')) # type: ignore
    print(f'Sent image schedule at {time.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]", time.localtime())}\n')


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

    if SEND_TIME[0] == int(time.strftime("%H", time.localtime())) and abs(SEND_TIME[1] - int(time.strftime("%M", time.localtime()))) < 5 :
        await schedule_img()


@bot.event
async def on_ready() -> None:
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

                if element.upper() == 'AMPHI A' :
                    element = 'Amphi  A'
                
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
                if message.content in ('!edt', '!edt today', '!edt td', '!edt tomorrow', '!edt tm') :
                    element = PRECISED_GROUP
                else :
                    element = message.content.split(' ')[1]

                print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')
                
                if message.content in ('!edt today', '!edt td') :
                    confGroup = byGroupSchedule(element, short = True)
                elif message.content in ('!edt tomorrow', '!edt tm') :
                    confGroup = byGroupSchedule(element, toDate = date.today() + timedelta(days = 1) ,short = True)
                else :
                    confGroup = byGroupSchedule(element)

                if confGroup :
                    if message.content in ('!edt today', '!edt td', '!edt tomorrow', '!edt tm') :
                        await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :', file = discord.File(OUTPUT_DIR + element + '.png'))
                    else :
                        await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :', file = discord.File(OUTPUT_DIR + element + '.pdf'))

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
                
                toPDF.clearFiles(OUTPUT_DIR, 'xlsx', 'pdf')

                if type[cpt] == 'staff' :
                    if dbOperations.countElement('staff', element) > 1 :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent.split(" ")[0], OUTPUT_DIR + element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps des ***{element}*** :'
                    else :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].profContent, OUTPUT_DIR + element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps de ***{courseList[0][0].profContent.split(",")[0]}*** :'
                
                elif type[cpt] == 'room' :
                    if dbOperations.countElement('room', element) > 1 :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent.split(" ")[0], OUTPUT_DIR + element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps des ***salles {element}*** :'
                    else :
                        toXLSX.createXlsx(courseList, overCourse, weekDesc, courseList[0][0].roomContent, OUTPUT_DIR + element.replace(' ', '_'))
                        toSendMsg = f'Voici l\'emploi du temps de la ***salle {courseList[0][0].roomContent.split(",")[0]}*** :'

                toPDF.convertToPdf(OUTPUT_DIR + element.replace(' ', '_') + '.xlsx', False)
                await message.channel.send(content = toSendMsg, file = discord.File(OUTPUT_DIR + element.replace(' ', '_') + '.pdf'))
            
            elif not confGroup and not courseList :
                print(f'Element {element} not found')
                await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')

        else :
            await message.channel.send(content = f'***{message.author.mention}***, tu racontes quoi mon reuf ?!')


if __name__ == "__main__" :
    bot.run(token)