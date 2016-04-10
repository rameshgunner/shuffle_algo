#/usr/bin/python

import os, subprocess, pygame, sys, tty, termios
from random import randint,random
from datetime import datetime
from time import time
from threading import Thread
from copy import deepcopy


playbox = os.getcwd()+'/PlayBox/'
songs = []
durations = []
playlist = []
play_probablity = []
tolerance = .5
hour_tolerance = 3


#file_system music lookup
for path, subdirs, files in os.walk(playbox):

	for name in files:
		
		#song duration
		duration = subprocess.check_output(['exiftool '+playbox+'\''+name+'\' | grep Duration'], shell= True)[34:-10].split(':')
		duration = int(duration[0])*3600+int(duration[1])*60+int(duration[2])
		
		#song list
		songs.append(name)
		durations.append(duration)
		#play_probablity.append(10)#randint(0,5))


#knock-off
def knock_off(playlist):
	
	
	#information for each song. Name, play frequence, play time and portion listened
	song_info = []
	for song in playlist:
		song_info.append([song, 0, [0]*24, None ])

	for play_instance in access_db():
		
		play_instance = play_instance[:-1].split('\t')
		
		if play_instance[0] in playlist:
			
			song_no = playlist.index(play_instance[0])
			song_info[song_no][0] = play_instance[0]
			song_info[song_no][1]+=1
			song_info[song_no][2][ int(play_instance[1])-1 ]+=1
			song_info[song_no][3] = play_instance[3]
	
	now = int(datetime.now().strftime('%H'))
	max_played = max(zip(*song_info)[1])
	
	#knock off songs which are less popular
	for song in song_info:
		
		max_play_hour = [i for i, x in enumerate(song[2]) if x == max(song[2])]

		played_often = song[1] > randint(0,max_played)
		
		played_almost_complete = random() < song[3]

		played_around_now = []
		for play_hour in max_play_hour:
			if abs(now - play_hour) < hour_tolerance:
				played_around_now.append(True)

		if not (played_often and played_around_now and played_almost_complete) and random()<tolerance:
			song_info.pop( song_info.index(song) )
	
	return list(zip(*song_info)[0])



#fisher-yates
def shuffle_playlist():
	
	playlist = knock_off(deepcopy(songs))
	
	for i in range(len(playlist)-1,-1,-1):

		random_song = randint(0,i)
		playlist[random_song] , playlist[i] = playlist[i] , playlist[random_song]
		#play_probablity[random_song] , play_probablity[i] = play_probablity[i] , play_probablity[random_song]
	
	return playlist


#copy-paste
def getch():
	try:	
		fd = sys.stdin.fileno()
	except ValueError:
		pass
	old_settings = termios.tcgetattr(fd)
	try :
		tty.setraw(fd)
		ch = sys.stdin.read(1)
	finally :
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch


#show_cli
def show_cli(msg,song,playlist):
	print playlist	
	gui = open('say_gui','w')

	gui.write('All Songs\n\n')
	
	for song in playlist:
		gui.write( song+'\n' )
	gui.write('\n')

	gui.write(msg+song)
	gui.close()


def update_db(song,portion_played):

	#open new song db ani pass chainna
	csv = open('history.csv','a')
	csv.write( song+'\t'+datetime.now().strftime('%H')+'\t'+'GPS'+'\t'+str(portion_played)+'\n')
	csv.close()
	###song id/time/date/gpsko lai kei/yadayadayada


def access_db():

	return open('history.csv','a+').readlines()


keystrokes = []
def user_input():

	global keystrokes
	while True:
		keystrokes.append(getch())


def play():
	
	play_state = True
	pygame.init()
	
	while True:

		global keystrokes
		playlist = shuffle_playlist()

		for song in playlist:
			
			show_cli('Now Playing...\t',song,playlist)
			update_db(song,1)

			pygame.mixer.music.load(playbox+song)
			pygame.mixer.music.play()
			
			user_control = Thread(target = user_input)
			user_control.start()

			start_time = time()

			duration = durations[songs.index(song)]
			while time() - start_time < duration:
			
				#print durations[songs.index(song)] - (time() - start_time) ###################################         JUST 4 FUN

				action = None
				if keystrokes != []:
					action = keystrokes.pop(0).lower()

				if action=='n':
					update_db(song,float( (time()-start_time)/duration ))
					break

				if action=='p':

					if play_state:
						show_cli('Paused...\t',song,playlist)
						pygame.mixer.music.pause()
					else:
						show_cli('Now Playing...\t',song,playlist)
						pygame.mixer.music.unpause()
					play_state = not play_state
				
				if action=='q':
					return


play()
pygame.quit()
quit()
