from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                           Message, PhotoSize)

BOT_TOKEN = '7547013972:AAFwzF16WCaF_4txDBuabJWclmcLAIq8NzU'

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)
user_dict: dict[int, dict[str, str | int | bool]] = {}

class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_age = State()
    fill_gender = State()
    upload_photo = State()
    fill_education = State()
    fill_get_news = State()
    fill_number = State()
    fill_email = State()

@dp.message(CommandStart(), StateFilter(default_state))
async def start_func(message: Message):
    await message.answer(f'Этот бот демонстрирует машину состояний\n'
                         f'Чтобы начать заполнение анкеты, отправьте команду /fillform')

@dp.message(Command(commands=['cancel']), ~StateFilter(default_state))
async def cancel_func(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из машины состояний, и прекратили заполнять анкету.'
                         'Чтобы начать заполнять анкету заново, напишите /fillform')
    await state.clear()

@dp.message(Command(commands=['fillform']), StateFilter(default_state))
async def fillform_func(message: Message, state:FSMContext):
    await message.answer('Вы начали заполнять анкету, введите ваще имя: ')
    await state.set_state(FSMFillForm.fill_name)

@dp.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def set_name_func(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    print(state)
    await message.answer('Имя сохранено! Теперь введите ваш возраст: ')
    print(state.__dict__)
    await state.set_state(FSMFillForm.fill_age)

@dp.message(StateFilter(FSMFillForm.fill_name))
async def wrong_name_func(message:Message):
    await message.answer('Вы ввели не имя, онон должно состоять только из букв,'
                         'если вы хотите завершить заполнение анкеты, то введите /cancel')

@dp.message(StateFilter(FSMFillForm.fill_age), lambda x: x.text.isdigit() and 10 <= int(x.text) <= 100)
async def fill_age_func(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    male_button = InlineKeyboardButton(text='Мужской', callback_data='male')
    female_button = InlineKeyboardButton(text='Женский', callback_data='female')
    keyboard = [[male_button, female_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Спасибо! Теперь выберите пол: ', reply_markup=markup)
    await state.set_state(FSMFillForm.fill_gender)

@dp.message(StateFilter(FSMFillForm.fill_age))
async def wrong_age(message: Message):
    await message.answer(text='Введите корректный возраст от 10 до 100 лет,если хотите прервать заполнение анкеты, то введите /cancel')

@dp.callback_query(StateFilter(FSMFillForm.fill_gender), F.data.in_(['male', 'female']))
async def fill_photo_func(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.delete()
    await callback.message.answer(text='Спасибо! Отправьте ваше фото.')
    await state.set_state(FSMFillForm.upload_photo)

@dp.message(StateFilter(FSMFillForm.fill_gender))
async def wrong_gender(message: Message):
    await message.answer('Введите корректный пол, нажав на кнопку, если хотите прервать заполнение анкеты, то введите /cancel')

@dp.message(StateFilter(FSMFillForm.upload_photo), F.photo[-1].as_('largest_photo'))
async def photo_func(message: Message, state: FSMContext, largest_photo: PhotoSize):
    await state.update_data(photo_unique_id= largest_photo.file_unique_id, photo_id=largest_photo.file_id)
    await message.answer('Отлично! Теперь введите свой номер телефона(формат ввода: +7**********)')
    await state.set_state(FSMFillForm.fill_number)

@dp.message(StateFilter(FSMFillForm.upload_photo))
async def wrong_photo(message: Message):
    await message.answer(text='Вам нужно прислать фото, если хотите завершить заполнение анкеты введите /cancel')

@dp.message(StateFilter(FSMFillForm.fill_number), lambda x: x.text[1:].replace(' ','').isdigit() and len(x.text[1:]) == 11 and x.text[1] == '7')
async def number_func(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer(text='Теперь укажите ваше образование.')
    await state.set_state(FSMFillForm.fill_education)

@dp.message(StateFilter(FSMFillForm.fill_number))
async def wrong_number_func(message: Message):
    await message.answer(text='Вы ввели некорректный номер телефона. Введите номер формата +7********** или завершите заполнение анкеты, вызвав /cancel')

@dp.message(StateFilter(FSMFillForm.fill_education))
async def education_func(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer(text='Хорошо! Теперь введите ваш email.')
    await state.set_state(FSMFillForm.fill_email)

@dp.message(StateFilter(FSMFillForm.fill_email), lambda x: '@' in x.text)
async def email_func(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    button_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    button_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard = [[button_yes], [button_no]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(text='Спасибо! Теперь скажите, хотите ли получать расслыки(да/нет)?', reply_markup=markup)
    await state.set_state(FSMFillForm.fill_get_news)

@dp.message(StateFilter(FSMFillForm.fill_email))
async def wrong_email_func(message: Message):
    await message.answer(text='Вы ввели некорректный email. Введите email корректного формата или завершите заполнение анкеты, вызвав /cancel')

@dp.callback_query(StateFilter(FSMFillForm.fill_get_news), F.data.in_(['yes', 'no']))
async def get_news_func(callback: CallbackQuery, state: FSMContext):
    if callback.data.lower() == 'да':
        await state.update_data(get_news='ВКЛ')
    else:
        await state.update_data(get_news='ВЫКЛ')
    user_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    await callback.message.answer(text='Спасибо! Вы завершили заполнение анкеты, чтобы вывести ее, вызовите /showdata')

@dp.message(StateFilter(FSMFillForm.fill_get_news))
async def wrong_email_func(message: Message):
    await message.answer(text='Пожалуйста, используйте кнопки для ввода ответа или закончите заполнение анкеты, вызвав /cancel')

@dp.message(Command(commands=['showdata']), StateFilter(default_state))
async def show_data_func(message: Message):
    await message.delete()
    if message.from_user.id in user_dict:
        await message.answer_photo(photo=user_dict[message.from_user.id]['photo_id'], caption=f'Имя: {user_dict[message.from_user.id]["name"]}\n'
                                                                                              f'Возраст: {user_dict[message.from_user.id]["age"]}\n'
                                                                                              f'Гендер: {user_dict[message.from_user.id]["gender"]}\n'
                                                                                              f'Email: {user_dict[message.from_user.id]["email"]}\n'
                                                                                              f'Образование: {user_dict[message.from_user.id]["education"]}\n'
                                                                                              f'Рассылки: {user_dict[message.from_user.id]["get_news"]}\n')
    else:
        await message.answer('Вас нет в базе, чтобы продолжить заполнять анкету, введите /fillform')




if __name__ == '__main__':
    dp.run_polling(bot)


