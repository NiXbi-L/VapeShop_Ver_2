import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html,types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.send_media_group import SendMediaGroup
import aiogram

import pandas as pd

import yoomoney
from yoomoney import Quickpay,Client

import cfg

form_router = Router()
bot = Bot(token=cfg.telegramAPI_TOKEN, parse_mode="HTML")

##########################################################################
#Считываем данные с Excel файле в словарь df
df = pd.read_excel('DataBase/Sheets/DataFrame.xlsx',usecols=[1,2,3]).to_dict('list')
userdata = pd.read_excel('DataBase/Sheets/UserData.xlsx',usecols=[1,2,3,4,5,6,7]).to_dict('list')
Citis = pd.read_excel('DataBase/Sheets/Сitis.xlsx',usecols=[1,2]).to_dict('list')
prod = pd.read_excel('DataBase/Sheets/Products.xlsx',usecols=[1,2,3,4,5,6,7,8,9,10,11]).to_dict('list')
VapeDataBase = pd.read_excel('DataBase/Sheets/VapeDataBase.xlsx').to_dict('list')
##########################################################################

#Создаем объект client
client = Client(cfg.yoomoneyAPI_TOKEN)

#Состояния пользователя
class Form(StatesGroup):
    City = State() #Выбор города
    Yes_or_No = State() #Подтверждение выбора города
    vote_my_product = State() #Выбор товара из списка своих
    my_product = State() #Выбор деуствия с товаром
    #Создание карточки товара
    ##########################################################################
    add_productType = State() #Выбор категории
    add_company = State() #Выбор компании производителя
    add_companyName = State() #Выбор названия продукта
    add_Other_company = State()
    add_name = State() #Ввод Названия товара
    add_Amount = State() #Ввод цены  товара
    add_Description = State() #Ввод описания товара
    add_photos = State() #Запрос фотографий товара
    ##########################################################################

    # Поиск по ключевым словам
    ##########################################################################
    vote_search = State() #Выбор типа поиска
    search_of_category = State()
    add_prodType = State()
    vote_prodType = State()
    companyName = State()
    company = State()
    notboxmod = State()
    search_of_KeyWords = State() #Ввод ключемвых слов для поиска
    vote_search_type = State()
    viewing_output = State() #Просмотр выдачи
    ##########################################################################

    #Оплата
    ##########################################################################
    pay_amount = State()
    pay_ok = State()
    ##########################################################################
    #Продвижениие
    vote_up = State()
#Словари глабальных переменных
gl = {}
moder = {}
search_indexes = {}
search = {}
label = {}
up_index = {}
#Функции обработчики
##########################################################################
#Функция возвращает все вхождения элемента в списке
def get_indexes(list,el):
    return [i for i in range(len(list)) if list[i] == el]
#Функция возвращает список всех товаров пользователя(Вспомогательная функция бля вывода профиля)
def search_your_products(userid):
    index = get_indexes(prod['UserID'],userid)
    st = ''
    for i in range(len(index)): #генерируем строку с товарами пользователя
        st += '#'+str(i+1)+' '+ str(prod['ProductsName'][index[i]])+' Цена: '+ str(prod['Amount'][index[i]])+'₽\n'
    return st
#Функции сохраняют товар в базу данных
##########################################################################
def get_mediaGroup(userID,gl):
    if len(gl)>6:
        prod['ProdID'].append(sorted(prod['ProdID'])[len(prod['ProdID'])-1]+1)
        prod['Company'].append(gl[1])
        prod['CompanyName'].append(gl[2])
        prod['ProductsName'].append(gl[3])
        prod['ProductsDescription'].append(gl[4])
        prod['Amount'].append(gl[5])
        prod['ProdType'].append(gl[0])
        prod['UserID'].append(int(userID))
        prod['ModerStatus'].append('moderating')
        st = '|'
        print(len(gl[6::]))
        print(gl)
        for i in range(6,len(gl)):
            st += gl[i]+'|'
        prod['PhotoID'].append(st)
        print(userdata['City'][userdata['UserID'].index(int(userID))])
        prod['City'].append(userdata['City'][userdata['UserID'].index(int(userID))])
        print(prod)
        pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
        return True
    else:
        return False
def non_mdeiaGroup(userID,gl):
    prod['ProdID'].append(sorted(prod['ProdID'])[len(prod['ProdID']) - 1] + 1)
    prod['Company'].append(gl[1])
    prod['CompanyName'].append(gl[2])
    prod['ProductsName'].append(gl[3])
    prod['ProductsDescription'].append(gl[4])
    prod['Amount'].append(gl[5])
    prod['ProdType'].append(gl[0])
    prod['UserID'].append(int(userID))
    prod['ModerStatus'].append('moderating')
    prod['PhotoID'].append('non')
    prod['City'].append(userdata['City'][userdata['UserID'].index(int(userID))])
    pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
def getMdediaGroup(userID,gl):
    if len(gl) > 4:
        prod['ProdID'].append(sorted(prod['ProdID'])[len(prod['ProdID']) - 1] + 1)
        prod['Company'].append('non')
        prod['CompanyName'].append('non')
        prod['ProductsName'].append(gl[1])
        prod['ProductsDescription'].append(gl[2])
        prod['Amount'].append(gl[3])
        prod['ProdType'].append(gl[0])
        prod['UserID'].append(int(userID))
        prod['ModerStatus'].append('moderating')
        st = '|'
        print(len(gl[4::]))
        print(gl)
        for i in range(4, len(gl)):
            st += gl[i] + '|'
        prod['PhotoID'].append(st)
        print(userdata['City'][userdata['UserID'].index(int(userID))])
        prod['City'].append(userdata['City'][userdata['UserID'].index(int(userID))])
        print(prod)
        pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
        return True
    else:
        return False
