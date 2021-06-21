#!/bin/python3

# A simple 2048 AI

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
from signal import signal, SIGINT

print("""=======
Initialization
=======""")
print("Starting Chrome...")
driver = webdriver.Chrome()
print("Done.")
print("Launching 2048...")
driver.get("https://play2048.com")
print("Done.")

print("The program will wait 5 seconds if you want to remove the popups and to make sure everything is loaded.")
time.sleep(5)

game = driver.find_element_by_tag_name("body")
moves = ["up", "right", "down", "left"]

def get_grid():
    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    tiles = driver.find_elements_by_class_name("tile")
    for tile in tiles:
        classes = tile.get_attribute("class")
        positions = classes.split()[2][14:].split("-")
        posx, posy = int(positions[0]) - 1, int(positions[1]) - 1
        value = int(classes.split()[1][5:])
        grid[posy][posx] = value

    return grid

# Movements on real game
def move(direction):
    directions = {"up": Keys.UP, "right": Keys.RIGHT, "down": Keys.DOWN, "left": Keys.LEFT}
    game.send_keys(directions[direction])

# Movements on an internal grid
def grid_move(direction, internal_grid):

    # For each tile
    y = 0
    # Count merges
    merges = 0
    total_merges = 0
    max_merge = 0
    for row in internal_grid:
        x = 0
        for tile in row:

            if tile != 0:
                # Calculating the maximum number of movements
                nmove = 0
                merge = False
                for space in range(1, 4):

                    if direction == "up":
                        if y >= space:
                            if internal_grid[y - space][x] == 0:
                                nmove += 1
                            # See if it can merge
                            elif internal_grid[y - space][x] == tile:
                                merge = True
                                merges += 1
                                break

                    elif direction == "right":
                        if 3 - x >= space:
                            if internal_grid[y][x + space] == 0:
                                nmove += 1
                            # See if it can merge
                            elif internal_grid[y][x + space] == tile:
                                merge = True
                                merges += 1
                                break

                    elif direction == "down":
                        if 3 - y >= space:
                            if internal_grid[y + space][x] == 0:
                                nmove += 1
                            # See if it can merge
                            elif internal_grid[y + space][x] == tile:
                                merge = True
                                merges += 1
                                break

                    elif direction == "left":
                        if x >= space:
                            if internal_grid[y][x - space] == 0:
                                nmove += 1
                            # See if it can merge
                            elif internal_grid[y][x - space] == tile:
                                merge = True
                                merges += 1
                                break
                
                # Move the tile
                internal_grid[y][x] = 0
                if direction == "up":
                    internal_grid[y - nmove][x] = tile
                elif direction == "right":
                    internal_grid[y][x + nmove] = tile
                elif direction == "down":
                    internal_grid[y + nmove][x] = tile
                elif direction == "left":
                    internal_grid[y][x - nmove] = tile

                # Merge the tile
                if merge:
                    new_tile = tile * 2
                    if direction == "up":
                        internal_grid[y - nmove][x] = 0
                        internal_grid[y - (nmove + 1)][x] = new_tile
                    elif direction == "right":
                        internal_grid[y][x + nmove] = 0
                        internal_grid[y][x + (nmove + 1)] = new_tile
                    elif direction == "down":
                        internal_grid[y + nmove][x] = 0
                        internal_grid[y + (nmove + 1)][x] = new_tile
                    elif direction == "left":
                        internal_grid[y][x - nmove] = 0
                        internal_grid[y][x - (nmove + 1)] = new_tile
                    total_merges += new_tile
                    if new_tile > max_merge:
                        max_merge = new_tile

            x += 1
        y += 1
    
    return (internal_grid, merges, total_merges, max_merge)

def main(depth, tmp_grid):
    global merges_data
    if depth == 0:
        return
    # Try all movements in a certain depth
    for movement in moves:
        grid_results = grid_move(movement, tmp_grid)
        merges_data[movement][0] += grid_results[1]
        merges_data[movement][1] += grid_results[2]
        if grid_results[3] > merges_data[movement][2]:
            merges_data[movement][2] = grid_results[3]
        main(depth - 1, grid_results[0])

def stop(signal_received, frame):
    print("Closing Chrome...")
    driver.close()
    exit()

print("AI started.")
while True:

    # Initialize the grid
    merges_data = {"up": [0, 0, 0], "right": [0, 0, 0], "down": [0, 0, 0], "left": [0, 0, 0]}
    merges_score = {"up": 0, "right": 0, "down": 0, "left": 0}
    grid = get_grid()
    
    # Launch the "brute force AI"
    main(5, grid)
    
    # Compute the score of each movement
    merges_data_values = list(merges_data.values())
    n = 0
    max_merge_list = []
    for data in merges_data_values:
        score = data[0] * data[1]
        merges_score[moves[n]] = score
        max_merge_list.append(data[2])
        n += 1
    
    # The best move is the move which has the biggest max_merge
    # If there are no doubles
    # if max_merge_list.count(max(max_merge_list)) == 1:
    best_move = moves[max_merge_list.index(max(max_merge_list))]
    if grid_move(best_move, grid)[0] == grid:
        best_move = random.choice(moves)

    print(best_move)

    # else:
    #     # Get the maximum score and so the best move
    #     score_values = list(merges_score.values())
    #     max_score = max(score_values)
    #     if max_score == 0:
    #         best_move = random.choice(moves)
    #     else:
    #         best_move = moves[score_values.index(max_score)]

    #     if grid_move(best_move, grid)[0] == grid:
    #         best_move = random.choice(moves)

    move(best_move)
    time.sleep(0.2)