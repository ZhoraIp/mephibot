import telebot
import time
import random
from telebot import types
import requests
from bs4 import BeautifulSoup 
import re
import nltk
from transliterate import translit, get_available_language_codes

#C:\Users\45vit\OneDrive\Рабочий стол\ПП\GitHub\mephibot

TOKEN = '1923581477:AAG77Qs3y8UCD7Low50zhhYZeemuQ5ja7gg' 
bot = telebot.TeleBot(TOKEN, parse_mode=None)

RUS = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя\ '
EN = 'abcdefghijklnmopqrstuvwxyz- '

utoch = []
summary = [{'Военная кафедра', '111'}]

def filter_text(text):
	text = text.lower()
	k = 0
	for i in range(0, len(text)):
		if text[i] in EN:
			k += 1
	if(k/len(text) > 0.8):
		text = translit(text, 'ru')
	text = [c for c in text if c in 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя- ']
	text = ''.join(text)
	return text


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Для того чтобы посмотреть команды откройте /menu")


@bot.message_handler(commands=['menu'])
def artem(message):
	b = message.chat.id
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('/random')
	itembtn2 = types.KeyboardButton('/weather')
	itembtn3 = types.KeyboardButton('/pen')
	itembtn4 = types.KeyboardButton('/ref')
	markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
	bot.send_message(b, "Выберите пункт меню:", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_text(m):
	if m.text.lower() == '/random':
		bot.send_message(m.chat.id, 'Введите диапазон (два числа через пробел)')
		bot.register_next_step_handler(m, rnd)
	elif m.text.lower() == '/weather':
		bot.send_message(m.chat.id, 'Введите город')
		bot.register_next_step_handler(m, weather)
	elif m.text.lower() == '/pen':
		bot.send_message(m.chat.id, 'Введите имя первого и второго игрока через пробел, например(Артем Артем)')
		bot.register_next_step_handler(m, ans1)
	elif m.text.lower() == '/ref':
		bot.send_message(m.chat.id, 'Введите запрос, по которому вы хотите получить ссылку с сайта ПК')
		bot.register_next_step_handler(m, ref)
	else:
		bot.send_message(m.chat.id, "Нет такой команды, чтобы посмотреть команды откройте /menu")

def change(words, question):
	for i in range(0, len(words)):
		dist = nltk.edit_distance(words[i], question)
		if(len(question)>0):
			r = dist/len(question)
			if r < 0.4:
				return words[i]
	return question


def comp(lst, reference, question):
	#try:
		for i in range(0, len(lst)):
			result = re.search(fr"{question}", lst[i])
			if result != None:
				ans = str(lst[i])
				k1 = 0
				k2 = 0
				if(ans.find('href') != -1):
					k1 = ans.find('href')+6

				if(ans.find('>', k1, len(ans)) != -1):
					k2 = ans.find('>', k1, len(ans))

				#print(k1, k2)
				
				for j in range(k1, k2-1):
					reference += ans[j]

				break
		
		if((reference.find('>')+1)+(reference.find('<')+1)+(reference.find('title')+1)>0):
			return 'Нет такой ссылки, попробуйте поменять запрос'
		elif(len(reference) > 0):

			if(reference.find('http') == -1):
				lnk = reference
				reference = 'https://admission.mephi.ru/'
				reference += lnk
			return reference
		else:
			return 'Нет такой ссылки, попробуйте поменять запрос'

	#except:
		#return "ОШИБКА!"
		#bot.send_message(message.chat.id, "ОШИБКА!")
      
def remove_at(i, s):
    return s[:i] + s[i+1:]

def ref(message):
	#try:
		utoch.clear()

		question = message.text
		question = filter_text(str(question))

		qst1 = re.split('; |, | |\n', question)
		qst1.append(question)

		qst = []
		

		for i in range(0, len(qst1)):
			if(len(qst1[i]) > 2):
				#print(qst1[i])
				qst.append(qst1[i])
				
		#print(qst)
		
		

		link = 'https://admission.mephi.ru/'

		responce = requests.get(link).text
		soup = BeautifulSoup(responce, 'lxml')

		block = soup.find('div', id = 'top-menu')
		block = str(block).lower()

		words = [];
		y = 0
		while(y < len(block)):
			word = ' '
			while(block[y] in RUS):
				word += block[y]
				y += 1
			if(len(word) > 2):
				words.extend(filter_text(word).split())
			y += 1


		ph = []
		t = []

		lst = []
		lst1 = block.split('\n')
		for i in range(0, len(lst1)):
			lst.extend(lst1[i].split('href="'))


		f = open('text.txt', 'w', encoding='utf-8')
		for i in range(0, len(lst)):
			f.write(str(lst[i]) + '\n')

		for i in range(0, len(lst)):
			t.clear()
			ans = ''
			ans1 = ''
			s = str(lst[i])
			for j in range(0, len(s)):
				if(s[j] in RUS):
					ans += s[j]

				'''
			for j in range(1, len(ans)):
				if(ans[j] == ' ' and ans[j-1] == ' '):
					t.append(j-1)
			ans1 = ans
			for j in range(0, len(t)):
				if(ans1[t[j]] == ' '):
					ans = remove_at(t[j], ans)
			'''
			if(len(ans) > 2):
				ph.append(str(ans))
		print(ph)




	
			

		#phrases(words, lst)


		proverka = set()

		#f = open('test.txt', 'r')

		for i in range(0, len(qst)):
			reference = ''

			pair1 = str(change(words, str(qst[i])))
			string = comp(lst, reference, pair1)


			for j in range(0, len(ph)):
				if(ph[j].find(pair1) != -1):
					pair1 = ph[j]
					print(ph[j])

			#print(pair1)

			if(string not in proverka and string != 'Нет такой ссылки, попробуйте поменять запрос'):
				pair = (pair1, string)
				utoch.append(pair)
				proverka.add(string)

		if(len(proverka) == 0):
			bot.send_message(message.chat.id, 'Нет такой ссылки, попробуйте поменять запрос')
		
		if(len(utoch)>1):
			bot.send_message(message.chat.id, 'Пожалуйста, уточните запрос.')
			b = message.chat.id
			itembtn = [0]*len(utoch)
			markup = types.ReplyKeyboardMarkup(row_width=1)
			
			for i in range(0, len(utoch)):
				if(utoch[i][0] in summary):
					print(summary[0])
				num = ''
				num += str(i+1)
				num += '.'
				num += utoch[i][0]
				bot.send_message(message.chat.id, num)
				itembtn[i] = types.KeyboardButton(str(i+1))
				markup.row(itembtn[i])
			bot.send_message(b, "По какому пункту вы хотите получить информацию?", reply_markup=markup)
			bot.register_next_step_handler(message, fun)

		elif(len(utoch) == 1):
			bot.send_message(message.chat.id, utoch[0][1])	

	#except:
		#bot.send_message(message.chat.id, "ОШИБКА!")


def fun(message):
	question = message.text
	question = int(question)
	bot.send_message(message.chat.id, utoch[question-1][1])

def phrases(words, lst):
	f = open('test.txt', 'w')
	string1 = ''
	string2 = ''
	

	for i in range(0, len(words)):
		cnt = 0
		slovo = words[i]
		reference = ''
		string1 = comp(lst, reference, words[i])
		
		for j in range(i+1, len(words)):
			slovo1 = slovo + ' ' + words[j]
			string2 = comp(lst, reference, slovo1)
			if(string2 == string1):
				slovo += ' ' + words[j]
				cnt+=1
			else:
				break
		i+=cnt
		f.write(slovo + '\n')




def ans1(message):
	try:
		st = str(message.text)
		first = st.split()[0]
		second = st.split()[1]

		f = 0 
		s = 0

		for i in range (1, 6):
			a = random.randint(1, 10)
			if(a < 8):
				time.sleep(1)
				e = first + " ГОЛ!"
				bot.send_message(message.chat.id, e)
				f += 1
			else:
				time.sleep(1)
				e = first + " Промазал(а)!"
				bot.send_message(message.chat.id, e)
			a = random.randint(1, 10)
			if(a < 8):
				time.sleep(1)
				e = second + " ГОЛ!"
				bot.send_message(message.chat.id, e)
				s += 1
			else:
				time.sleep(1)
				e = second + " Промазал(а)!"
				bot.send_message(message.chat.id, e)

		if f == s:
			bot.send_message(message.chat.id, "Доп. удары")
		while f == s:
			a = random.randint(1, 10)
			if(a < 8):
				time.sleep(1)
				e = first + " ГОЛ!"
				bot.send_message(message.chat.id, e)
				f += 1
			else:
				time.sleep(1)
				e = first + " Промазал(а)!"
				bot.send_message(message.chat.id, e)
			a = random.randint(1, 10)
			if(a < 8):
				time.sleep(1)
				e = second + " ГОЛ!"
				bot.send_message(message.chat.id, e)
				s += 1
			else:
				time.sleep(1)
				e = second + " Промазал(а)!"
				bot.send_message(message.chat.id, e)

		r = first + " " + str(f) + ":" + str(s) + " " + second
		bot.send_message(message.chat.id, r)
	except:
		bot.send_message(message.chat.id, "ОШИБКА!")

def rnd(message):
	try:
		s = str(message.text)
		b = message.chat.id
		b1 = int(s.split()[0])
		b2 = int(s.split()[1])

		if(b2 < b1):
			b1, b2 = b2, b1
		a = random.randint(b1, b2)
		bot.reply_to(message, a)
	except:
		bot.send_message(message.chat.id, "ОШИБКА!")

def weather(message):
	try:
		question = str(message.text)

		link = 'https://pogoda.mail.ru/prognoz/'
		link += question

		responce = requests.get(link).text


		soup = BeautifulSoup(responce, 'lxml')

		block = soup.find('div', class_='information__content__temperature')
		block = str(block)

		ans = ''

		for i in range(0, len(block)):
			if(block[i] == '/' and block[i+1] == 's' and block[i+2] == 'p' and block[i+3] == 'a' and block[i+4] == 'n'):
				j = i+6
				while(block[j] != '<'):
					ans += block[j]
					j+=1

		bot.send_message(message.chat.id, ans)
	except:
		bot.send_message(message.chat.id, "ОШИБКА!")

bot.polling(none_stop=True)