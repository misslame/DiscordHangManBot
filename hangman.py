import discord
import asyncio
import string
import bs4 as bs
import urllib.request
import re

from random import randint
from collections import namedtuple

client = discord.Client()

servertoken = 'SERVER ID'
channeltoken = 'DEFAULT CHANNEL ID'
bottoken = 'BOT TOKEN'

## Bot Class:
##	 Will manage the bot. 
##	 Can set a channel to message and play hangman in, change the owner of the bot
##	 and provides infor and help for the bot. 
class Bot:
	def __init__(self):
		self.botOwner = None
		self.game = None
		self.channel = None
		self.inSettings = False
		self.settingCaseSensitive = False
		self.settingGuessWord = False
	
	def set_owner(self, owner):
		self.botOwner = owner
	
	def set_channel(self, c):
		self.channel = c
	
	## Help Menu
	async def help(self):
		await client.send_message(bot.channel, '```Discord Hangman Bot:\n\tCommands:\n\t\t\'>startgame\' : Will start a new game if a game is not already in progress. \n\t\t\'>info\' : Will give information on the bot program itself.\n\t\t\'>exit\' : Will end the current game if you are the server owner or game host\n\t\t\'>settings\' : Will put you through a settings menu which will temperaryily disable the ability to make a game while in the menu. This command can not be used while in a game.\n\nThis bot has the capability of running a hangman game. If you want to enable word guesses or case sensitive guesses, go to the setting```') 

	async def exit(self, msg):
		## server host exit permission
		if(self.game != None and getName(msg.author) == getName(self.botOwner)):
			self.game = None
			await client.send_message(msg.channel, 'Server host has ended the game!')
		## gives game host permission to end hangman game
		elif(self.game != None and self.game.gameOwner == msg.author):
			self.game = None
			await client.send_message(msg.channel, 'Game owner has ended the game!')
		## sends message that you can not end game if you are not server host or game host
		else:
			await client.send_message(msg.channel, 'Sorry, you do not have permission to end game...')
	
	## Bot Information
	async def info(self, msg):
		if self.game.inProgress:
			str = "```Current status: Game in Progress\nThis Server\'s Bot Owner: "
		elif self.inHelp:
			str = "```Current status: Someone is getting help\nThis Server\'s Bot Owner: "
		else:
			str = "```Current status: Sitting idle\nThis Server\'s Bot Owner: "
		await client.send_message(msg.channel, '{}{}(){}'.format('Hangman Discord Bot\nCreated by: Katie (MissLame)\nGithub: https://github.com/misslame \nThis bot\'s repo:https://github.com/misslame/DiscordHangManBot \nVersion: In Development\n',str,getName(self.botOwner),'\n\nThank you for using my bot!```' ))
	
	## Settings Menu
	async def settings(self, msg):
		if(self.game is None and msg.author is self.botOwner):
			self.inSettings = True
			await client.send_message(bot.channel, '{}{}{}{}{}'.format('```Settings:\n\n1. Set allow case sensitive to ', not(self.settingCaseSensitive), '\n2. Set allow guessing words to ', not(self.settingGuessWord), '\n3. To set the text channel, @ bot in the text channel you want to set.\n\n Send number for menu option, or type, \'exit\' to exit```'))
			response = await client.wait_for_message(timeout = 60.30, author=msg.author, channel=bot.channel, check=checkNumberResponse)
			while(response is not None and response.lower() != 'exit'):
				if( response == '1'):
					await client.send_message(bot.channel, '{}{}'.format('You have set the current setting for allowing case sensitive to ', self.settingCaseSensitive))
				else:
					await client.send_message(bot.channel, '{}{}'.format('You have set the current setting for allowing word guesses to ', self.settingGuessWord))
				await client.send_message(bot.channel, '{}{}{}{}{}'.format('```Settings:\n\n1. Set allow case sensitive to ', not(self.settingCaseSensitive), '\n2. Set allow guessing words to ', not(self.settingGuessWord), '\n3. To set the text channel, @ bot in the text channel you want to set.\n\n Send number for menu option, or type, \'exit\' to exit```'))
				response = await client.wait_for_message(timeout = 60.30, author=msg.author, channel=bot.channel, check=checkNumberResponse)
			if(response is None):
				await client.send_message(bot.channel, 'Sorry, system timed out, you either did not respond or I did not understand you')
			self.inSettings = False
		else:
			await client.send_message(bot.channel, 'Sorry! There is a game in progress right now or you do not have permission to change the settings!')
	
	## Sets the game object to a new game with settings.
	def set_game(self, gameOwnerp):
		if(not(self.inSettings)):
			self.game = Game(gameOwnerp, self.settingGuessWord, self.settingCaseSensitive)


Player = namedtuple('Player',['name','score'])

