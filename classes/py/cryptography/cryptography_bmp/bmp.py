from PIL import Image

def load_bmp(file_path, threshold=128):
    """
    Loads a BMP file and converts it to a matrix (list of lists) of 0/1.
    0 = black pixel
    1 = white pixel
    """
    img = Image.open(file_path).convert("L")  # grayscale
    width, height = img.size
    pixels = img.load()

    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(1 if pixels[x, y] >= threshold else 0)
        matrix.append(row)

    return matrix

def save_bmp(matrix, file_path):
    """
    Saves a 0/1 matrix as a black/white BMP.
    0 = black, 1 = white
    """
    height = len(matrix)
    width = len(matrix[0])

    img = Image.new("L", (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            pixels[x, y] = 255 if matrix[y][x] == 1 else 0

    img.save(file_path, format="BMP")

import random

def random_bmp(width, height):
    """
    Generates a width x height matrix of random 0/1 values.
    """
    return [[random.randint(0, 1) for _ in range(width)] for _ in range(height)]

def mod2(A, B):
    """
    Bitwise modulo-2 (XOR) of two 0/1 matrices.
    """
    h = len(A)
    w = len(A[0])

    result = [[0]*w for _ in range(h)]

    for y in range(h):
        for x in range(w):
            result[y][x] = (A[y][x] + B[y][x]) % 2

    return result