def nonMdeiaGroup(userID, gl):
    prod['ProdID'].append(sorted(prod['ProdID'])[len(prod['ProdID']) - 1] + 1)
    prod['Company'].append('non')
    prod['CompanyName'].append('non')
    prod['ProductsName'].append(gl[1])
    prod['ProductsDescription'].append(gl[2])
    prod['Amount'].append(gl[3])
    prod['ProdType'].append(gl[0])
    prod['UserID'].append(int(userID))
    prod['ModerStatus'].append('moderating')
    prod['PhotoID'].append('non')
    prod['City'].append(userdata['City'][userdata['UserID'].index(int(userID))])
    pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
##########################################################################

#Функции платежей
##########################################################################
def check_pay(username,label):
    history = client.operation_history(label=label)

    for operation in history.operations:
        if operation.status == 'success':
            return True
        else:
            return False
    else:
        return False
#Функия создания url для оплаты по сумме, тегу, username и типу товара
def create_pay_url(sum,username):
    quickpay = Quickpay(
        receiver=cfg.yoomoneyWallet,
        quickpay_form="shop",
        targets="Payment for services",
        paymentType="SB",
        sum=sum,
        label=str(sorted(df['PayID'])[len(df['PayID'])-1]+1)
    )
    label[str(username)] = sorted(df['PayID'])[len(df['PayID']) - 1] + 1
    df['UserName'].append(username)
    df['PayID'].append(int(sorted(df['PayID'])[len(df['PayID'])-1]+1))
    df['PayAmunt'].append(sum)
    pd.DataFrame(df).to_excel('DataBase/Sheets/DataFrame.xlsx',sheet_name='Payments')
    return quickpay.redirected_url
##########################################################################

#Форма регистрации
##########################################################################
@form_router.message(Command("start"))
async def command_start(message: types.message, state: FSMContext) -> None:
    if message.chat.type == 'private':
        if message.from_user.first_name in userdata['UserName']: #Если пользователь уже есть в базе данных
            await message.answer('Вот список доступных команд:\n' #выводим список команд
                                 '/profile - Посмотреть свой профиль\n'
                                 '/add - Выстовить товар на продажу\n'
                                 '/search - Поиск товаров\n'
                                 '/pay - Задонатить на баланс бота')
        else:
            await message.answer('Для начала работы мне потребуются некоторые твои данные.', #Запрашиваем данные у пользователя
                reply_markup=types.ReplyKeyboardRemove())
            await message.answer('Из какого ты города?',
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Form.City) #Меняем состояние пользователя
@form_router.message(Form.City)
async def City(message: Message, state: FSMContext) -> None:
    if message.chat.type == 'private':
        if message.text in Citis['Город']: #Если город является действительным
            await message.answer(str(message.text)+' '+str(Citis['Край'][Citis['Город'].index(str(message.text))]+'\nВерно?'),reply_markup=types.ReplyKeyboardMarkup(keyboard=[
                    [
                        KeyboardButton(text="Да"),
                        KeyboardButton(text="Нет"),
                    ]
                ],
                resize_keyboard=True))
            #Создаем профиль пользователя
            userdata['UserName'].append(message.from_user.first_name)
            userdata['City'].append(message.text)
            userdata['UserID'].append(message.chat.id)
            userdata['Товары на продаже'].append(0)
            userdata['кол-во продаых товаров'].append(0)
            userdata['Рейтинг'].append(5.0)
            userdata['Balance'].append(0.0)
            await state.set_state(Form.Yes_or_No)
            pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx',sheet_name='Users')
        else:
            await message.answer('Такого города нет. Попоробуй еще раз.')
            await state.clear()
            await state.set_state(Form.City)