## Game Class:
## 	 Class that manages hangman. 
## 	 contains methods that will manage and run the game. 		
class Game:
	## **IN PROGRESS** Will be a constant of photos depicting the hangman 
	pictures = [1,2,3,4,5,6,7]
		
	def __init__(self, gameOwnerp, guessWord, caseSensitive):
		self.gameOwner = gameOwnerp
		self.inProgress = True
		self.players = []
		self.phrase = ''
		self.originalPhrase = ''
		self.definition = ''
		self.dashedPhrase = ''
		self.incorrectI = 0
		self.guessWord = guessWord
		self.caseSensitive = caseSensitive
		
	
	## Checks if a player exists already on the players list
	def player_exists(self, playerSearch):
		return any(playerSearch in name for name in self.players)
		
	def update_player_score(self, player):
		for i in range(len(self.players)):
			if (self.players[i].name.lower() == player.lower()):
				self.players[i] = self.players[i]._replace(score=(self.players[i].score+1))
				return True
		return False
		
	## Sets the game owner as the first player. 
	def initialize_players(self):
		self.players.append(Player(getName(self.gameOwner), score=0))
	
	## Adds a player to the players list if they are not already
	async def add_player(self, msg):
		if(self.player_exists(getName(msg.author))):
			await client.send_message(msg.channel, '{}{}'.format('You are already in the game, ', getName(msg.author)))
		else:
			self.players.append(Player(getName(msg.author), score=0))
			await client.send_message(msg.channel, '{}{}'.format('You were added to the game, ', getName(msg.author)))
		print(self.players)
	
	async def print_current_players(self, msg):
		s = ''
		for p in self.players:
			s += p.name + ' \n'
		await client.send_message(msg.channel, '{}{}'.format('The current players are ', s ))
	
	## Uses BeautifulSoup4 parses urbandictionary random page. 
	def retrieve_random_phrase(self):
		pg = randint(1,3000)
		url = 'https://www.urbandictionary.com/random.php?page=' + str(pg)
		sauce = urllib.request.urlopen(url).read()
		soup = bs.BeautifulSoup(sauce, 'lxml')
		
		self.originalPhrase = soup.title.text
		print(self.originalPhrase)
		##Allows no special characters except spaces 
		self.phrase = re.sub('[^A-Za-z0-9 ]+', '',(soup.title.text))
		if(not(self.caseSensitive)):
			self.phrase = self.phrase.lower()
		print(self.phrase)	
		self.phrase = self.phrase[17:]

		self.definition = soup.find('div',class_='meaning').text
		## **Debug**
		print(self.phrase)
		print(self.definition)
	
	## splits the phrase in to a list of words, and then splits each word in to a dashed list. 
	def find_dashed_phrase(self):
		dashedList = []
		splitPhraseList = self.phrase.split(' ')
		print(splitPhraseList)
		for word in splitPhraseList:
			dashedList.append('_ ' *len(word))
		self.dashedPhrase = '  '.join(dashedList)
		## **Debug**
		print(self.dashedPhrase)
	
	## **START GAME METHOD**
	async def start_game(self, msg):
		self.initialize_players()
		await self.print_current_players(msg)
		await client.send_message(msg.channel, 'How to play:\n If you want to guess a letter just @ me, and then put your letter any larger than a single letter will be assummed to be a phrase. If you get the phrase wrong, you are out of the game')
		self.retrieve_random_phrase()
		self.find_dashed_phrase()
		await self.update_board(msg)
	
	## Returns a list of all the indexes the character guess is
	##    ** Only a character passed in will work
	def find_all_indexes_of(self, guess):
		return [i for i, ltr in enumerate(self.phrase) if ltr == guess]
	
	## Replaces a single dash in the dashed phrase from char guesses
	def replace_dash(self, guess):
		indexedList = self.find_all_indexes_of(guess)
		for i in indexedList:
			self.dashedPhrase = self.dashedPhrase[:(i*2)]+ guess + self.dashedPhrase[(i*2)+1:]
		## **Debug**
		print(self.dashedPhrase)
	
	## Replaces multiple dashes in the dashed phrase from a phrase guess
	##    **KNOWN BUG**
	##		 - When guessed phrase appears multiple times in the original phrase
	##	  **Future Fix**
	def replace_dashes(self, guess):
		startIndex = ((re.search(r'\b%s\b'%guess,self.phrase)).start())* 2
		guess = " ".join(guess)
		endIndex = startIndex + (len(guess)-1)
		self.dashedPhrase = self.dashedPhrase[:startIndex] + guess + self.dashedPhrase[endIndex + 1:]
	
	## Returns true if guess is correct but also updates the dashed phrase.
	def check_guess(self, guess):
		if(guess in self.phrase):
			if(len(guess) is 1):
				self.replace_dash(guess)
			elif(self.guessWord):
				self.replace_dashes(guess)
			else:
				self.incorrectI += 1
				return False
			return True
		else:
			self.incorrectI += 1
			return False
	
	async def update_board(self, msg):
		print(self.incorrectI)
		await client.send_message(msg.channel, '{}{}{}{}{}'.format('``` Word:\n',self.dashedPhrase,'\n Incorrect guesses: ', self.incorrectI, '```'))
	
	def check_win(self):
		if('_' not in self.dashedPhrase):
			return self.end_game(True)
		elif(self.incorrectI is 6):
			return self.end_game(False)
		return None
	
	## ** END GAME **
	def end_game(self, isWin):
		p = ''
		for i in self.players:
			p += i.name + '  ' + str(i.score) + '\n'
		if isWin:
			return '``` Game Over!\n\n' + p + '\n' + 'You guessed the correct phrase before hanging the man! ```'
		else:
			return '``` Game Over!\n\n' + p + '\n' + 'You did not guess it. :( ```'
			
		
