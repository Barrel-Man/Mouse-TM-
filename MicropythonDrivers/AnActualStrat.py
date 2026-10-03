import API
import sys

# 5 for the test maze on the board, 16 for the MMS simulator.
size_of_array = 5

# Compass helpers: (dx, dy) for a step, and which way is left/right/behind.
STEP = {'n': (0, 1), 'e': (1, 0), 's': (0, -1), 'w': (-1, 0)}
OPPOSITE = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
LEFT_OF = {'n': 'w', 'w': 's', 's': 'e', 'e': 'n'}
RIGHT_OF = {'n': 'e', 'e': 's', 's': 'w', 'w': 'n'}


def log(string):
    print(string)

def initialise_maze():
    global maze, pathO, pathM
    maze = [[{"distanceO": 0, "distanceM": 0,
              "e": x == size_of_array - 1, "w": x == 0,
              "n": y == size_of_array - 1, "s": y == 0,
              "stepped": False, "explored": False}
             for y in range(size_of_array)] for x in range(size_of_array)]
    # FIX: was `pathO = pathM = []`, which makes both names point at the SAME
    # list, so popping pathM (in move) silently edited pathO too.
    pathO = []
    pathM = []


def output_graphics():
    global maze, pathO, pathM
    API.clearAllColor()
    for x in range(len(maze)):
        for y in range(len(maze[x])):
            API.setText(x, y, maze[x][y]["distanceO"])
    for x in range(len(maze)):
        for y in range(len(maze[x])):
            for d in 'ensw':
                if maze[x][y][d]:
                    API.setWall(x, y, d)
    for x1, y1 in pathO:
        API.setColor(x1, y1, 'a')


def set_wall(x, y, d, present):
    """Record a wall on side d of cell (x, y) AND on the neighbour's matching
    side. Returns True if this changed what we knew. The outer boundary is
    always a wall, so a sensor reading can never open it."""
    dx, dy = STEP[d]
    nx, ny = x + dx, y + dy
    if not (0 <= nx < size_of_array and 0 <= ny < size_of_array):
        return False
    changed = maze[x][y][d] != present
    maze[x][y][d] = present
    maze[nx][ny][OPPOSITE[d]] = present
    return changed


def check_surroundings(x, y, orientation) -> bool:
    """Look left/right/front and update the map. True if a wall changed."""
    # FIX: only sense a cell the first time we are in it. Re-sensing every
    # visit let one noisy ToF reading overwrite a wall we already knew, which
    # could seal the goal off (-> infinite loop) or open a wall that is there.
    if maze[x][y]['explored']:
        return False
    wall_left = API.wallLeft()
    wall_right = API.wallRight()
    wall_front = API.wallFront()
    print("walls L", wall_left, "F", wall_front, "R", wall_right)
    new_wall = False
    new_wall |= set_wall(x, y, LEFT_OF[orientation], wall_left)
    new_wall |= set_wall(x, y, RIGHT_OF[orientation], wall_right)
    new_wall |= set_wall(x, y, orientation, wall_front)
    return new_wall


def update_distances(Mouse=False, x=0, y=0):
    """Flood fill. Mouse=False: distance from the start, until the goal is
    reached (distanceO). Mouse=True: distance from (x, y), until an
    unexplored cell of the current best path is reached (distanceM).
    Returns False if nothing it was looking for can be reached."""
    global maze, size_of_array, pathO, pathM
    for a in range(len(maze)):
        for b in range(len(maze[0])):
            maze[a][b]["stepped"] = False
    if Mouse:
        Mouse_distance = True
        for a, b in pathO:
            maze[a][b]["distanceM"] = 0
    else:
        Mouse_distance = False

    stop_finding = False
    steps_out = 0
    current_step = [(x, y)]
    maze[x][y]["stepped"] = True
    next_step = []
    x_half = y_half = size_of_array // 2
    # FIX: also stop when the frontier is empty. Before, if the goal was
    # unreachable (e.g. one wall misread) this loop never ended.
    while not stop_finding and current_step:
        for x1, y1 in current_step:
            if Mouse_distance:
                maze[x1][y1]["distanceM"] = steps_out
                if (x1, y1) in pathO and not maze[x1][y1]['explored']:
                    stop_finding = True
            else:
                maze[x1][y1]["distanceO"] = steps_out
                if (x1, y1) == (x_half, y_half):
                    stop_finding = True

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
    # Cells in the last frontier were marked but never given a distance.
    for (a, b) in current_step:
        maze[a][b]["stepped"] = False
    return stop_finding


