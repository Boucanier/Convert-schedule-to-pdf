import time
import json
from datetime import date, timedelta
import discord
from discord.ext import tasks, commands
from functions import db_operations, element_schedule, to_pdf, to_xlsx, scraper, drawing

with open('config/token.json', 'r', encoding="utf-8") as fl :
    token = json.load(fl)['token']

with open('config/bot_config.json', 'r', encoding="utf-8") as fl :
    obj = json.load(fl)
    TO_PING = obj['to_ping']
    DEFAULT_GROUP = obj['default_group']
    PRECISED_GROUP = obj['precised_group']
    DEFAULT_CHANNEL = int(obj['default_channel'])
    OUTPUT_DIR = obj['output_dir']
    SEND_TIME = obj['send_time']


def by_group_schedule(group : str, to_date : date = date.today(), short : bool = False) :
    """
        Get the schedule of a given group if it exists

        - Args :
            - message (discord.Message) : message that triggered the function

        - Returns :
            - group (str) : name of the group to get schedule from (None if group does not exist)
    """
    url, title = scraper.get_link(True, group.upper())

    # If the group exists
    if url is not None and title is not None :
        response = scraper.get_schedule(url)
        course_list, week_desc = scraper.parse_schedule(response)
        course_list, over_course = scraper.sort_sourse(course_list)
        print(f'Found {group} as group')

        if not short :
            to_pdf.clear_files(OUTPUT_DIR, 'xlsx', 'pdf', 'png')

            to_xlsx.create_xlsx(course_list,
                                over_course,
                                week_desc,
                                title,
                                OUTPUT_DIR + group.replace(' ', '_'))

            to_pdf.convert_to_pdf(OUTPUT_DIR + group.replace(' ', '_') + '.xlsx', False)

        elif short :
            drawing.create_schedule_image(course_list,
                                          week_desc,
                                          OUTPUT_DIR + group.replace(' ', '_'),
                                          to_date)

        return group

    print(f'Group {group} not found')

    return None


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def schedule_img() -> None :
    """
        Create the schedule image of the default precised group and send it to the default channel

        - Args :
            - None

        - Returns :
            - None
    """
    days = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
    tm_date = date.today() + timedelta(days = 1)
    by_group_schedule(PRECISED_GROUP, tm_date, short = True)
    message_channel = bot.get_channel(DEFAULT_CHANNEL)
    await message_channel.send(content = f'Voici l\'emploi du temps du groupe ***{PRECISED_GROUP}*** pour **{days[tm_date.weekday()]} {tm_date.strftime("%d/%m/%Y")}** :', # type: ignore
                               file = discord.File(OUTPUT_DIR + PRECISED_GROUP + '.png'))
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
    iut_url, iut_title = scraper.get_link(True, "IUT")
    all_course, week_desc = element_schedule.get_full_schedule(iut_url, iut_title)
    db_operations.overwrite_db(all_course, week_desc)
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
        if len(message.content) >= 4\
            and len(message.content.split(' ')) <= 3\
            and message.content.split(' ')[0] == '!edt':

            week_desc = []
            course_list = None
            filter_type = ['staff', 'staff', 'room', 'room']
            cpt = 0
            conf_group = False

            if len(message.content.split(' ')) == 3 :
                element = message.content.split(' ')[1] + ' ' + message.content.split(' ')[2]

                if element.upper() == 'AMPHI A' :
                    element = 'Amphi  A'

                print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

                while (not course_list) and (cpt < 4) :
                    course_list, week_desc = db_operations.get_course_by_element(filter_type[cpt], element)

                    if not course_list :
                        element = element.split(' ')[1] + ' ' + element.split(' ')[0]
                        cpt += 1
                        if cpt == 2 :
                            print(f'Staff {element} not found')
                        elif cpt == 4 :
                            print(f'Room {element} not found')
                    else :
                        print(f'Found {element} as {filter_type[cpt]}')

            else :
                if message.content in ('!edt',
                                       '!edt today',
                                       '!edt td',
                                       '!edt tomorrow',
                                       '!edt tm') :
                    element = PRECISED_GROUP
                else :
                    element = message.content.split(' ')[1]

                print(f'\n{message.author} asked for schedule ({element.replace(" ", "_")}) at {message.created_at.strftime(r"%H:%M.%S on %d/%m/%Y [ %Z ]")}\n')

                if message.content in ('!edt today', '!edt td') :
                    conf_group = by_group_schedule(element, short = True)
                elif message.content in ('!edt tomorrow', '!edt tm') :
                    conf_group = by_group_schedule(element,
                                                   to_date = date.today() + timedelta(days = 1),
                                                   short = True)
                else :
                    conf_group = by_group_schedule(element)

                if conf_group :
                    if message.content in ('!edt today', '!edt td', '!edt tomorrow', '!edt tm') :
                        await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :',
                                                   file = discord.File(OUTPUT_DIR + element + '.png'))
                    else :
                        await message.channel.send(content = f'Voici l\'emploi du temps du groupe ***{element}*** :',
                                                   file = discord.File(OUTPUT_DIR + element + '.pdf'))

                else :
                    while (not course_list) and (cpt < 2) :
                        course_list, week_desc = db_operations.get_course_by_element(filter_type[cpt * 2], element)

                        if not course_list :
                            cpt += 1
                            if cpt == 1 :
                                print(f'Staff {element} not found')
                            elif cpt == 2 :
                                print(f'Room {element} not found')
                        else :
                            print(f'Found {element} as {filter_type[cpt]}')
                            cpt *= 2

            if course_list :
                to_send_msg = None
                course_list = element_schedule.check_equals(course_list)
                course_list, over_course = scraper.sort_sourse(course_list)

                to_pdf.clear_files(OUTPUT_DIR, 'xlsx', 'pdf')

                if filter_type[cpt] == 'staff' :
                    if db_operations.count_element('staff', element) > 1 :
                        to_xlsx.create_xlsx(course_list,
                                            over_course,
                                            week_desc,
                                            course_list[0][0].prof_content.split(" ")[0],
                                            OUTPUT_DIR + element.replace(' ', '_'))
                        to_send_msg = f'Voici l\'emploi du temps des ***{element}*** :'

                    else :
                        to_xlsx.create_xlsx(course_list,
                                            over_course,
                                            week_desc,
                                            course_list[0][0].prof_content,
                                            OUTPUT_DIR + element.replace(' ', '_'))
                        to_send_msg = f'Voici l\'emploi du temps de ***{course_list[0][0].prof_content.split(",")[0]}*** :'

                elif filter_type[cpt] == 'room' :
                    if db_operations.count_element('room', element) > 1 :
                        to_xlsx.create_xlsx(course_list,
                                            over_course,
                                            week_desc,
                                            course_list[0][0].room_content.split(" ")[0],
                                            OUTPUT_DIR + element.replace(' ', '_'))
                        to_send_msg = f'Voici l\'emploi du temps des ***salles {element}*** :'

                    else :
                        to_xlsx.create_xlsx(course_list, over_course,
                                            week_desc, course_list[0][0].room_content,
                                            OUTPUT_DIR + element.replace(' ', '_'))
                        to_send_msg = f'Voici l\'emploi du temps de la ***salle {course_list[0][0].room_content.split(",")[0]}*** :'

                to_pdf.convert_to_pdf(OUTPUT_DIR + element.replace(' ', '_') + '.xlsx', False)
                await message.channel.send(content = to_send_msg,
                                           file = discord.File(OUTPUT_DIR + element.replace(' ', '_') + '.pdf'))

            elif not conf_group and not course_list :
                print(f'Element {element} not found')
                await message.channel.send(content = f'***{message.author.mention}*** : élément **{element}** introuvable')

        else :
            await message.channel.send(content = f'***{message.author.mention}***, tu racontes quoi mon reuf ?!')


if __name__ == "__main__" :
    bot.run(token)