## Global variable that runs bot				
bot = Bot()

@client.event
async def on_ready():
	global bot
	print('logged in as')
	print(client.user.name)
	print('----------------')
	await client.change_presence(game=discord.Game(name='HANGMAN BABY!'))
	bot.set_owner(client.get_server(servertoken).owner)
	bot.set_channel(client.get_server(servertoken).get_channel(channeltoken))
	await client.send_message(bot.channel, 'Hello, I am Hangman bot. You can type \"help\" while you aren\'t in a game for help. Type \">startgame\" to start a game!')
		

@client.async_event
async def on_message(message):
	if(client.user.mentioned_in(message)):
		if(message.channel == bot.channel):	
			if(message.content[23:] == ' '):
				await client.send_message(bot.channel, '{0.author.mention} You called? What do you want?'.format(message))
			elif(bot.game is not None and bot.game.inProgress):
				if(bot.game.player_exists(getName(message.author))):
					if(bot.game.check_guess(message.content[23:])):
						await client.send_message(bot.channel, '{0.author.mention} guessed right!'.format(message))
						bot.game.update_player_score(getName(message.author))
					else:
						await client.send_message(bot.channel, '{0.author.mention} guessed wrong!'.format(message))
					saved = bot.game.check_win()
					await bot.game.update_board(message)
					if saved is not None:
						await client.send_message(bot.channel, saved)
						bot.game = None
				else:
					await client.send_message(bot.channel, '{0.author.mention} you have to op-in to the game by saying \"here\"'.format(message))
			else:
				await client.send_message(bot.channel, 'I am currently idle, type \"help\" for help and commands, \">startgame" to start a game!')
		else:
			if(message.author == bot.botOwner):
				await client.send_message(message.channel, 'Would you like to set this channel as the text channel to hold games?')
				response = await client.wait_for_message(timeout = 60.30, author=message.author, channel=bot.channel, check=checkYes)
				if response is not None:
					bot.game.set_channel(message.channel)
			else:
				await client.send_message(bot.channel, 'Hey, {0.author.mention} I am authorized to host games in this text channel, hang with me here! ;)'.format(message))
	elif(message.channel == bot.channel):
		if message.content.lower() == ('>startgame'):
			if(bot.game != None and bot.game.inProgress):
				await client.send_message(bot.channel, '{}{}{}'.format('There is already a game in progress, ', getName(message.author), "! You can play next time!"))
			else: 
				await client.send_message(bot.channel,'{}{}{}'.format( 'Hello ',  getName(message.author), '! Let\'s play Hangman!\nType \"ready\" to start the game! other players type \"here\" to join the game!\nIf you don\'t know what to do, type \"help\"') )
				response = await client.wait_for_message(timeout = 60.30, author=message.author, channel=bot.channel, check=checkReady)
				bot.set_game(message.author)
				if(response != None):
					await client.send_message(bot.channel, 'I will start the game in 3...2...1...NOW!')
					await bot.game.start_game(message)
				else:
					await client.send_message(bot.channel, 'Time-out, You took too long to reply or I didn\'t understand what you were saying...')
					bot.game = None
		elif(message.content.lower() == '>exit'):
			await bot.exit(message)
		elif(message.content.lower() == '>info'):
			await bot.info(message)
		elif(message.content.lower() == 'help'):
			await bot.help()
		elif(message.content.lower() == '>setting' and message.author == bot.botOwner):
			await bot.settings(message)
		elif(message.content.lower() == 'here' and bot.game != None):
			await bot.game.add_player(message)
			
def getName(messageAuthor):
	if(messageAuthor != None):
		if(messageAuthor.nick == None):
			'''fix'''
			str = messageAuthor.__str__()
			str = str.split("#")
			return str[0]
		else:
			return messageAuthor.nick
			
def checkReady(msg):
	return msg.content.lower() == 'ready'

def checkYes(msg):
	return msg.content.lower() == 'yes' or msg.content.lower() == 'y'

def checkNumberResponse(msg):
	return msg.content.lower() == 'exit' or msg.content.lower() == '1' or msg.content.lower() == '2'
	
## Bot token 	
client.run(bottoken)