def find_path(Mouse=False, x=0, y=0):
    """Walk downhill through the flood-fill numbers to build a path.
    Path is stored target -> ... -> start (Mouse: target -> ... -> mouse)."""
    global pathO, pathM, maze
    key = "distanceM" if Mouse else "distanceO"
    if Mouse:
        best = None
        for cell in pathO:
            x2, y2 = cell
            d = maze[x2][y2]["distanceM"]
            if d != 0 and not maze[x2][y2]["explored"]:
                if best is None or d < best[0]:
                    best = (d, x2, y2)
        if best is None:
            pathM = []
            return False
        x1, y1 = best[1], best[2]
    else:
        x1 = y1 = size_of_array // 2

    path = []
    current_score = maze[x1][y1][key]
    while current_score != -1:
        path.append((x1, y1))
        # FIX: pick ONE neighbour per step (was four separate `if`s that could
        # each move the cursor again, using the already-updated x1/y1).
        moved = False
        for d in 'wsen':
            dx, dy = STEP[d]
            nx, ny = x1 + dx, y1 + dy
            if not (0 <= nx < size_of_array and 0 <= ny < size_of_array):
                continue
            if (maze[nx][ny][key] == current_score - 1
                    and not maze[x1][y1][d] and maze[nx][ny]["stepped"]):
                x1, y1 = nx, ny
                moved = True
                break
        if not moved and current_score != 0:
            return False  # map is inconsistent; don't spin forever
        current_score -= 1
    if Mouse:
        pathM = path
    else:
        pathO = path
    return True


def move(x, y, orientation) -> tuple:
    global pathM
    print("at", x, y, "facing", orientation, "path", pathM)
    if len(pathM) > 1:
        x1, y1 = pathM[-2]
    else:
        x1 = x
        y1 = y
    if pathM:
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
    global pathO, pathM, maze
    initialise_maze()
    x = y = 0
    orientation = 'n'

    # FIX: plan BEFORE the first look. Before, the first path was only made
    # if the start cell revealed a wall; if it didn't (both sides open), pathO
    # stayed [] which counts as "everything explored" and the mouse never moved.
    update_distances()
    find_path()
    output_graphics()

    t = 0
    while True:
        new_wall = check_surroundings(x, y, orientation)
        if new_wall:
            if not update_distances() or not find_path():
                log("goal unreachable in map - a wall was probably misread")
                API.ackReset()
                return
            output_graphics()

        first_visit = not maze[x][y]['explored']
        maze[x][y]['explored'] = True

        if all(maze[a][b]['explored'] for a, b in pathO):
            break

        # FIX: re-plan the mouse's route whenever the map changed OR this is a
        # new cell. (Before it only re-planned on a new cell, so a wall found
        # on a revisit left the mouse following a route through that wall.)
        if first_visit or new_wall:
            update_distances(True, x, y)
            if not find_path(True, x, y):
                log("no route to an unexplored cell")
                API.ackReset()
                return
        if len(pathM) < 2:
            log("mouse path empty")
            API.ackReset()
            return
        x, y, orientation = move(x, y, orientation)
        t += 1

    API.ackReset()
    x = y = 0
    orientation = 'n'
    pathM = pathO.copy()
    while len(pathM) > 1:
        x, y, orientation = move(x, y, orientation)


if __name__ == "__main__":
    main()