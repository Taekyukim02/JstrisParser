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
def get_color(pix):
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
    return mapping.get(pix[1], None)


### GLOBAL VARIABLES ###

# initialize pandas dataframe of moves
max_moves = 1000
moves = pd.DataFrame(index=np.arange(0, max_moves),
                     columns={"block1": pd.Series(dtype='category'),
                              "block2": pd.Series(dtype='category'),
                              "tot_time": pd.Series(dtype='float'),
                              "think_time": pd.Series(dtype='float'),
                              "place_time": pd.Series(dtype='float'),
                              "switch_time": pd.Series(dtype='float'),
                              "switched": pd.Series(dtype='bool')})
move_index = 0

# timing game moves
t_game = None  # start of game
t_move = None  # start of move
t_switch = None  # when held is pressed (or start of move if not held)
t_place = None  # start of placement movement


def update(monitor, block_location):
    sct = mss.mss()

    # DEBUG: print matrix
    output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)
    sct_img = sct.grab(monitor)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
    print(output)

    global t_game, t_move, t_switch
    t_game = time.time()
    t_move = time.time()
    t_switch = t_move

    # callback functions
    def on_press(key):
        global max_moves, moves, move_index, t_game, t_switch, t_move, t_place

        # start movement
        if (key in KeyMap.key_list and t_place == None):
            t_place = time.time()

        # end move
        if (key == KeyMap.harddrop):
            t_move_end = time.time()
            moves.loc[move_index]["tot_time"] = (t_move_end - t_move)
            moves.loc[move_index]["think_time"] = (t_place - t_move)
            moves.loc[move_index]["place_time"] = (t_move_end - t_switch)
            moves.loc[move_index]["switch_time"] = (t_switch - t_move)

            # DEBUG: print dataframe row
            print(moves.loc[move_index])

            # get new block
            move_index = move_index + 1
            img = np.array(sct.grab(monitor))
            pix = img[block_location[0] * 2, block_location[1] * 2,]
            moves.loc[move_index]["block1"] = get_color(pix)
            moves.loc[move_index]["switched"] = False

            # start new move timing
            t_move = time.time()
            t_switch = t_move
            t_place = None
            return

        # hold block
        if (key == KeyMap.hold and move_index > 0):
            img = np.array(sct.grab(monitor))
            pix = img[block_location[0] * 2, block_location[1] * 2,]
            moves.loc[move_index]["block2"] = get_color(pix)
            moves.loc[move_index]["switched"] = True

            t_switch = time.time()
            t_place = None
            return

        if (not key in KeyMap.key_list):
            print("pressed other key:", key)
            return

    # don't do anything when key is released
    def on_release(key):
        return

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while 1:
        pass


def main():
    # find matrix location
    print("Finding the board...")
    topleft_location = None
    while (topleft_location == None):
        print("Please ensure the top-left of the matrix is visible.")
        topleft_location = py.locateOnScreen('./assets/topleft.png')

    square_length = 24  # width / length of square in matrix
    matrix_height = square_length * 20
    matrix_width = square_length * 10

    monitor = {"top": topleft_location.top // 2 + 2, "left": topleft_location.left // 2 + 1, "width": matrix_width,
               "height": matrix_height}
    #monitor = {"top": newgame_location.top // 2 - 502, "left": newgame_location.left // 2 - 145, "width": matrix_width,
    #           "height": matrix_height}

    # important locations relative to matrix
    go_location = (124, 290)
    block_location = (square_length // 2, 9 * square_length // 2)

    # wait until game starts
    #	go_color = py.pixel(710, 473)[0]
    #	print(go_color)

    # run game
    try:
        print("Parsing jstris...")
        update(monitor, block_location)
    except KeyboardInterrupt:  # If Ctrl + C input
        exit('Ctrl + C Input - Terminating')


if __name__ == '__main__':
    main()
