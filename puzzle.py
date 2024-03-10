from nclib import Netcat
from math import sqrt
import re
from random import randint

HOST = 'puzzle.challenges.cybersecuritychallenge.be'
PORT = 1337

def pprint(received_text): 
    # pprint from pprint lib didn't suit my visualisatin needs.
    received_text = received_text.splitlines()
    for line in received_text:
        print(line)

def generate_solved_matrix(matrix_size): 
    # This way we know what to aim for. Also serves to determine where each value should go.
    solved_matrix = []
    for i in range(matrix_size):
        sublist = [str(x) for x in range(matrix_size * i + 1,matrix_size * i + matrix_size + 1)]
        solved_matrix.append(sublist)
    return solved_matrix

def get_destination(value, solution_matrix):
    # Gets the correct position of a given puzzle value.
    for i,j in enumerate(solution_matrix):
        if value in j:
            coords=(j.index(value),int(i))
            return coords

def move(src, dst):
    # Procedurally generates the solution string based on the movements needed to place each value in its correct spot.
    movement_string = b''
    x_diff = abs(dst[0] - src[0])
    if dst[0] >= src[0]:
        movement_string += b'r'*x_diff
    else:
        movement_string += b'l'*x_diff
    y_diff = abs(dst[1] - src[1])
    if dst[1] >= src[1]:
        movement_string += b'd'*y_diff
    else:
        movement_string += b'u'*y_diff
    return movement_string
            
# Data reception & processing
nc = Netcat(connect=(HOST, PORT))
intro = nc.recv_until(b"Aaaand, here is the puzzle:")
puzzle = nc.recv_until(b"Enter your answer:")
puzzle = puzzle[1:-24]
pattern = re.compile(r'\|\s*(\d+)\s*')
puzzle_values = pattern.findall(puzzle.decode())
sorted_values = sorted(puzzle_values, key=int)
matrix_size = int(sqrt(len(puzzle_values)))
puzzle_matrix = []
for i in range(matrix_size):
    sublist = puzzle_values[i + i * (matrix_size-1):i + i * (matrix_size-1) + matrix_size]
    puzzle_matrix.append(sublist)

pprint(puzzle)

# Generation of the solution
# Initialisation
buffer = '0'
current_pos = (0,0)
solution = b'b'
solution_matrix = generate_solved_matrix(matrix_size)
buffer, puzzle_matrix[0][0] = puzzle_matrix[0][0], buffer
destination = get_destination(buffer, solution_matrix)

# This does the dirty work
while puzzle_matrix != solution_matrix:
    if buffer == '0':
        # If the buffer contains 0, get_destination() will return None and break the resolution. This is a band-aid fix to this problem.
        destination = (randint(0,matrix_size -1), randint(0,matrix_size -1))
    else:
        destination = get_destination(buffer, solution_matrix)
    solution += move(current_pos,destination) + b'b'
    current_pos = destination
    buffer, puzzle_matrix[destination[1]][destination[0]] = puzzle_matrix[destination[1]][destination[0]], buffer
    
print(solution)
nc.interactive() # All that remains is to copy/paste the solution string in the terminal.
