def result(matrix, pos, data, this_way, weights):
    i, j = pos
    this_way.append((i, j))

    if matrix[i][j] == 'Fin':
        data.append([i for i in this_way])

    if j > 0 and matrix[i][j - 1] and weights[i][j - 1] > weights[i][j] + 1:
        # go left

        weights[i][j - 1] = weights[i][j] + 1
        result(matrix, (i, j - 1), data, this_way, weights)
        this_way.pop()

    if j < len(matrix) - 1 and matrix[i][j + 1] and weights[i][j + 1] > weights[i][j] + 1:
        # go right

        weights[i][j + 1] = weights[i][j] + 1
        result(matrix, (i, j + 1), data, this_way, weights)
        this_way.pop()

    if i > 0 and matrix[i - 1][j] and weights[i - 1][j] > weights[i][j] + 1:
        # go up

        weights[i - 1][j] = weights[i][j] + 1
        result(matrix, (i - 1, j), data, this_way, weights)
        this_way.pop()

    if i < len(matrix) - 1 and matrix[i + 1][j] and weights[i + 1][j] > weights[i][j] + 1:
        # go down

        weights[i + 1][j] = weights[i][j] + 1
        result(matrix, (i + 1, j), data, this_way, weights)
        this_way.pop()

    return data


if __name__ == '__main__':
    lifes = int(input('Введите количество жизней героя: '))
    pos = tuple(map(int, input('Введите стартовую позицию через пробел: ').split()))
    f = [['Fin' if row == '☼' else (0 if row == '☒' else (1 if row == '.' else (0 if int(row) >= lifes else int(row))))
          for row in string.rstrip()]
         for string in open('data.txt').readlines()]
    weights = [[1000000 for j in range(len(f[0]))] for i in range(len(f))]
    weights[pos[0]][pos[1]] = 1
    res = result(f, pos, [], [], weights)
    with_monsters = []
    for i in res:
        cnt = 0
        for j in i:
            this = f[j[0]][j[1]]
            if this != 'Fin' and this != 1:
                cnt += int(this)
        if cnt < lifes:
            with_monsters.append([cnt] + i)
    with_monsters.sort(key=len)
    if with_monsters:
        print('Из точки с позицией', pos, 'до выхода из лабиринта быстрее всего можно добраться, потратив',
              with_monsters[0][0],
              'жизней, по следующему пути (длина --', len(with_monsters[0]) - 1, '):')
        print(with_monsters[0][1:])
    else:
        print('К сожалению, с заданными условиями добраться до конца лабиринта не получится(((((')
