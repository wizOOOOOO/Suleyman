import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot import types
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Настройки для доступа к Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/User/Downloads/pizza-428415-a0ffe5c51b82.json', scope)
client = gspread.authorize(creds)

# Откройте таблицу по ID и выберите нужный лист
spreadsheet_id = "19qRjGrt064N0coKnyzr35ZO649KeU1UwFOzDSHgqN3M"
sheet_name = "Отв. на форму"

# Получаем объект листа
spreadsheet = client.open_by_key(spreadsheet_id)
sheet = spreadsheet.worksheet(sheet_name)

# Создание бота с токеном
TOKEN = '7345010473:AAHLtxcXuWVvM1rbI1LrLirFMNfQa_6knic'
bot = telebot.TeleBot(TOKEN)

# ID чата для отправки уведомлений
chat_id = 6536838346

# ID папки в Google Диске для сохранения фотографий
folder_id = '1nSFwMmR4VjEVOk7GF4KlIzuUawbaKW-m'

# Путь к файлу credentials.json для авторизации в Google Drive API
creds_drive = ServiceAccountCredentials.from_json_keyfile_name(
    'C:/Users/User/Downloads/pizza-428415-a0ffe5c51b82.json', scope
)

# Сервис для Google Drive API
service = build('drive', 'v3', credentials=creds_drive)

# Словарь для временного хранения данных опроса
user_data = {}


# Создание кнопки "СТАРТ" для всех сообщений
def create_start_button():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.add(types.KeyboardButton('СТАРТ'))
    return markup


# Стартовый обработчик
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = create_start_button()
    bot.send_message(message.chat.id, "Нажмите 'СТАРТ', чтобы начать", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "СТАРТ")
def start_survey(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('СПб_15_1', 'Парголово_1', 'Парголово_2', 'СПб_10_1', 'СПб_10_2', 'СПб_10_5', 'СПб_10_4',
               'Янино_1', 'Костомукша_1', 'Бугры_1', 'Волхов_1')
    msg = bot.reply_to(message, "Выберите пиццерию:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_pizzeria_step)


def process_pizzeria_step(message):
    if message.text == "СТАРТ":
        start_survey(message)
        return

    try:
        chat_id = message.chat.id
        user_data[chat_id] = {'Пиццерия': message.text}

        # Определение текущей даты и времени
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")  # Форматируем дату и время

        user_data[chat_id]['Отметка времени'] = timestamp

        msg = bot.reply_to(message, 'Введите ваше ФИО:', reply_markup=create_start_button())
        bot.register_next_step_handler(msg, process_name_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка, попробуйте снова.', reply_markup=create_start_button())


def process_name_step(message):
    if message.text == "СТАРТ":
        start_survey(message)
        return

    try:
        chat_id = message.chat.id
        user_data[chat_id]['ФИО'] = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Кухня', 'Улица', 'Зал', 'Двор')  # Добавлен пункт 'Двор'
        msg = bot.reply_to(message, 'Выберите участок работы:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_work_area_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка, попробуйте снова.', reply_markup=create_start_button())


def process_work_area_step(message):
    if message.text == "СТАРТ":
        start_survey(message)
        return

    try:
        chat_id = message.chat.id
        user_data[chat_id]['Участок работы'] = message.text
        msg = bot.reply_to(message, 'Опишите проблему:', reply_markup=create_start_button())
        bot.register_next_step_handler(msg, process_problem_description_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка, попробуйте снова.', reply_markup=create_start_button())


def process_problem_description_step(message):
    if message.text == "СТАРТ":
        start_survey(message)
        return

    try:
        chat_id = message.chat.id
        user_data[chat_id]['Описание проблемы'] = message.text
        msg = bot.reply_to(message, 'Отправьте фото или видео, либо введите ссылку на них:', reply_markup=create_start_button())
        bot.register_next_step_handler(msg, process_photo_video_step)
    except Exception as e:
        bot.reply_to(message, 'Ошибка, попробуйте снова.', reply_markup=create_start_button())


def process_photo_video_step(message):
    if message.text == "СТАРТ":
        start_survey(message)
        return

    try:
        chat_id = message.chat.id

        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = f"temp_{message.photo[-1].file_id}.jpg"
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            file_metadata = {'name': file_path, 'parents': [folder_id]}
            media = MediaFileUpload(file_path, mimetype='image/jpeg')
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            file_link = f"https://drive.google.com/file/d/{uploaded_file['id']}/view?usp=sharing"
            user_data[chat_id]['Ссылка на фото или видео'] = file_link

        elif message.text:
            link = message.text.strip()
            user_data[chat_id]['Ссылка на фото или видео'] = link
        else:
            user_data[chat_id]['Ссылка на фото или видео'] = ''

        # Запись данных в Google таблицу
        row = [user_data[chat_id][key] for key in
               ['Пиццерия', 'Отметка времени', 'ФИО', 'Участок работы', 'Описание проблемы', 'Ссылка на фото или видео']]
        sheet.append_row(row, value_input_option='RAW')

        # Отправка уведомления в указанный чат
        formatted_message = f"<b>Данные успешно записаны в таблицу:</b>\n\n" \
                            f"<b>Пиццерия:</b> {row[0]}\n" \
                            f"<b>Отметка времени:</b> {row[1]}\n" \
                            f"<b>ФИО:</b> {row[2]}\n" \
                            f"<b>Участок работы:</b> {row[3]}\n" \
                            f"<b>Описание проблемы:</b> {row[4]}\n" \
                            f"<b>Ссылка на фото или видео:</b> <a href='{row[5]}'>Ссылка на файл</a>"

        bot.send_message(chat_id, formatted_message, parse_mode='HTML')

        bot.reply_to(message, 'Спасибо! Ваши данные были записаны в Google Таблицу.', reply_markup=create_start_button())
    except gspread.exceptions.APIError as e:
        bot.reply_to(message, f'Произошла ошибка при записи в таблицу: {str(e)}', reply_markup=create_start_button())
    except Exception as e:
        bot.reply_to(message, f'Произошла непредвиденная ошибка: {str(e)}', reply_markup=create_start_button())


bot.polling()


















