import numpy as np
import sys
import copy

def read_sudoku(fname):
    with open(fname) as f:
        f_input = [x.strip('\r\n') for x in f.readlines()]

    sudoku_list = []
    for i in range(len(f_input)):
        sudoku = np.zeros((9, 9), dtype=np.int64)
        temp = f_input[i]
        for j in range(0, len(temp), 9):
            sudoku_row = temp[j:j + 9]
            for k in range(0, 9):
                sudoku[int(j / 9)][k] = sudoku_row[k]
        sudoku_list.append(sudoku)

    return sudoku_list

def write_all_sudokus(filename, sudoku_list):
    with open(sys.argv[2], 'w') as write_file:
        for s in sudoku_list:
            write_sudoku(write_file, s)

def write_sudoku(f, sudoku):
    for i in sudoku.flatten():
        f.write(str(i))
    f.write('\n')

def print_sudoku(sudoku):
    print('+-------+-------+-------+')
    for i in range(0, 9):
        c = [str(i) if i != 0 else '*' for i in sudoku[i]]
        print("| {} {} {} | {} {} {} | {} {} {} |".format(c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8]))
        if (i + 1) % 3 == 0:
            print('+-------+-------+-------+')

def get_neighbors(coordinate):
    neighbors = set()
    row_start = 3 * (coordinate[0] // 3)
    col_start = 3 * (coordinate[1] // 3)
    for i in range(row_start, row_start + 3):
        for j in range(col_start, col_start + 3):
            neighbors.add((i, j))
    for i in range(9):
        neighbors.add((coordinate[0], i))
    for i in range(9):
        neighbors.add((i, coordinate[1]))
    neighbors.remove((coordinate[0], coordinate[1]))
    return list(sorted(neighbors))


def in_neighbors(domains, val, x, y):
    neighbors = get_neighbors((x, y))
    for neighbor in neighbors:
        if len(domains[neighbor[0]][neighbor[1]]) == 1:
            domain = domains[neighbor[0]][neighbor[1]]
            for num in domain:
                if val == num:
                    return True
    return False
            

def revise(domains, x, y):
    for val in domains[x][y]:
        if in_neighbors(domains, val, x, y):
            domains[x][y].remove(val)
            return True
    return False
        
        
def ac3(domains):
    return True, domains
    queue = []
    for i in range(0, 9):
        for j in range(0, 9):
            queue.append((i, j))
    # queue now contains all the arcs in the graph
    while queue:
        (x, y) = queue.pop()
        # if the domain was revised then we check length
        if revise(domains, x, y):
            if len(domains[x][y]) == 0:
                return False, None
            for neighbor in get_neighbors((x, y)):
                queue.append(neighbor)
    return True, domains

def is_assignment_complete(domains):
    return all((all((len(space) == 1 for space in domain_row)) for domain_row in domains))

def is_solved(sudoku):
    for i in range(9):
        for num in range(1, 10):
            block_coord = [(i * 9) // 9, (i * 9) % 9]

            row_range = [3 * (block_coord[1] // 3), 3 * (block_coord[1] // 3) + 3]
            col_range = [3 * (block_coord[0] // 3), 3 * (block_coord[0] // 3) + 3]
            block = sudoku[col_range[0]:col_range[1], row_range[0]:row_range[1]]

            if (not num in sudoku[:, i]) or (not num in sudoku[i, :]) or \
                    (not num in block):
                return False
    return True

def get_domains(sudoku):
    return [[{1, 2, 3, 4, 5, 6, 7, 8, 9} if sudoku[i, j] == 0 else {sudoku[i, j]}
             for j in range(9)] for i in range(9)]

def bts(domains):
    # Start by using AC-3 to reduce the initial domains
    still_valid, domains = ac3(domains)
    # If for some reason AC-3 fails here, this was apparently an impossible Sudoku
    if still_valid:
        return backtrack(domains, bt_count=0)
    else:
        return False, None, 0

def backtrack(domains, bt_count=0):
    if is_assignment_complete(domains):
        return True, domains, bt_count

    # Find the minimum remaining value
    min_i = 0
    min_j = 0
    for i in range(9):
        for j in range(9):
            # We will assign the smallest domain with more than 1 element
            if len(domains[min_i][min_j]) <= 1 or \
                    (len(domains[i][j]) > 1 and len(domains[i][j]) < len(domains[min_i][min_j])):
                min_i = i
                min_j = j
    assert len(domains[min_i][min_j]) > 1

    # This is the location of the minimum remaining value
    coord = (min_i, min_j)

    # The book discusses potentially reordering this list to choose more promising values first.
    # Don't worry about that.
    for possible_value in domains[coord[0]][coord[1]]:
        # Check for consistency with neighbors if we assign this value
        if all((coord == n or any((possible_value != val for val in domains[n[0]][n[1]])) \
                for n in get_neighbors(coord))):
            domains_with_assignment = copy.deepcopy(domains)
            domains_with_assignment[coord[0]][coord[1]] = {possible_value}
            # Inference step
            still_valid, domains_with_assignment = ac3(domains_with_assignment)
            # If this fails, this assignment doesn't work. Skip to backtracking.
            if still_valid:
                solved, solution, bt_count = backtrack(domains_with_assignment, bt_count)
                if solved:
                    return True, solution, bt_count
            bt_count += 1
    print(bt_count)
    return False, None, bt_count

def main():
    sudoku_list = read_sudoku(sys.argv[1])
    solved_sudokus = []
    for sudoku in sudoku_list:
        print_sudoku(sudoku)
        print('Using backtracking search')
        domains = get_domains(sudoku)
        solved, domains, count = bts(domains)
        if solved:
            print('Solved Sudoku')
            for i in range(9):
                for j in range(9):
                    sudoku[i, j] = domains[i][j].pop()
            print_sudoku(sudoku)
            assert is_solved(sudoku)
        else:
            print('No solution found')
        print('Backtracking count: %s' % count)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 input-filename')
    else:
        main()
