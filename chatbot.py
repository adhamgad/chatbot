from fysom import *
import sys
import nltk
from difflib import SequenceMatcher as SM
import random
import string 
import datetime
import pickle

knowledge = {("what is your name"): 
					["A bot has no name.",
					 "You can call me anything I'm a bot anyway"],

			("hi", "hello", "hey"):
					["HI THERE!",
					 "HI!"],

			("i want to go to", "i want to make", "i want to reserve", "i want to book", "i want to stay for"):
					["Sure"],

			("who are you"):
					["I'M AN A.I PROGRAM."],

			("thank you","thanks"):
					["YOU ARE WELCOME!",
					 "YOU ARE A VERY POLITE PERSON!",
					 "NO PROBLEM!"]}


months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
			  'August', 'September', 'October', 'November', 'December']

season = {"Winter":1, "Spring": 4 , "Summer":6, "Autumn": 10}

fsm = Fysom({
	"initial":"welcome",
	"events":[
	{"name": "name", "src":"welcome","dst":"name"},
	{"name": "age", "src":"name", "dst": "age"},
	{"name": "name_age", "src":"welcome", "dst": "name_age"},
	{"name": "nationality", "src":["name","age","name_age"], "dst":"nationality"},
	{"name": "package", "src":["name","age","name_age","nationality"], "dst":"package"},
	{"name": "period", "src":"package", "dst":"period"},
	{"name": "exit", "src":["welcome","name","age","name_age","nationality","package","period"], "dst": "exit"}
	]
	})

load_models_flag = False
model = None
vectorizer = None

def load_models():
	if load_models_flag:
		model = pickle.load(open('model.sav', 'rb'))
		vectorizer = pickle.load(open('vectorizer.sav', 'rb'))
	return model, vectorizer

def predict_sentiment(text):
	if load_models_flag == True:
		if model.predict(vectorizer.transform([text]))[0] == 0:
			msg = "would you like to talk to a sales representative? \n"
			user_input = confirmation(msg)
			if user_input == True:
				print "You'll now talk with a sales representative"
				sys.exit()

	
class User:
	def __init__(self):
		self.name = ""
		self.age = 0
		self.nationality = ""
		self.occupation = ""
		self.destination = ""
		self.checkin_date = ""
		self.checkin_month = ""
		self.checkout_date = ""
		self.checkout_month = ""



def jump_to(state_name):
	if state_name == "name":
		fsm.name()
	if state_name == "name_age":
		fsm.name_age()
	elif state_name == "age":
		fsm.age()
	elif state_name == "nationality":
		fsm.nationality()
	elif state_name == "period":
		fsm.period()
	elif state_name == "package":
		fsm.package()
	elif state_name == "exit":
		fsm.exit()

def preprocess_string(user_input):
	user_input = user_input.lower().strip()
	return user_input


def match_with_kb(user_input):
	user_input = preprocess_string(user_input)

	jump = None
	answer = ""
	for sent in nltk.sent_tokenize(user_input):
		max_sim = ""
		max_ratio = 0
		flag = False
		for keys, v in knowledge.iteritems():
			if sent in keys:

				answer = answer + random.choice(v) + " "
				if random.choice(v) == "Sure":
					#jump_to("package")
					#package()
					jump = "package"
				flag = True
				break
			else:
				if type(keys) == str:
					
					ratio = SM(None, keys, sent).ratio()
					if ratio > max_ratio:
						max_ratio = ratio
						max_sim = keys
				else:
					for key in keys:
						
						ratio = SM(None, key, sent).ratio()
						if ratio > max_ratio:
							max_ratio = ratio
							max_sim = key

		if (max_ratio > .5) and (flag == False):
			for keys, v in knowledge.iteritems():
				if max_sim in keys:
					answer = answer + random.choice(v) + " "
					if random.choice(v) == "Sure":
						#jump_to("package")
						#package()
						jump = "package"
	sys.stdout.write(answer)
	return jump	

def welcome(destination = None):
	sys.stdout.write("Hello, ")
	jump_to("name_age")


def confirmation(msg):
	user_input = raw_input(msg)
	predict_sentiment(user_input)
	jump = match_with_kb(user_input)
	if jump != None:
		jump_to(jump)


	user_input = preprocess_string(user_input)

	for sent in nltk.sent_tokenize(user_input):
		sent = sent.translate(None, string.punctuation)
		if sent in ["yes", "yeah", "yea"]:
			return True
		elif sent == "":
			return confirmation(msg)
		else:
			return False