@form_router.message(Form.Yes_or_No)
async def Yes_or_No(message: Message, state: FSMContext) -> None:
    if message.chat.type == 'private':
        if message.text == 'Да':
            await state.clear()

            await message.answer(
                "Данные занесены.\n"
                'Вот список доступных команд:\n'
                '/profile - Посмотреть свой профиль\n'
                '/add - Выстовить товар на продажу\n'
                '/search - Поиск товаров\n'
                '/pay - Задонатить на баланс бота',
                reply_markup=types.ReplyKeyboardRemove()
            )
        elif message.text == 'Нет': #Удаляем Упоменание о пользователя в базе данных и просим пройти процедуру заного
            userdata['City'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['Balance'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['UserID'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['Товары на продаже'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['кол-во продаых товаров'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['Рейтинг'].pop(userdata['UserName'].index(message.from_user.first_name))
            userdata['UserName'].remove(message.from_user.first_name)
            pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx', sheet_name='Users')
            await message.answer('Хорошо. Введите новое название города.')
            await state.set_state(Form.City)
##########################################################################

#Профиль пользователя
##########################################################################
@form_router.message(Command("profile"))
async def command_profile(message: Message) -> None:
    if message.chat.type == 'private':
        await message.answer(message.from_user.first_name+'\n=========================\nБаланс: ' #Выводим данные профиля
                             +str(userdata['Balance'][userdata['UserID'].index(message.chat.id)])
                             +'₽\nРейтинг: ' + str(userdata['Рейтинг'][userdata['UserID'].index(message.chat.id)])
                                +'\n=========================\nКол-во проданных товаров: '
                                +str(userdata['кол-во продаых товаров'][userdata['UserID'].index(message.chat.id)])
                             +'\nКол-во товаров на продаже: ' + str(len(get_indexes(prod['UserID'],message.chat.id)))
                             +'\n=========================\nТовары на продаже:\n'+search_your_products(message.chat.id)
                             +'\n=========================\nЧтобы открыть страницу товара введите\n/order')
##########################################################################

#Вызов страницы товара
##########################################################################
@form_router.message(Command("order")) #Вызов страници товара
async def command_profile(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        await state.set_state(Form.vote_my_product) #Запрос id товара из профиля
        await message.answer('Введите номер товара',reply_markup=builder.as_markup())
@form_router.message(Form.vote_my_product)
async def vote_my_product(message: Message, state: FSMContext) -> None:
    if message.chat.type == 'private':
        index = get_indexes(prod['UserID'],message.chat.id) #получем список индексов товаров пользователя
        if prod['PhotoID'][index[int(message.text) - 1]] != 'non': #Елси к товару приложены фотографии
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                    text="Удалить",
                    callback_data="del"+str(index[int(message.text)-1])),
                types.InlineKeyboardButton(
                    text="Продвинуть",
                    callback_data="up"+str(index[int(message.text)-1])+'|'+str(message.from_user.id)),
            )
            await state.clear()
            media = []
            indexph = get_indexes(list(prod['PhotoID'][index[int(message.text)-1]]),'|') #Получаем список индексов элемента '|' Он нужен для разделения photoID
            #Генерируем медиагруппу
            for i in range(len(indexph)-1):
                if i == 0: #В первую фотографию добавляем описание
                    media.append(types.InputMediaPhoto(media=prod['PhotoID'][index[int(message.text)-1]][indexph[i]+1:indexph[i+1]],
                                                       caption='Название: ' + str(prod['ProductsName'][index[int(message.text)-1]])
                                     +'\nЦена: ' + str(prod['Amount'][index[int(message.text)-1]])+'₽'
                                     +'\n=========================\nОписание:\n'+str(prod['ProductsDescription'][index[int(message.text)-1]])+'\n=========================\n'))
                else:
                    media.append(types.InputMediaPhoto(media=prod['PhotoID'][index[int(message.text) - 1]][indexph[i] + 1:indexph[i + 1]]))
            await SendMediaGroup(chat_id=message.chat.id,media=media) #Отправляем медиа группу
            await message.answer('⬇️Действия с товаром⬇️',reply_markup=builder.as_markup())
        else: #Если к товару не приложены фотографии
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Удалить",
                callback_data="del" + str(index[int(message.text) - 1])),
                types.InlineKeyboardButton(
                    text="Продвинуть",
                    callback_data="up" + str(index[int(message.text) - 1])+'|'+str(message.from_user.id)),
            )
            await state.clear()
            await message.answer('Название: ' + str(prod['ProductsName'][index[int(message.text)-1]])
                                     +'\nЦена: ' + str(prod['Amount'][index[int(message.text)-1]])+'₽'
                                     +'\n=========================\nОписание:\n'+str(prod['ProductsDescription'][index[int(message.text)-1]])+'\n=========================\n')
            await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
##########################################################################

#Создание товара
##########################################################################
@form_router.message(Command("add"))
async def command_profile(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        await state.set_state(Form.add_productType)
        await message.answer('Выберите категорию',reply_markup=types.ReplyKeyboardMarkup(keyboard=[[ #Вызов клавиатуры категорий
                        KeyboardButton(text="Жидкости"),
                        KeyboardButton(text="Мехмоды"),
                        KeyboardButton(text="Боксмоды/Подмоды"),
                    ]],resize_keyboard=True))
@form_router.message(Form.add_productType) #Запрос типа продукта
async def add_productType(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        if message.text == 'Жидкости' or message.text == 'Мехмоды': #Если выбран раздел Жидкости или Мехмоды то мы перескакиваем сразу на ввод названия
            gl[str(message.from_user.id)] = [message.text]
            await state.set_state(Form.add_name)
            await message.answer(reply_markup=types.ReplyKeyboardRemove(), text='*')
            await message.answer('Введите название товара',reply_markup=builder.as_markup())
        elif message.text == 'Боксмоды/Подмоды': #Если выбран раздел Боксмоды/Подмоды то мы переходим на ввод компании производителя
            gl[str(message.from_user.id)] = [message.text]
            await state.set_state(Form.add_company)
            st = ''
            for i in range(len(list(VapeDataBase))): #Формируем список компаний
                st += '#'+str(i+1)+' '+str(list(VapeDataBase)[i])+'\n'
            await message.answer(reply_markup=types.ReplyKeyboardRemove(),text='*')
            await message.answer('Выберите компанию производитель:\n'+st+'#'+str(len(list(VapeDataBase))+1)+' Другое',reply_markup=builder.as_markup())
@form_router.message(Form.add_company) #Запрос компании производителя
async def add_company(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        try:
            if int(message.text) != len(list(VapeDataBase))+1 and int(message.text) < len(list(VapeDataBase))+1 and int(message.text) > 0: #Если Значение в деапазоне допустимого то запаращиваем название
                await state.set_state(Form.add_companyName)
                gl[str(message.from_user.id)].append(list(VapeDataBase)[int(message.text)-1])#Добавляем компанию производитель
                st = ''
                x = 0
                for i in range(len(VapeDataBase[gl[str(message.from_user.id)][1]])):
                    if str(VapeDataBase[gl[str(message.from_user.id)][1]][i]) == 'nan': #формируем список устройств
                        x = i
                        break
                    st += '#' + str(i + 1) + ' ' + str(VapeDataBase[gl[str(message.from_user.id)][1]][i]) + '\n'
                await message.answer('Выберите устройство:\n'+st+'#'+str(x+1)+' Другое',reply_markup=builder.as_markup())
            elif int(message.text) == len(list(VapeDataBase))+1:
                await state.set_state(Form.add_Other_company)
                await message.answer('Введите название компании производителя:',reply_markup=builder.as_markup())
            else:
                await message.answer('Введено неверное значение. Попробуйте еще раз.')
        except:
            await message.answer('Введено неверное значение. Попробуйте еще раз.')
@form_router.message(Form.add_companyName) #Запрос названия устройства
async def add_companyName(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        try:
            print(int(message.text))
            x = 0
            for i in range(len(VapeDataBase[gl[str(message.from_user.id)][1]])):
                if str(VapeDataBase[gl[str(message.from_user.id)][1]][i]) == 'nan':
                    x = i
                    break
            if int(message.text) != x+1 and int(message.text) < x+1 and int(message.text) > 0: #Если выбрано верное значение то заносим название в базу и переходим к заполнению названия
                await state.set_state(Form.add_name)
                gl[str(message.from_user.id)].append(VapeDataBase[gl[str(message.from_user.id)][1]][int(message.text)-1])
                await message.answer('Введите название товара',reply_markup=builder.as_markup())
            elif int(message.text) == x+1:
                await state.set_state(Form.add_name)
                gl[str(message.from_user.id)][1]+=' '
                await message.answer('Введите название товара',reply_markup=builder.as_markup())
            else:
                await message.answer('Введено неверное значение. Попробуйте еще раз.')
        except:
            await message.answer('Введено неверное значение. Попробуйте еще раз.')
@form_router.message(Form.add_Other_company) #Если выбрано другое то запрос компании производителя в текстовом виде
async def add_Other_company(message: Message,state: FSMContext) -> None:
    gl[str(message.from_user.id)].append(str(message.text))
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="Отмена")
    )
    await message.answer('Введите название товара',reply_markup=builder.as_markup())
    await state.set_state(Form.add_name)
@form_router.message(Form.add_name) #Запрос названия товара
async def add_name(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        try:
            if gl[str(message.from_user.id)][1] in list(VapeDataBase):
                gl[str(message.from_user.id)].append(message.text)
                await state.set_state(Form.add_Description)
                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(
                    text="Отмена",
                    callback_data="Отмена")
                )
                await message.answer('Введите описание',reply_markup=builder.as_markup())
            else:
                gl[str(message.from_user.id)].append(message.text)
                gl[str(message.from_user.id)].append(message.text)
                await state.set_state(Form.add_Description)
                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(
                    text="Отмена",
                    callback_data="Отмена")
                )
                await message.answer('Введите описание', reply_markup=builder.as_markup())
        except:
            gl[str(message.from_user.id)].append(message.text)
            await state.set_state(Form.add_Description)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Отмена",
                callback_data="Отмена")
            )
            await message.answer('Введите описание', reply_markup=builder.as_markup())
@form_router.message(Form.add_Description) #Запрос описания товара
async def add_Description(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        gl[str(message.from_user.id)].append(message.text)
        await state.set_state(Form.add_Amount)
        await message.answer('Введите цену товара',reply_markup=builder.as_markup())
        print(gl[str(message.from_user.id)])
@form_router.message(Form.add_Amount) #Запрос цены товара
async def add_Amount(message: Message,state: FSMContext) -> None:
    try:
        gl[str(message.from_user.id)].append(int(message.text))
        await state.set_state(Form.add_photos)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Нажать после\nотправки фотографий",
            callback_data=str(message.from_user.id))
        )
        builder.row(types.InlineKeyboardButton(
            text="Продолжить без фотографий",
            callback_data='non'+str(message.from_user.id)))
        await message.answer('Отравьте фотографии',reply_markup=builder.as_markup())
    except:
        await message.answer('Введено неверное значение')
