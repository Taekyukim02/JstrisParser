# data handling
import numpy as np
import pandas as pd

# graphic data
import pyautogui as py
from PIL import ImageGrab

# keyboard detection
from pynput import keyboard
import mss

import time


### CUSTOM DEFINITIONS ###

class KeyMap:	
	# key mappings
	ccw = keyboard.KeyCode.from_char("q")
	cw = keyboard.KeyCode.from_char("w")
	rot180 = keyboard.KeyCode.from_char("p")
	hold = keyboard.KeyCode.from_char("e")
	left = keyboard.Key.left
	right = keyboard.Key.right
	softdrop = keyboard.Key.down
	harddrop = keyboard.Key.up

	# key list
	key_list = [ccw, cw, rot180, hold, left, right, softdrop, harddrop]


# black:	RGB(red=0, green=0, blue=0)
# line: 	RGB(red=1, green=155, blue=213)
# yellow:	RGB(red=228, green=159, blue=31)
# purple:	RGB(red=176, green=41, blue=136)
# orange:	RGB(red=228, green=91, blue=14)
# blue:		RGB(red=31, green=65, blue=195)
# green:	RGB(red=88, green=177, blue=36)
# red:		RGB(red=216, green=15, blue=54)
def get_color(pixRGB):
	mapping = {
		0: "empty",
		155: "I",
		159: "O",
		41: "T",
		91: "L",
		65: "J",
		177: "S",
		15: "Z",
	}	
	return mapping.get(pixRGB[1], None)



### GLOBAL VARIABLES ###

# initialize pandas dataframe of moves
max_moves = 1000
moves = pd.DataFrame(index=np.arange(0, max_moves), columns=("move", "block1", "block2", "tot_time", "think_time", "place_time", "switch_time", "switched"))
move_index = 0

# observe pixels and keyboard presses
start = time.time()
move_start = time.time()
switch_start = move_start



def update(monitor, block_location):

	sct = mss.mss()

	# callback functions
	def on_press(key):
		global max_moves, moves, move_index, start, move_start, switch_start

		if(key == KeyMap.harddrop):
			print("end move")
			move_end = time.time()
			move_index = move_index + 1
				
			# get new block
			img = np.array(sct.grab(monitor))
			pixRGB = img[block_location[0]*2, block_location[1]*2, ]
			moves.loc[move_index]["block1"] = get_color(pixRGB)
			return

		elif(key == KeyMap.hold and move_index > 0):
			print("pressed hold")
			img = np.array(sct.grab(monitor))
			pixRGB = img[block_location[0]*2, block_location[1]*2, ]
			moves.loc[move_index]["block2"] = get_color(pixRGB)
			return

		elif(key in KeyMap.key_list):
			print("made move")


		else:
			print("pressed other key:", key)
			return
				
	# don't do anything when key is released
	def on_release(key):
		return

	#with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
		#listener.join()

	listener = keyboard.Listener(on_press=on_press, on_release=on_release)
	listener.start()

	while 1:
		pass

		


def main():

	# find matrix location
	print("Finding the board...")
	newgame_location = None
	while(newgame_location == None):
		print("Please ensure \"New Game\" button is visible on screen.")
		newgame_location = py.locateOnScreen('./assets/newgame.png')

	square_length = 24 		# width / length of square in matrix
	matrix_height = square_length * 20
	matrix_width = square_length * 10

	monitor = {"top": newgame_location.top//2 - 502, "left": newgame_location.left//2 - 145, "width": matrix_width, "height": matrix_height}
	

	# important locations relative to matrix
	go_location = (124, 290)
	block_location = (square_length//2, 9*square_length//2)


	# wait until game starts
#	go_color = py.pixel(710, 473)[0]
#	print(go_color)

	# run game
	try:
		print("Parsing jstris...")
		update(monitor, block_location)
	except KeyboardInterrupt: # If Ctrl + C input
		exit('Ctrl + C Input - Terminating')


if __name__ == '__main__':
	main()
