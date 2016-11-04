import discord
import asyncio
import string

client = discord.Client()

## Bot class								 ##
##		Manages the bot with owner blacklist ## 
##   	and game. It handles generic methods ##
##		that I felt like putting in. 		 ##
##											 ##
class Bot:
	def __init__(self):
		self.botOwner = None
		self.blacklist = []
		self.game = None
		self.inHelp = False
	
	## Method is called in on_ready to set the bot owner
	def setOwner(self, owner):
		self.botOwner = owner
	
	## Is method for when help is called. Will explain the game and answer questions
	## Should not be called while in game.
	async def help(self, msg):
		self.inHelp = True
		await client.send_message(msg.channel, 'You need help? With what?\n\nPress the number you need help with\:\n1. How to play Hangman\n2. What are the commands?\n3. How many max players?\n4.I don\'t even know dude, just lost...\n5. This bot is trash, I would like to complain\n\nType \'exit\' to exit')
		response = await client.wait_for_message(timeout = 60.30, author=msg.author, channel=msg.channel, check=checkNumberResponse)
		while(response != None and response.content != 'exit'):
			if(response.content == '1'):
				await client.send_message(msg.channel, 'How do you not know how to play Hangman!?\n\nJust try and guess the phrase or word. The dashes are letters in a word, and words are separated by two spaces. For this bot in particular, if You are playing Singleplayer game, you have 6 wrong guesses till you lose.\nMultiplayer games are a bit different...You can play cooperatively or head to head. Cooperatively allows 6 players,3 players, or 2 players while head to head allows unlimited amounts of players.\n\nType \"more\" for more about multiplayer.')
				response = await client.wait_for_message(timeout = 60.30, author=msg.author, channel=msg.channel, check=checkMore)
				if(response != None):
					await client.send_message(msg.channel, 'You want more ey?\n\nCooperative\: 6 players have 1 wrong guess each\n             3 players have 2 wrong guesses\n             2 players have 3 wrong guesses\nEvery player will have to op-in and each guess is turn based and everyone benefits from each other\'s guesses.\n\nHead-to-Head\: Everyone is on there own, and don\'t get to see everyone\'s guesses. Every player will have to op-in and everyone guesses once at the same time per round.Who ever guesses first, wins the game!')
					await client.send_message(msg.channel, 'I hope you understand now...')
			elif(response.content == '2'):
				await client.send_message(msg.channel, 'The commands are easy. \">startgame\" starts the game (as you already know), typing solo or together after that will start up a Singleplayer or Multiplayer game. Typing \">exit\" anytime will end the game if you are the game owner. Typing \">info\" anytime will give the server name and owner, players in game, whether the game is in progress and other information in the game.' )
			elif(response.content == '3'):
				await client.send_message(msg.channel, 'For cooperative play, there is only allowed 6, 3, or 2 players at a time, while for head to head play, there is an unlimited amount of players allowed.')
			elif(response.content == '4'):
				await client.send_message(msg.channel, 'Get your life together. Find a therepist maybe...Shit, I don\'t know how to help you.')
			elif(response.content == '5'):
				await client.send_message(msg.channel, 'Complain to your mom! Ha! Or you know, complain to Katie. But really, FUCK YOU! :) <3')
			await client.send_message(msg.channel, 'Do you need anything else?\n1. How to play Hangman\n2. What are the commands?\n3. How many max players?\n4.I don\'t even know dude, just lost...\n5. This bot is trash, I would like to complain\n\nType \'exit\' to exit')
			response = await client.wait_for_message(timeout = 60.30, author=msg.author, channel=msg.channel, check=checkNumberResponse)
		if(response == None):
			await client.send_message(msg.channel, 'I am just assuming you don\'t need anything then...Bye now!')
			self.inHelp = False
		else:
			await client.send_message(msg.channel, 'I hope I was helpful! Bye now!')
			self.inHelp = False
	
	## Deletes instance of game to end game. 
	async def exit(self, msg):
		## server host exit permission (right now is Katie)
		if(self.game != None and getName(msg.author) == getName(self.botOwner)):
			self.game = None
			await client.send_message(msg.channel, 'GameOwner has ended the game!')
		## gives game host permission to end hangman game
		elif(self.game != None and self.game.gameOwner == msg.author):
			self.game = None
			await client.send_message(msg.channel, 'Game owner has ended the game!')
		## sends message that you can not end game if you are not server host or game host
		else:
			await client.send_message(msg.channel, 'Sorry, you do not have permission to end game...')
	
	## Will give information about the server owner, current game, and possibly more.
	async def info(self, msg):
		await client.send_message(msg.channel, 'Not made yet!')
	
	