@form_router.message(Form.add_photos) #Запрос фотографий
async def add_photos(message: Message,state: FSMContext) -> None:
    try:
        if message.chat.type == 'private':
            gl[str(message.from_user.id)].append(message.photo[-1].file_id)
    except:
        await message.answer('Вы отправили не фото.')

##########################################################################

#Поиск товара
##########################################################################
@form_router.message(Command("search"))
async def command_search(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        await state.set_state(Form.vote_search)
        await message.answer('Выберите способ поиска',reply_markup=types.ReplyKeyboardMarkup(keyboard=[[ #Вызов клавиатуры категорий
                        KeyboardButton(text="По категориям"),
                        KeyboardButton(text="По ключевым словам"),
                    ]],resize_keyboard=True))
@form_router.message(Form.vote_search)
async def vote_search(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        if message.text == "По категориям":
            await state.set_state(Form.vote_prodType)
            await message.answer('Выберите категорию',
                                 reply_markup=types.ReplyKeyboardMarkup(keyboard=[[  # Вызов клавиатуры категорий
                                     KeyboardButton(text="Жидкости"),
                                     KeyboardButton(text="Мехмоды"),
                                     KeyboardButton(text="Боксмоды/Подмоды"),
                                 ]], resize_keyboard=True))
        elif message.text == "По ключевым словам":
            await state.set_state(Form.search_of_KeyWords)
            await message.answer('*',reply_markup=types.ReplyKeyboardRemove())
            await message.answer('Введите поисковой запрос.',reply_markup=builder.as_markup())
@form_router.message(Form.vote_prodType)
async def vote_prodType(message: Message,state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="Отмена")
    )
    if message.text == "Боксмоды/Подмоды":
        await state.set_state(Form.notboxmod)
        await message.answer('Выберите способ поиска',
                             reply_markup=types.ReplyKeyboardMarkup(keyboard=[[  # Вызов клавиатуры категорий
                                 KeyboardButton(text="Выбрать компанию производитель"),
                                 KeyboardButton(text="Показать все"),
                             ]], resize_keyboard=True))
    elif message.text == 'Жидкости' or message.text == 'Мехмоды':
        search_indexes[str(message.from_user.id)] = [i for i in range(len(prod['ProductsName'])) if prod['ProdType'][i] == message.text and prod['ModerStatus'][i] == 'Moderated' and prod['City'][i] == userdata['City'][userdata['UserID'].index(int(message.from_user.id))]]
        if search_indexes[str(message.from_user.id)] == []:
            await state.clear()
            await message.answer('По вашему запросу ничего не найдено',reply_markup=types.ReplyKeyboardRemove())
        else:
            await state.set_state(Form.vote_search_type)
            await message.answer('Выберите тип выдачи:\n#1 Сразу все\n#2 Листать',reply_markup=types.ReplyKeyboardRemove())
@form_router.message(Form.notboxmod)
async def notboxmod(message: Message,state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="Отмена")
    )
    if message.text == 'Выбрать компанию производитель':
        await state.set_state(Form.company)
        st = ''
        for i in range(len(list(VapeDataBase))):  # Формируем список компаний
            st += '#' + str(i + 1) + ' ' + str(list(VapeDataBase)[i]) + '\n'
        await message.answer(reply_markup=types.ReplyKeyboardRemove(), text='*')
        await message.answer(
            'Выберите компанию производитель:\n' + st,
            reply_markup=builder.as_markup())
    elif message.text == 'Показать все':
        search_indexes[str(message.from_user.id)] = [i for i in range(len(prod['ProductsName'])) if
                                                     prod['ProdType'][i] == 'Боксмоды/Подмоды' and prod['ModerStatus'][
                                                         i] == 'Moderated' and prod['City'][i] == userdata['City'][
                                                         userdata['UserID'].index(int(message.from_user.id))]]
        if search_indexes[str(message.from_user.id)] == []:
            await state.clear()
            await message.answer('По вашему запросу ничего не найдено', reply_markup=types.ReplyKeyboardRemove())
        else:
            await state.set_state(Form.vote_search_type)
            await message.answer('Выберите тип выдачи:\n#1 Сразу все\n#2 Листать',
                                 reply_markup=types.ReplyKeyboardRemove())
