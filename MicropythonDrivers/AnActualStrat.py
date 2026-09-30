import API
import sys
import time

"""
Diagnosis: problem in current Mpath to Opath algorithm (try to find problem and 
fix tmrw)
"""

size_of_array = 5


def log(string):
    sys.stderr.write("{}\n".format(string))
    sys.stderr.flush()

def initialise_maze():
    # Initialisation
    global maze, pathO, pathM
    maze = [[{"distanceO" : 0, "distanceM" : 0, "e" : x == size_of_array - 1, "w" : x == 0, "n" : y == size_of_array - 1, "s" : y == 0, "stepped": False, "explored" : False} for y in range(size_of_array)] for x in range(size_of_array)]    
    pathO = pathM = []
    

def output_graphics():
    global maze, pathO, pathM
    API.clearAllColor()
    for x in range(len(maze)):
        for y in range(len(maze[x])):
            API.setText(x, y, maze[x][y]["distanceO"])
    for x in range(len(maze)):
        for y in range(len(maze[x])):
            if maze[x][y]["e"]:
                API.setWall(x, y, 'e')
            if maze[x][y]["w"]:
                API.setWall(x, y, 'w')
            if maze[x][y]["n"]:
                API.setWall(x, y, 'n')
            if maze[x][y]["s"]:
                API.setWall(x, y, 's')
    
    for x1, y1 in pathO:
        API.setColor(x1, y1, 'a')


def check_surroundings(x, y, orientation) -> bool:
    global maze, pathO
    wall_left = API.wallLeft()
    wall_right = API.wallRight()
    wall_front = API.wallFront()
    new_wall = False

    if orientation == 's':
        if maze[x][y]['e'] != wall_left:
            maze[x][y]['e'] = wall_left
            new_wall = True
        if x != size_of_array - 1:
            maze[x+1][y]['w'] = wall_left

        if maze[x][y]['w'] !=  wall_right:
            maze[x][y]['w'] = wall_right
            new_wall = True
        if x != 0:
            maze[x-1][y]['e'] = wall_right

        if maze[x][y]['s'] != wall_front:
            maze[x][y]['s'] = wall_front
            new_wall = True
        if y != 0:
            maze[x][y-1]['n'] = wall_front
            
        
    if orientation == 'w':
        if maze[x][y]['s'] != wall_left:
            maze[x][y]['s'] = wall_left
            new_wall = True
        if y != 0:
            maze[x][y-1]['n'] = wall_left

        if maze[x][y]['n'] != wall_right:
            maze[x][y]['n'] = wall_right
            new_wall = True
        if y !=  size_of_array - 1:
            maze[x][y+1]['s'] = wall_right

        if maze[x][y]['w'] != wall_front:
            maze[x][y]['w'] = wall_front
            new_wall = True
        if x != 0:
            maze[x-1][y]['e'] = wall_front
        
    if orientation == 'n':
        if maze[x][y]['w'] != wall_left:
            maze[x][y]['w'] = wall_left
            new_wall = True
        if x != 0:
            maze[x-1][y]['e'] = wall_left

        if maze[x][y]['e'] != wall_right:
            maze[x][y]['e'] = wall_right
            new_wall = True
        if x != size_of_array - 1:
            maze[x+1][y]['w'] = wall_right

        if maze[x][y]['n'] != wall_front:
            maze[x][y]['n'] = wall_front
            new_wall = True
        if y != size_of_array -1:
            maze[x][y+1]['s'] = wall_front
        
    if orientation == 'e':
        if maze[x][y]['n'] != wall_left:
            maze[x][y]['n'] = wall_left
            new_wall = True
        if y != size_of_array - 1:
            maze[x][y+1]['s'] = wall_left

        if maze[x][y]['s'] != wall_right:
            maze[x][y]['s'] = wall_right
            new_wall = True
        if y != 0:
            maze[x][y-1]['n'] = wall_right

        if maze[x][y]['e'] != wall_front:
            maze[x][y]['e'] = wall_front
            new_wall = True
        if x != size_of_array - 1:
            maze[x+1][y]['w'] = wall_front
    return new_wall

def update_distances(Mouse = False, x=0, y=0):
    global maze, size_of_array, pathO, pathM
    for a in range(len(maze)):
        for b in range(len(maze[0])):
            maze[a][b]["stepped"] = False
    if Mouse:
        Mouse_distance = True
        for a, b in pathO:
            maze[a][b]["distanceM"] = 0
    else:
        Mouse_distance =  False

    stop_finding = False
    steps_out = 0
    current_step = [(x, y)]
    maze[x][y]["stepped"] = True
    next_step = []
    x_half = y_half = size_of_array // 2
    while not stop_finding:
        done = []
        for x1, y1 in current_step:
            
            if Mouse_distance:
                maze[x1][y1]["distanceM"] = steps_out
                if (x1, y1) in pathO and not maze[x1][y1]['explored']:
                    stop_finding = True
                    x_final, y_final = x1,y1
            else:
                maze[x1][y1]["distanceO"] = steps_out
                if (x1, y1) == (x_half, y_half):
                    stop_finding = True
                    x_final, y_final = x_half, y_half

                    
            done.append((x1,y1))
            if y1 != size_of_array - 1:
                if not (maze[x1][y1]["n"] or maze[x1][y1+1]["stepped"]):
                    maze[x1][y1+1]["stepped"] = True
                    next_step.append((x1, y1 + 1))
            if y1 != 0:
                if not (maze[x1][y1]["s"] or maze[x1][y1-1]["stepped"]):
                    maze[x1][y1-1]["stepped"] = True
                    next_step.append((x1, y1 - 1))
            if x1 != size_of_array - 1:
                if not (maze[x1][y1]["e"] or maze[x1+1][y1]["stepped"]):
                    maze[x1+1][y1]["stepped"] = True
                    next_step.append((x1 + 1, y1))
            if x1 != 0:
                if not (maze[x1][y1]["w"] or maze[x1-1][y1]["stepped"]):
                    maze[x1-1][y1]["stepped"] = True
                    next_step.append((x1 - 1, y1))

        current_step = next_step
        next_step = [] 
        steps_out += 1
    for (a,b) in current_step:
        if (a, b) != (x_final, y_final):
            maze[a][b]["stepped"] = False
        


