from tiles import Shape

def read_row(row, size):
    bushes = []
    row = row[:size*2]
    for bush in row[::2]:
        try:
            bushes.append(int(bush))
        except ValueError:
            bushes.append(0)
        bushes.append
    return bushes

def read(path):
    with open(path, 'r') as f:
        # Skip header
        lines = f.readlines()

        bushes = []
        size = len(lines[2]) // 2

        assert size > 0, 'size of bushes being read in is not positive'

        # Load inital map
        bushes = [read_row(lines[2 + i], size) for i in range(size)]
        
        # Load available tiles
        tile_dict = {}
        # print('... ', lines[2 + size + 2])
        temp_dict = lines[2 + size + 2].strip()
        # Remove {}
        temp_dict = temp_dict[1:len(temp_dict)-1]
        # print(temp_dict)
        for tile in temp_dict.split(','):
            tile = tile.strip()
            k, v = tile.split('=')
            tile_dict[Shape[k]] = int(v)
        # print(tile_dict)
        
        # Load targets
        targets = {}
        for i in range(4):
            k, v = lines[2 + size + 2 + 3 + i].strip().split(':')
            targets[int(k)] = int(v)
        # print(targets)
        
        # Load solution if it exists in the file
        solution = []
        for line in lines[2 + size + 2 + 3 + 9: 2 + size + 2 + 3 + 9 + size * size // 4 // 4]:
            # print(line)
            tile_id, tile_size, tile_shape = line.strip().split(' ')
            # print(tile_id)
            # print(tile_size)
            # print(tile_shape)
            solution.append([int(tile_id), int(tile_size), Shape[tile_shape]])
        # print(solution)
        return bushes, tile_dict, size, targets, solution