@form_router.message(Form.company)
async def company(message: Message,state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="Отмена")
    )
    if int(message.text) < len(list(VapeDataBase)) and int(message.text) > 0:  # Если Значение в деапазоне допустимого то запаращиваем название
        await state.set_state(Form.companyName)
        search[str(message.from_user.id)] = [list(VapeDataBase)[int(message.text) - 1]]  # Добавляем компанию производитель
        st = ''
        x = 0
        for i in range(len(VapeDataBase[search[str(message.from_user.id)][0]])):
            if str(VapeDataBase[search[str(message.from_user.id)][0]][i]) == 'nan':  # формируем список устройств
                x = i
                break
            st += '#' + str(i + 1) + ' ' + str(VapeDataBase[search[str(message.from_user.id)][0]][i]) + '\n'
        await message.answer('Выберите устройство:\n' + st,
                             reply_markup=builder.as_markup())
    else:
        await message.answer('Введено неверное значение. Попробуйте еще раз.')
@form_router.message(Form.companyName)
async def companyName(message: Message,state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="Отмена")
    )
    print(int(message.text))
    x = 0
    for i in range(len(VapeDataBase[search[str(message.from_user.id)][0]])):
        if str(VapeDataBase[search[str(message.from_user.id)][0]][i]) == 'nan':
            x = i
            break
    if int(message.text) != x + 1 and int(
            message.text) < x + 1 and int(message.text) > 0:  # Если выбрано верное значение то заносим название в базу и переходим к заполнению названия
        await state.set_state(Form.add_name)
        search[str(message.from_user.id)].append(VapeDataBase[search[str(message.from_user.id)][0]][int(message.text) - 1])
        search_indexes[str(message.from_user.id)] = [i for i in range(len(prod['ProductsName'])) if search[str(message.from_user.id)][0] == prod['Company'][i] and search[str(message.from_user.id)][1] == prod['CompanyName'][i] and prod['ModerStatus'][i] == 'Moderated' and prod['City'][i]==userdata['City'][userdata['UserID'].index(int(message.from_user.id))]]
        if search_indexes[str(message.from_user.id)] == []:
            await state.clear()
            await message.answer('По вашему запросу ничего не найдено')
        else:
            await state.set_state(Form.vote_search_type)
            await message.answer('Выберите тип выдачи:\n#1 Сразу все\n#2 Листать')
    else:
        await message.answer('Введено неверное значение. Попробуйте еще раз.')
@form_router.message(Form.search_of_KeyWords)
async def search_of_KeyWords(message: Message,state: FSMContext) -> None:
    search_indexes[str(message.from_user.id)] = [i for i in range(len(prod['ProductsName'])) if message.text in prod['ProductsName'][i] and prod['ModerStatus'][i] == 'Moderated' and prod['City'][i]==userdata['City'][userdata['UserID'].index(int(message.from_user.id))]]
    if search_indexes[str(message.from_user.id)] == []:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Продолжить\nпоиск",
            callback_data="go")
        )
        await state.clear()
        await message.answer('По вашему запросу ничего не найдено',reply_markup=builder.as_markup())
    else:
        await state.set_state(Form.vote_search_type)
        await message.answer('Выберите тип выдачи:\n#1 Сразу все\n#2 Листать')