def name_age():
	user_input = raw_input("Can you please tell me your name, age ? \n")
	predict_sentiment(user_input)
	jump = match_with_kb(user_input)
	if jump != None:
		jump_to(jump)
		return "",""
	else:
		jump_to("nationality")
	user_name = name(user_input)
	user_age = age(user_input)


	#to_confirm = raw_input("Just to confirm, your name is %s & your age is %s ? \n" %(user_name, user_age))
	msg = "Just to confirm, your name is %s & your age is %s ? \n" %(user_name, user_age)
	
	if not confirmation(msg):
		user_name = name(name_only = True)
		user_age = age(age_only = True)

	if jump != None:
		jump_to(jump)
		user_name, user_age

	return user_name, user_age

# def get_entity(named_entities, entity_type):
# 	for t in named_entities.subtrees():
# 		if t.label() == entity_type:
# 			return t.leaves()[0][0]


def name(user_input = "", name_only = False):
	if name_only:
		user_input = raw_input("Can you please tell me your name? \n")
		predict_sentiment(user_input)
	tokens, tagged, named_entities = extract_tags(user_input)

	user_name = ""

	for t in named_entities.subtrees():
		if t.label() == "PERSON":
			user_name = t.leaves()[0][0]
	
	if user_name == "":
		for pos in tagged:
			if pos[1] == "NNP":
				user_name = pos[0] 
		if user_name == "":
			user_name = name(name_only= True)
	
	if name_only:
		msg = "Just to confirm, your name is %s ? \n" % user_name		
		if confirmation(msg):
			return user_name
		else:
			name(name_only = True)

	return user_name


def age(user_input = "", age_only = False):
	if age_only:
		user_input = raw_input("Can you please tell me your age? \n")
		predict_sentiment(user_input)

	tokens, tagged, named_entities = extract_tags(user_input)
	user_age = 0
	for pos in tagged:
		if pos[1] == "CD":
			user_age = pos[0]
	if user_age == 0:
		user_age = age(age_only= True)

	if age_only:
		msg = "Just to confirm, your age is %s ? \n" % user_age
		if confirmation(msg):
			return user_age
		else:
			age(age_only = True)

	return user_age



def nationality():
	user_input = raw_input("Where are you from? \n")
	predict_sentiment(user_input)
	tokens, tagged, named_entities = extract_tags(user_input)
	nation = ""
	for t in named_entities.subtrees():
		if t.label() == "GPE":
			nation = t.leaves()[0][0]
	if nation == "":
		nationality()

	msg = "Just to confirm, you're from %s ? \n" % nation
	if confirmation(msg):
		jump_to("package")
	else:
		nationality()

	return nation

		

def period(destination, checkin_date, checkin_month, checkout_date, checkout_month):
	checkin_season = ""
	checkin_month_num = datetime.datetime.strptime(checkin_month, '%B').date().month
	for s, v in season.iteritems():
		if checkin_month_num >= v:
			checkin_season = s

	out = ""
	if destination == "Egypt":
		if (checkin_season == "Winter") or (checkin_season == "Autumn"):
			msg = "so we have a package from %s %s to %s %s, in Cairo, including a Nile cruise and a Pyramids visit.  Would   you   like  reserve? " %(checkin_date, checkin_month, checkout_date, checkout_month)
		else:
			msg = "so we have a package from %s %s to %s %s, in Alexandria,  Would   you   like  reserve? " %(checkin_date, checkin_month, checkout_date, checkout_month)
	else:
		if (checkin_season == "Winter") or (checkin_season == "Autumn"):
			msg = "so we have a package from %s %s to %s %s, in %s . Would   you   like  reserve? " %(checkin_date, checkin_month, checkout_date, checkout_month,destination)
		else:
			msg = "so we have a package from %s %s to %s %s, in %s . Would   you   like  reserve? " %(checkin_date, checkin_month, checkout_date, checkout_month,destination)


	if confirmation(msg):
		print "Great!"
	else:
		print "Ok let us know when you change your mind"

