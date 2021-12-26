import numpy as np
import pandas as pd
import pyautogui as py
import keyboard
import time


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
	return mapping.get(pixRGB.green, None)


def pressed_hold_key(event):
	print("yes")


def update(block_location):

	# key mappings
	ccw_key = "q"
	cw_key = "w"
	hold_key = "e"
	left_key = "left"
	right_key = "right"
	softdrop_key = "down"
	harddrop_key = "up"

	# initialize pandas dataframe of moves
	max_moves = 1000
	moves = pd.DataFrame(index=np.arange(0, max_moves), columns=("move", "block1", "block2", "tot_time", "think_time", "place_time", "switch_time", "switched"))
	move_index = 0

	# callback function
	def on_hold_key(event):
		print("pressed hold_key")
		pixRGB = py.pixel(block_location[0], block_location[1])
		moves.loc[move_index]["block2"] = get_color(pixRGB)

	# observe pixels and keyboard presses
	start = time.time()
	while 1:
		move_start = time.time()
		switch_start = move_start

		# get block1 and block2
		pixRGB = py.pixel(block_location[0], block_location[1])
		moves.loc[move_index]["block1"] = get_color(pixRGB)


		#keyboard.on_press_key(hold_key, on_hold_key)
		keyboard.on_press_key(hold_key, pressed_hold_key)

		print(moves.loc[move_index]["block2"])
		time.sleep(.1)

		move_end = time.time()

		# Put in all the time values


		move_index = move_index + 1


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
	matrix_location = (newgame_location.left - 147*2, newgame_location.top - 503*2)

	go_location = (matrix_location[0] + 124*2, matrix_location[1] + 290*2)
	block_location = (matrix_location[0] + 9*square_length, matrix_location[1] + square_length)


	# wait until game starts
#	go_color = py.pixel(710, 473)[0]
#	print(go_color)

	# run game
	try:
		print("Parsing jstris...")
		update(block_location)
	except KeyboardInterrupt: # If Ctrl + C input
		exit('Ctrl + C Input - Terminating')



if __name__ == '__main__':
	main()