@form_router.message(Form.vote_search_type)
async def add_vote_search_type(message: Message,state: FSMContext) -> None:
    if message.text == '1':
        index = search_indexes[str(message.from_user.id)]
        for i in range(len(search_indexes[str(message.from_user.id)])):
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Написать продавцу",
                url='tg://openmessage?user_id=' + str(prod['UserID'][index[i]]),
            ))
            if str(prod['PhotoID'][index[i]]) != 'non':  # Елси к товару приложены фотографии
                await state.clear()
                media = []
                indexph = get_indexes(list(prod['PhotoID'][index[i]]),
                                      '|')  # Получаем список индексов элемента '|' Он нужен для разделения photoID
                # Генерируем медиагруппу
                for j in range(len(indexph) - 1):
                    if j == 0:  # В первую фотографию добавляем описание
                        media.append(types.InputMediaPhoto(
                            media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]],
                            caption='Название: ' + str(prod['ProductsName'][index[i]])
                                    + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                    + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])))
                    else:
                        media.append(types.InputMediaPhoto(
                            media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]]))
                await SendMediaGroup(chat_id=message.chat.id, media=media)  # Отправляем медиа группу
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
            else:  # Если к товару не приложены фотографии
                await state.clear()
                await message.answer('Название: ' + str(prod['ProductsName'][index[i]])
                                     + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                     + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])+'\n=========================\n')
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
    elif message.text == '2':
        index = search_indexes[str(message.from_user.id)]
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
                text="Написать продавцу",
                url='tg://openmessage?user_id=' + str(prod['UserID'][index[0]]),
        ))
        if str(prod['PhotoID'][index[0]]) != 'non':  # Елси к товару приложены фотографии
            media = []
            indexph = get_indexes(list(prod['PhotoID'][index[0]]),
                                      '|')  # Получаем список индексов элемента '|' Он нужен для разделения photoID
                # Генерируем медиагруппу
            for j in range(len(indexph) - 1):
                if j == 0:  # В первую фотографию добавляем описание
                    media.append(types.InputMediaPhoto(
                            media=prod['PhotoID'][index[0]][indexph[j] + 1:indexph[j + 1]],
                            caption='Название: ' + str(prod['ProductsName'][index[0]])
                                    + '\nЦена: ' + str(prod['Amount'][index[0]]) + '₽'
                                    + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[0]])+'\n=========================\n'))
                else:
                    media.append(types.InputMediaPhoto(
                        media=prod['PhotoID'][index[0]][indexph[j] + 1:indexph[j + 1]]))
            await SendMediaGroup(chat_id=message.chat.id, media=media)  # Отправляем медиа группу
            await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
        else:  # Если к товару не приложены фотографии
            await message.answer('Название: ' + str(prod['ProductsName'][index[0]])
                                     + '\nЦена: ' + str(prod['Amount'][index[0]]) + '₽'
                                     + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[0]])+'\n=========================\n')
            await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
        if len(index)>1:
            await state.set_state(Form.viewing_output)
            await message.answer('*',
                                 reply_markup=types.ReplyKeyboardMarkup(keyboard=[[  # Вызов клавиатуры категорий
                                     KeyboardButton(text="⬅️"),
                                     KeyboardButton(text="Отмена"),
                                     KeyboardButton(text="➡️"),
                                 ]], resize_keyboard=True))
            search[str(message.from_user.id)] = 0
        else:
            await message.answer('Список закончился')
            await state.clear()
@form_router.message(Form.viewing_output)
async def viewing_output(message: Message,state: FSMContext) -> None:
    if message.text == '➡️':
        search[str(message.from_user.id)]+=1
        i = search[str(message.from_user.id)]
        index = search_indexes[str(message.from_user.id)]
        if search[str(message.from_user.id)] > len(index)-1:
            await state.clear()
            await message.answer('Список закончился. Поиск отменен',reply_markup=types.ReplyKeyboardRemove())
        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                    text="Написать продавцу",
                    url='tg://openmessage?user_id=' + str(prod['UserID'][index[i]]),
            ))
            if str(prod['PhotoID'][index[i]]) != 'non':  # Елси к товару приложены фотографии
                media = []
                indexph = get_indexes(list(prod['PhotoID'][index[i]]),
                                          '|')  # Получаем список индексов элемента '|' Он нужен для разделения photoID
                # Генерируем медиагруппу
                for j in range(len(indexph) - 1):
                    if j == 0:  # В первую фотографию добавляем описание
                        media.append(types.InputMediaPhoto(
                            media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]],
                            caption='Название: ' + str(prod['ProductsName'][index[i]])
                                        + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                        + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])+'\n=========================\n'))
                    else:
                        media.append(types.InputMediaPhoto(
                                media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]]))
                await SendMediaGroup(chat_id=message.chat.id, media=media)  # Отправляем медиа группу
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
            else:  # Если к товару не приложены фотографии
                await message.answer('Название: ' + str(prod['ProductsName'][index[i]])
                                         + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                         + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])+'\n=========================\n')
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
    elif message.text == '⬅️':
        search[str(message.from_user.id)]-=1
        i = search[str(message.from_user.id)]
        index = search_indexes[str(message.from_user.id)]
        if search[str(message.from_user.id)] < 0:
            await state.clear()
            await message.answer('Список закончился. Поиск отменен',reply_markup=types.ReplyKeyboardRemove())
        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                    text="Написать продавцу",
                    url='tg://openmessage?user_id=' + str(prod['UserID'][index[i]]),
            ))
            if str(prod['PhotoID'][index[i]]) != 'non':  # Елси к товару приложены фотографии
                media = []
                indexph = get_indexes(list(prod['PhotoID'][index[i]]),
                                          '|')  # Получаем список индексов элемента '|' Он нужен для разделения photoID
                # Генерируем медиагруппу
                for j in range(len(indexph) - 1):
                    if j == 0:  # В первую фотографию добавляем описание
                        media.append(types.InputMediaPhoto(
                            media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]],
                            caption='Название: ' + str(prod['ProductsName'][index[i]])
                                        + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                        + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])+'\n=========================\n'))
                    else:
                        media.append(types.InputMediaPhoto(
                                media=prod['PhotoID'][index[i]][indexph[j] + 1:indexph[j + 1]]))
                await SendMediaGroup(chat_id=message.chat.id, media=media)  # Отправляем медиа группу
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
            else:  # Если к товару не приложены фотографии
                await message.answer('Название: ' + str(prod['ProductsName'][index[i]])
                                         + '\nЦена: ' + str(prod['Amount'][index[i]]) + '₽'
                                         + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index[i]])+'\n=========================\n')
                await message.answer('⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
    elif message.text == 'Отмена':
        await state.clear()
        await message.answer('Поиск отменен',reply_markup=types.ReplyKeyboardRemove())
##########################################################################

#Пополнение баланса
##########################################################################
@form_router.message(Command("pay"))
async def command_pay(message: Message,state: FSMContext) -> None:
    if message.chat.type == 'private':
        await state.set_state(Form.pay_amount)
        await message.answer('Введите сумму для пополнения')
@form_router.message(Form.pay_amount)
async def pay_amount(message: Message,state: FSMContext) -> None:
    if int(message.text) > 1:
        pay_url = create_pay_url(int(message.text),message.from_user.id)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
                text="Оплатить",
                url = str(pay_url)),
        )
        builder.row(types.InlineKeyboardButton(
                    text="Проверить оплату",
                    callback_data=str(label[str(message.from_user.id)])+'|'+str(message.from_user.id)+'|'+str(message.text)))
        await message.answer('Заявка на оплату №' + str(label[str(message.from_user.id)])+'создана',reply_markup=builder.as_markup())
    else:
        await message.answer('Введено неверное значение. Попробуйте еще раз',reply_markup=types.ReplyKeyboardRemove())
