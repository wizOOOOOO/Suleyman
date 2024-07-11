def process_name_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['ФИО'] = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row('Кухня', 'Улица', 'Зал')
        msg = bot.reply_to(message, 'Выберите участок работы:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_work_area_step)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {str(e)}')


def process_work_area_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['Участок работы'] = message.text
        msg = bot.reply_to(message, 'Опишите проблему:')
        bot.register_next_step_handler(msg, process_problem_description_step)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {str(e)}')


def process_problem_description_step(message):
    try:
        chat_id = message.chat.id
        user_data[chat_id]['Описание проблемы'] = message.text
        msg = bot.reply_to(message, 'Введите ссылку на фото или видео:')
        bot.register_next_step_handler(msg, process_photo_video_link_step)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {str(e)}')


def process_photo_video_link_step(message):
    try:
        chat_id = message.chat.id
        link = message.text.strip()
        user_data[chat_id]['Ссылка на фото или видео'] = link

        # Получаем данные для записи в таблицу
        current_pizzeria = user_data[chat_id]['Пиццерия']
        spreadsheet_url = pizzeria_sheets[current_pizzeria]['url']
        gid = pizzeria_sheets[current_pizzeria]['gid']

        # Открываем таблицу по ссылке и gid
        spreadsheet = gc.open_by_url(spreadsheet_url)
        sheet = spreadsheet.get_worksheet(int(gid))  # Используем int(gid) для выбора листа

        # Собираем данные для записи в строку таблицы
        row = [user_data[chat_id][key] for key in
               ['Пиццерия', 'Отметка времени', 'ФИО', 'Участок работы', 'Описание проблемы',
                'Ссылка на фото или видео']]

        # Записываем данные в таблицу
        sheet.append_row(row, value_input_option='RAW')

        bot.reply_to(message, 'Спасибо! Ваши данные были записаны в Google Таблицу.')
    except Exception as e:
        bot.reply_to(message, f'Ошибка при записи в таблицу: {str(e)}')


# Запускаем бота
bot.polling()