def extract_destination(user_input = "", out = False):
	if out == True:
		user_input = raw_input("Please re-enter your destination \n")
		predict_sentiment(user_input)
	tokens, tagged, named_entities = extract_tags(user_input)
	destination = ""
	for t in named_entities.subtrees():
		if t.label() == "GPE":
			destination = t.leaves()[0][0]
	if destination == "":
		return extract_destination(out = True)
	return destination

#i'm adham gad 23 years old
#I wanna go to roma from 23 oct to 30 nov

def extract_checkin(user_input, out = False):
	if out == True:
		user_input = raw_input("Please re-enter your checkin date \n")
		predict_sentiment(user_input)
	tokens, tagged, named_entities = extract_tags(user_input)
	checkin = 0
	for i,pos in enumerate(tagged):
		if pos[1] == "CD":
			if checkin == 0:
				checkin = pos[0]
				checkin_index = i

	if checkin == 0:
		extract_checkin(out = True)
	if out == True:
		checkin_index = 0

	return checkin, checkin_index

def extract_checkout(user_input = "", out = False):
	if out == True:
		user_input = raw_input("Please re-enter your checkout date \n")
		predict_sentiment(user_input)
	
	tokens, tagged, named_entities = extract_tags(user_input)
	checkout = 0
	for i,pos in enumerate(tagged):
		if pos[1] == "CD":
			if checkout == 0:
				checkout = pos[0]

	if checkout == 0:
		extract_checkout(out = True)

	return checkout


def extract_checkin_out(user_input = "", checkin_only = False, checkout_only = False):
	checkin = 0
	checkout = 0
	checkin_index = -1

	tokens, tagged, named_entities = extract_tags(user_input)
	for i,pos in enumerate(tagged):
		if pos[1] == "CD":
			if checkin == 0:
				checkin = pos[0]
				checkin_index = i
			else:
				checkout = pos[0]
				# checkout_index = i

	if checkin == 0:
		checkin, checkin_index = extract_checkin(user_input)
	if checkout == 0:
		checkout = extract_checkout(user_input)

	nnps = []
	checkin_out = []
	
	if checkin_index != -1:
		start = checkin_index - 4
		if start < 0:
			start = 0
		for pos in tagged[start:]:
			if (pos[1] == "NNP") or (pos[1] == "NN") :
				nnps.append(pos[0])

	for nnp in nnps:
		for month in months:
			if (nnp in month[:4]) or (nnp == month):
				checkin_out.append(month)
	
	checkin_month = checkin_out[0]
	if len(checkin_out) == 1:
		checkout_month = checkin_out[0]
	else:
		checkout_month = checkin_out[1]


	return checkin, checkin_month, checkout, checkout_month


def package():
	user_input = raw_input("Please enter your destination, check-in & check-out dates \n")
	predict_sentiment(user_input)
	#tokens, tagged, named_entities = extract_tags(user_input)
	
	destination = ""
	destination = extract_destination(user_input)


	checkin_date, checkin_month, checkout_date, checkout_month = extract_checkin_out(user_input)
	msg = "Just to confirm, your destination is %s, check-in %s %s & check-out %s %s ? \n" % (destination, checkin_date, checkin_month, checkout_date, checkout_month)
	if confirmation(msg):
		jump_to("period")
		return destination, checkin_date, checkin_month, checkout_date, checkout_month 
	else:
		package()


def extract_tags(user_input): 
	user_input = user_input.title()
	tokens = nltk.word_tokenize(user_input) 
	tagged = nltk.pos_tag(tokens)
	named_entities = nltk.ne_chunk(tagged)
	return tokens, tagged, named_entities




if __name__ == "__main__":
	user = User()
	current_state = None
	load_models_flag = False 
	if load_models_flag:
		model, vectorizer = load_models()
	while(current_state != "exit"):
		current_state = fsm.current
		switcher = {
			"welcome": welcome,
			"name_age": name_age,
			"name": name,
			"age": age,
			"nationality": nationality,
			"period": period,
			"package": package,
			"exit": exit
		}
		state = switcher.get(current_state, "No state")
		if state.__name__ == "welcome":
			state()
		if state.__name__ == "name_age":
			user.name,user.age = state()
		if state.__name__ == "nationality":
			user.nationality = state()
		if state.__name__ == "package":
			user.destination, user.checkin_date, user.checkin_month, user.checkout_date, user.checkout_month = state()

		
		if state.__name__ == "period":
			period(user.destination, user.checkin_date, user.checkin_month, user.checkout_date, user.checkout_month)
			sys.exit()