##########################################################################

#Продвижение
##########################################################################
@form_router.message(Form.vote_up)
async def vote_up(message: Message,state: FSMContext) -> None:
    if message.text == '1':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Написать продавцу",
            url='tg://openmessage?user_id=' + str(message.from_user.id),
        ))
        if userdata['Balance'][userdata['UserID'].index(int(message.from_user.id))] - 200 > 0:
            userdata['Balance'][userdata['UserID'].index(int(message.from_user.id))] -= 200
            pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx', sheet_name='Users')
            index = up_index[str(message.from_user.id)]
            for i in range(len(userdata['UserID'])):
                if prod['City'][i] == userdata['City'][userdata['UserID'].index(int(message.from_user.id))]:
                    if prod['PhotoID'][i] != 'non':
                        groupID = userdata['UserID'][i]
                        media = []
                        indexph = get_indexes(list(prod['PhotoID'][index]), '|')
                        for i in range(len(indexph) - 1):
                            if i == 0:
                                media.append(types.InputMediaPhoto(
                                    media=prod['PhotoID'][index][indexph[i] + 1:indexph[i + 1]],
                                    caption='Название: ' + str(prod['ProductsName'][index])
                                            + '\nЦена: ' + str(prod['Amount'][index]) + '₽'
                                            + '\n=========================\nОписание:\n' + str(
                                        prod['ProductsDescription'][index])
                                            + '\n=========================\nКомпания производитель:' + str(
                                        prod['Company'][index])
                                            + '\nНазвание продукта:' + str(prod['CompanyName'][index])
                                            + '\nРаздел: ' + str(prod['ProdType'][index])))
                            else:
                                media.append(types.InputMediaPhoto(
                                    media=prod['PhotoID'][index][indexph[i] + 1:indexph[i + 1]]))
                        await SendMediaGroup(chat_id=groupID, media=media)
                        await bot.send_message(groupID, '⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
                        await state.clear()
                    else:
                        groupID = userdata['UserID'][i]
                        await bot.send_message(groupID, 'Название: ' + str(prod['ProductsName'][index])
                                               + '\nЦена: ' + str(prod['Amount'][index]) + '₽'
                                               + '\n=========================\nОписание:\n' + str(
                            prod['ProductsDescription'][index])
                                               + '\n=========================\nКомпания производитель:' + str(
                            prod['Company'][index])
                                               + '\nНазвание продукта:' + str(prod['CompanyName'][index])
                                               + '\nРаздел: ' + str(prod['ProdType'][index]))
                        await bot.send_message(groupID,'⬇️Действия с товаром⬇️',reply_markup=builder.as_markup())
                        await state.clear()
            await message.answer('Услуга оказана')
##########################################################################

#Обработка колбеков
##########################################################################
@form_router.callback_query(Form.add_photos) #Колбеки фотграфий
async def callback_query_handler(callback_query: types.CallbackQuery,state: FSMContext) -> any:
    if callback_query.data[0:3] != 'non':
        if gl[str(callback_query.data)][0] == 'Жидкости' or gl[str(callback_query.data)][0] == 'Мехмоды':
            bool = getMdediaGroup(callback_query.data, gl[str(callback_query.data)])
        else:
            bool = get_mediaGroup(callback_query.data, gl[str(callback_query.data)])
        gl[str(callback_query.data)].clear()
        if bool:
            await bot.send_message(chat_id=callback_query.data,
                                               text='Товар создан. Как только товар пройдет модерацию, вам прийдет уведомление.')
            await bot.delete_message(chat_id=callback_query.message.chat.id,message_id=callback_query.message.message_id)
            await state.clear()
            #отправка товара на модерацию
            groupID = -1001667843376
            index = get_indexes(prod['UserID'], int(callback_query.data))
            print(index)
            index = sorted(index)[len(index)-1]
            print(index)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                    text="Удалить",
                    callback_data="deladm" + str(index)),
                    types.InlineKeyboardButton(
                        text="Выставить",
                        callback_data="upadm" + str(index)),
            )
            moder[str(index)] = callback_query.data
            await state.clear()
            media = []
            indexph = get_indexes(list(prod['PhotoID'][index]), '|')
            for i in range(len(indexph) - 1):
                if i == 0:
                    media.append(types.InputMediaPhoto(
                        media=prod['PhotoID'][index][indexph[i] + 1:indexph[i + 1]],
                        caption='Название: ' + str(prod['ProductsName'][index])
                                    + '\nЦена: ' + str(prod['Amount'][index]) + '₽'
                                    + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index])
                                     +'\n=========================\nКомпания производитель:' + str(prod['Company'][index])
                                    +'\nНазвание продукта:'+str(prod['CompanyName'][index])
                                    +'\nРаздел: '+str(prod['ProdType'][index])))
                else:
                    media.append(types.InputMediaPhoto(
                        media=prod['PhotoID'][index][indexph[i] + 1:indexph[i + 1]]))
            await SendMediaGroup(chat_id=groupID, media=media)
            await bot.send_message(groupID,'⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
        else:
            await bot.send_message(chat_id=callback_query.data,
                                   text='Ошибка создания товара. Попробуйте создать его заного')
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    else:
        if gl[str(callback_query.data[3::])][0] == 'Жидкости' or gl[str(callback_query.data[3::])][0] == 'Мехмоды':
            nonMdeiaGroup(callback_query.data[3::], gl[str(callback_query.data[3::])])
        else:
            non_mdeiaGroup(callback_query.data[3::], gl[str(callback_query.data[3::])])
        gl[str(callback_query.data[3::])].clear()
        await bot.send_message(chat_id=callback_query.data[3::],
                                   text='Товар создан. Как только товар пройдет модерацию, вам прийдет уведомление.')
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await state.clear()
        # отправка товара на модерацию
        groupID = -1001667843376
        index = get_indexes(prod['UserID'], int(callback_query.data[3::]))
        print(index)
        index = sorted(index)[len(index)-1]
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
                text="Удалить",
                callback_data="deladm" + str(index)),
                types.InlineKeyboardButton(
                    text="Выставить",
                    callback_data="upadm" + str(index)),
        )
        moder[str(index)] = callback_query.data[3::]
        await bot.send_message(groupID, 'Название: ' + str(prod['ProductsName'][index])
                                + '\nЦена: ' + str(prod['Amount'][index]) + '₽'
                                + '\n=========================\nОписание:\n' + str(prod['ProductsDescription'][index])
                                 +'\n=========================\nКомпания производитель:' + str(prod['Company'][index])
                                +'\nНазвание продукта:'+str(prod['CompanyName'][index])
                                +'\nРаздел: '+str(prod['ProdType'][index]))
        await bot.send_message(groupID, '⬇️Действия с товаром⬇️', reply_markup=builder.as_markup())
        await state.clear()
