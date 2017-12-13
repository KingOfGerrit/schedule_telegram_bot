from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import os
import pytz
import logging
import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text(config.start_message)

def help(bot, update):
    update.message.reply_text(config.help_message)

# Europe/Kiev
# 0 - first
# 1 - second
def get_week():
    return 0 if ((datetime.now(pytz.timezone(config.timezone_c)).isocalendar()[1]) % 2 == 1) else 1

def get_schedule(week, day):
    """

    :param week: takes week 0 - first, 1 - second
    :param day: takes day 0 - monaday, 4 - friday
    :return: schedule

    """
    st = ''

    current_date = str(datetime.now(pytz.timezone(config.timezone_c)).date()).split('-')

    if datetime.now(pytz.timezone(config.timezone_c)).isoweekday() >= 5 and day != 4:
        week = 1 - week

    try:
        st += '<b>{} - {}:</b>\n'.format(config.days_list[day],
                                         ('1 ' + config.week_lang) if (week == 0) else ('2 ' + config.week_lang)
                                         )

        for i in config.schedule[week][day]:
            st += i + '\n'

        st += '\n\n<i>{}\n{}\n{} - {} ({}) - {}</i>'.format(config.today_lang,
                                                               config.days_list[int(datetime.now(pytz.timezone(config.timezone_c)).isoweekday()) - 1],
                                                               current_date[2],
                                                               current_date[1],
                                                               config.months_list[int(current_date[1]) - 1],
                                                               current_date[0]
                                                               )
    except IndexError:
        st = config.weekend_lang

        st += '<b>{} - {}:</b>\n'.format(config.days_list[0],
                                         ('1 ' + config.week_lang) if (week == 0) else ('2 ' + config.week_lang)
                                         )

        for i in config.schedule[week][0]:
            st += i + '\n'

        st += '\n\n<i>{}\n{}\n{} - {} ({}) - {}</i>'.format(config.today_lang,
                                                               config.days_list[int(datetime.now(pytz.timezone(config.timezone_c)).isoweekday()) - 1],
                                                               current_date[2],
                                                               current_date[1],
                                                               config.months_list[int(current_date[1]) - 1],
                                                               current_date[0]
                                                               )

    return st



# def test(bot, update):
#     keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
#                  InlineKeyboardButton("Option 2", callback_data='2')],

#                 [InlineKeyboardButton("Option 3", callback_data='3')]]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     update.message.reply_text('Please choose:', reply_markup=reply_markup)



def today(bot, update):
    update.message.reply_text(get_schedule(get_week(), datetime.now(pytz.timezone(config.timezone_c)).isoweekday() - 1), parse_mode=ParseMode.HTML)

def tomorrow(bot, update):
    t = datetime.now(pytz.timezone(config.timezone_c)).isoweekday()
    if t < 7:
        update.message.reply_text(get_schedule(get_week(), t), parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(get_schedule(get_week(), 0), parse_mode=ParseMode.HTML)

def week(bot, update):
    keyboard =\
        [
            [InlineKeyboardButton(config.days_list[0], callback_data='0')],
            [InlineKeyboardButton(config.days_list[1], callback_data='1')],
            [InlineKeyboardButton(config.days_list[2], callback_data='2')],
            [InlineKeyboardButton(config.days_list[3], callback_data='3')],
            [InlineKeyboardButton(config.days_list[4], callback_data='4')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(config.choose_week_day_lang, reply_markup=reply_markup)

def button(bot, update):
    query = update.callback_query

    st = ''

    if datetime.now(pytz.timezone(config.timezone_c)).isoweekday() >= 5 and int(query.data) == 4:
        st = get_schedule(1 - get_week(), int(query.data))
    else:
        st = get_schedule(get_week(), int(query.data))

    bot.edit_message_text(text=st,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=ParseMode.HTML)

def monday(bot, update):
    update.message.reply_text(get_schedule(get_week(), 0), parse_mode=ParseMode.HTML)

def tuesday(bot, update):
    update.message.reply_text(get_schedule(get_week(), 1), parse_mode=ParseMode.HTML)

def wednesday(bot, update):
    update.message.reply_text(get_schedule(get_week(), 2), parse_mode=ParseMode.HTML)

def thursday(bot, update):
    update.message.reply_text(get_schedule(get_week(), 3), parse_mode=ParseMode.HTML)

def friday(bot, update):
    if datetime.now(pytz.timezone(config.timezone_c)).isoweekday() == 5:
        update.message.reply_text(get_schedule(1 - get_week(), 4), parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(get_schedule(get_week(), 4), parse_mode=ParseMode.HTML)

def echo(bot, update):
    update.message.reply_text(update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("test", test))


    dp.add_handler(CommandHandler("today", today))
    dp.add_handler(CommandHandler("tomorrow", tomorrow))
    dp.add_handler(CommandHandler("week", week))

    dp.add_handler(CommandHandler("monday", monday))
    dp.add_handler(CommandHandler("tuesday", tuesday))
    dp.add_handler(CommandHandler("wednesday", wednesday))
    dp.add_handler(CommandHandler("thursday", thursday))
    dp.add_handler(CommandHandler("friday", friday))

    dp.add_handler(CallbackQueryHandler(button))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    PORT = int(os.environ.get('PORT', '5000'))
    # add handlers
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=config.TOKEN)
    # updater.bot.set_webhook('https://{}.herokuapp.com/{}'.format(config.heroku_app_name, config.TOKEN))
    updater.bot.set_webhook('')
    updater.idle()

if __name__ == '__main__':
    main()