def find_path(Mouse=False, x=0, y=0):
    global pathO, pathM, maze, testing
    if Mouse:
        if (x, y) in pathO and not maze[x][y]["explored"]:
            pathM = pathO[:pathO.index((x,y))+1]
            return
        min_distance = 0
        for tuple in pathO:
            x2, y2 = tuple
            distance_point = maze[x2][y2]["distanceM"]
            if distance_point != 0:
                if (not min_distance or distance_point < min_distance) and not maze[x2][y2]["explored"]:
                    min_distance = distance_point
                    x1, y1 = x2, y2
        path = []
        current_score = maze[x1][y1]["distanceM"]

                
    else:
        x1 = y1 = size_of_array // 2
        path = []
        current_score = maze[x1][y1]["distanceO"]
        
    while current_score != -1:

        tuple = (x1, y1)
        path.append(tuple)

        if x1 != 0:
            if Mouse:
                left = maze[x1-1][y1]["distanceM"]
            else:
                left = maze[x1-1][y1]["distanceO"]
            if left == current_score - 1 and \
                not maze[x1][y1]['w'] and maze[x1-1][y1]["stepped"]:
                x1 -= 1
        if y1 != 0:
            if Mouse:
                down = maze[x1][y1-1]["distanceM"]
            else:
                down = maze[x1][y1-1]["distanceO"]            
            if down == current_score - 1 and \
                not maze[x1][y1]['s'] and maze[x1][y1-1]["stepped"]:
                y1 -= 1
        if x1 != size_of_array - 1:
            if Mouse:
                right = maze[x1+1][y1]["distanceM"]
            else:
                right = maze[x1+1][y1]["distanceO"]
            if right == current_score - 1 and \
                not maze[x1][y1]['e'] and maze[x1+1][y1]["stepped"]:
                x1 += 1
        if y1 != size_of_array - 1:
            if Mouse:
                up = maze[x1][y1+1]["distanceM"]
            else:
                up = maze[x1][y1+1]["distanceO"]
            if up == current_score - 1 and \
                not maze[x1][y1]['n'] and maze[x1][y1+1]["stepped"]:
                y1 += 1
        current_score -= 1
    if Mouse:
        pathM = path
    else:
        pathO = path

        
def move(x, y, orientation) -> tuple:
    global pathM
    if len(pathM) > 1:
        x1, y1 = pathM[-2]
    else:
        x1 = x
        y1 = y
    pathM.pop()
    
    if x1 == x + 1:
        if orientation == 'n':
            API.turnRight()
        if orientation == 'w':
            API.turnLeft()
            API.turnLeft()
        if orientation == 's':
            API.turnLeft()
        API.moveForward()
        orientation = 'e'
    if x1 == x - 1:
        if orientation == 's':
            API.turnRight()
        if orientation == 'e':
            API.turnLeft()
            API.turnLeft()
        if orientation == 'n':
            API.turnLeft()
        API.moveForward()   
        orientation = 'w'
    if y1 == y + 1:
        if orientation == 'w':
            API.turnRight()
        if orientation == 's':
            API.turnLeft()
            API.turnLeft()
        if orientation == 'e':
            API.turnLeft()
        API.moveForward()
        orientation = 'n'
    if y1 == y - 1:
        if orientation == 'e':
            API.turnRight()
        if orientation == 'n':
            API.turnLeft()
            API.turnLeft()
        if orientation == 'w':
            API.turnLeft()
        API.moveForward()
        orientation = 's'
    return (x1, y1, orientation)
    

def main():
    # Initialisation
    global pathO, pathM, maze, max_depth
    initialise_maze()
    x = y = 0
    orientation = 'n'
    explored_maze = False
    output_graphics()
    t=0
    while not explored_maze:
        new_wall = check_surroundings(x, y, orientation)
        log(f"check-surr {t}")
        output_graphics()
        if new_wall:
            update_distances()
            log(f"O-distance {t}")
            find_path()
            log(f"O-path {t}")
        current_explored = maze[x][y]['explored']
        maze[x][y]['explored'] = True
        explored_maze =  True
        for x1, y1 in pathO:
            if not maze[x1][y1]['explored']:
                explored_maze = False
                break
        if explored_maze:
            break
        if not current_explored:
            update_distances(True, x, y)
            log(f"M-distance {t}")
            find_path(True, x, y)
            log(f"M-path {t}")
        x, y, orientation = move(x, y, orientation)
        t+=1
    API.ackReset() 
    x = y = 0
    orientation = 'n'
    pathM = pathO.copy()
    while len(pathM) > 1:
        x, y, orientation = move(x, y, orientation)


if __name__ == "__main__":
    main()