@form_router.callback_query(Form.pay_amount) #Колбеки фотграфий
async def callback_query_handler(callback_query: types.CallbackQuery,state: FSMContext) -> any:
    index = get_indexes(list(callback_query.data),'|')
    if check_pay(callback_query.data[index[0]+1:index[1]],callback_query.data[0:index[0]]):
        userdata['Balance'][userdata['UserID'].index(int(callback_query.data[index[0]+1:index[1]]))] += int(callback_query.data[index[1]+1::])
        pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx', sheet_name='Users')
        await bot.delete_message(callback_query.message.chat.id,callback_query.message.message_id)
        await callback_query.answer('Оплата прошла деньги зачислены на баланс')
    else:
        await callback_query.answer('Ошибка')
@form_router.callback_query() #все колбеки
async def callback_query_handler(callback_query: types.CallbackQuery,state: FSMContext) -> any:
    if callback_query.data[0:3] == 'del' and callback_query.data[0:6] != 'deladm':
        try:
            prod['ProdID'].pop(int(callback_query.data[3::]))
            prod['Company'].pop(int(callback_query.data[3::]))
            prod['CompanyName'].pop(int(callback_query.data[3::]))
            prod['ProductsName'].pop(int(callback_query.data[3::]))
            prod['ProductsDescription'].pop(int(callback_query.data[3::]))
            prod['Amount'].pop(int(callback_query.data[3::]))
            prod['UserID'].pop(int(callback_query.data[3::]))
            prod['ModerStatus'].pop(int(callback_query.data[3::]))
            prod['PhotoID'].pop(int(callback_query.data[3::]))
            prod['City'].pop(int(callback_query.data[3::]))
            prod['ProdType'].pop(int(callback_query.data[3::]))
            await bot.send_message(callback_query.message.chat.id,'Товар удален')
            await bot.delete_message(callback_query.message.chat.id,callback_query.message.message_id)
            pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
        except:
            await bot.send_message(callback_query.message.chat.id, 'Товара нет в базе данных')
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    elif callback_query.data[0:6] == 'deladm':
        try:
            prod['ProdID'].pop(int(callback_query.data[6::]))
            prod['Company'].pop(int(callback_query.data[6::]))
            prod['CompanyName'].pop(int(callback_query.data[6::]))
            prod['ProductsName'].pop(int(callback_query.data[6::]))
            prod['ProductsDescription'].pop(int(callback_query.data[6::]))
            prod['Amount'].pop(int(callback_query.data[6::]))
            prod['UserID'].pop(int(callback_query.data[6::]))
            prod['ModerStatus'].pop(int(callback_query.data[6::]))
            prod['PhotoID'].pop(int(callback_query.data[6::]))
            prod['City'].pop(int(callback_query.data[6::]))
            prod['ProdType'].pop(int(callback_query.data[6::]))
            await bot.send_message(callback_query.message.chat.id,'Товар удален ')
            await bot.delete_message(callback_query.message.chat.id,callback_query.message.message_id)
            pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
        except:
            await bot.send_message(callback_query.message.chat.id, 'Товара нет в базе данных')
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    if callback_query.data[0:2] == 'up' and callback_query.data[0:5] != 'upadm':
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        up_index[str(callback_query.data[callback_query.data.index('|')+1::])] = int(callback_query.data[2:callback_query.data.index('|')])
        await bot.send_message(callback_query.message.chat.id,'Выберите тип провижения:\n#1 200₽ - Рассылка всем пользователям бота вашего города\n#2 20₽ - Поднятие в ленте')
        await state.set_state(Form.vote_up)
    elif callback_query.data[0:5] == 'upadm':
        try:
            print(int(callback_query.data[5::]))
            prod['ModerStatus'].pop(int(callback_query.data[5::]))
            prod['ModerStatus'].insert(int(callback_query.data[5::]),'Moderated')
            await bot.send_message(callback_query.message.chat.id, 'Товар выставлен на продажу.')
            await bot.send_message(int(moder[callback_query.data[5::]]),'Товар под названием "'
                                   +str(prod['ProductsName'][int(callback_query.data[5::])])
                                   +'" прошел модерацию')
            moder.pop(callback_query.data[5::])
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
            pd.DataFrame(prod).to_excel('DataBase/Sheets/Products.xlsx')
        except:
            await bot.send_message(callback_query.message.chat.id, 'Товара нет в базе данных')
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    if callback_query.data == 'Отмена':
        await state.clear()
        await callback_query.answer('Действие отменено')
        await bot.delete_message(callback_query.message.chat.id,callback_query.message.message_id)
    if callback_query.data == 'go':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="Отмена")
        )
        await state.set_state(Form.search_of_KeyWords)
        await bot.send_message(callback_query.message.chat.id,'Введите поисковой запрос',reply_markup=builder.as_markup())
##########################################################################
async def main():
    bot = Bot(token=cfg.telegramAPI_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