## Game class								 ##
##		Manages the game with attributes     ## 
##   	related to the game. It handles      ##
##		methods related to the game.    	 ##
##											 ##		
class Game:

	##temperary list for pictures of man hanging
	pictures = [1,2,3,4,5,6,7] 
		
	def __init__(self, gameOwnerp, kindOfGamep):
		self.inProgress = True
		self.gameOwner = gameOwnerp
		self.kindOfGame = kindOfGamep
		self.phrase = ' '
		self.dashedPhrase = ' '
		self.players = []
		self.splitPhraseList = []

	## Method that manages a Single player game 
	def StartSoloGame(self):
		print('inSoloGame')
	
	## Method that manages a Multiplayer game
	def StartTogetherGame(self):
		print('inTogetherGame')
	
	## Finds a random phrase from the internet. 
	## Currently not done yet.
	def RandomPhrase(self):
		print('in random')
		return "icecream is yummy"	
	
	## Will make a phrase replaced by dashes 
	def FindDashedPhrase(self):
		dashedList = []
		for word in self.splitPhraseList:
			dashedlist.append('_ ' *len(word))
		self.dashedPhrase = ' '.join(dashedList)
	
	## Checks if a certain player is playing. 
	def PlayerExists(self, playerSearch):
		return playerSearch in self.players
	
## Global bot object that does everything. 	
bot = Bot()

@client.event
async def on_ready():
	global bot
	print('logged in as')
	print(client.user.name)
	print('----------------')
	## Set Owner and send message to prefered text channel
	bot.setOwner(client.get_server("serverId").owner)
	await client.send_message(client.get_server("serverId").get_channel("channelId"), 'Hello, I am Hangman bot. You can type \">help\" while you aren\'t in a game for help. Type \">startgame\" to start a game!')
		

@client.async_event
async def on_message(message):
	global bot
	if message.content.lower() ==('>startgame'):
		if(bot.inHelp): ## If it is in help menu, do not start a game. 
			await client.send_message(message.channel, 'HEY! Wait your turn, someone is trying to get help. jeez...')
		else:
			if(bot.game!= None and bot.game.inProgress): ## Check if there is a current game.
				await client.send_message(message.channel, '{}{}{}'.format('There is already a game in progress, ', getName(message.author), "! You can play next time!"))
			else: ## If there is no current game, the bellow executes. 
				bot.game = Game(message.author, 'None')
				await client.send_message(message.channel,'{}{}{}'.format( 'Hello ',  getName(message.author), '! Let\'s play Hangman!\nType \"solo\" to play alone, and type \"together\" to play with friends!\nIf you don\'t know what to do, type \"help\"') )
				response = await client.wait_for_message(timeout = 60.30, author=message.author, channel=message.channel, check=checkGameKind)
				if(response != None):
					## Solo Game response
					if(response.content.lower() == 'solo'):
						await client.send_message(message.channel, 'Solo game? Okay! I will pick a phrase for you to guess!')
						bot.game = None
						bot.game = Game(message.author, 'solo')
						bot.game.StartSoloGame()
					## Together Game response
					elif(response.content.lower() == 'together'):
						await client.send_message(message.channel, 'Yay, I love playing with friends!')
						bot.game = None
						bot.game = Game(message.author, 'together')
						bot.game.StartTogetherGame()
				else: ## if(response != None):
					await client.send_message(message.channel, 'Time-out, You took too long to reply or I didn\'t understand what you were saying...')			
	elif(message.content.lower() == '>exit'): ## Exits current game
		await bot.exit(message)
	elif(message.content.lower() == '>info'): ## Gives information to the users
		await bot.info(message)
	elif(message.content.lower() == 'help'): ## Help command. 
		if(bot.game == None): ## Must not be in a game. 
			await bot.help(message)
		else:
			await client.send_message(message.channel, 'You can\'t do that while a game is in progress...')

## Returns name without #numbers at the end, or the nickname.		
def getName(messageAuthor):
	if(messageAuthor != None):
		if(messageAuthor.nick == None):
			'''fix'''
			str = messageAuthor.__str__()
			str = str.split("#")
			return str[0]
		else:
			return messageAuthor.nick

##					##
## Check Functions  ##
##			        ##
def checkGameKind(msg):
	return msg.content.lower() == 'solo' or msg.content.lower() == 'together'

def checkYesNo(msg):
	return msg.content.lower() == 'yes' or msg.content.lower() == 'no' 	

def checkPlay(msg):
	return msg.content.lower() == 'play'

def checkMore(msg):
	return msg.content.lower() == 'more'
	
def checkNumberResponse(msg):
	return msg.content.lower() == 'exit' or msg.content.lower() == '1' or msg.content.lower() == '2' or msg.content.lower() == '3' or msg.content.lower() == '4' or msg.content.lower() == '5'
	
## Bot token 	
client.run('token')