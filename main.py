import random
import multiprocessing
import os
import time

def element_and_save(index, A, B, intermediate_file):
    """Вычисляет один элемент результирующей матрицы и сохраняет его в общий файл."""
    i, j = index
    res = 0
    N = len(A[0])
    for k in range(N):
        res += A[i][k] * B[k][j]

    # Сохраняем промежуточный результат в общий файл
    with open(intermediate_file, 'a') as f:
        f.write(f"{i} {j} {res}\n")

    return i, j, res

def matrix_multiplication(matrix1, matrix2, pool_size, intermediate_file):
    """Перемножает матрицы с использованием пула процессов и сохраняет промежуточные результаты."""
    rows, cols = len(matrix1), len(matrix2[0])
    indices = [(i, j) for i in range(rows) for j in range(cols)]

    # Удаляем файл, если он уже существует
    if os.path.exists(intermediate_file):
        os.remove(intermediate_file)

    with multiprocessing.Pool(pool_size) as pool:
        results = pool.starmap(element_and_save, [(index, matrix1, matrix2, intermediate_file) for index in indices])

    # Создаем результирующую матрицу
    result_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    for i, j, value in results:
        result_matrix[i][j] = value

    return result_matrix

def save_matrix_to_file(filename, matrix):
    """Сохраняет матрицу в файл."""
    with open(filename, 'w') as f:
        for row in matrix:
            f.write(' '.join(map(str, row)) + '\n')

def read_matrix_from_file(filename):
    """Считывает матрицу из файла."""
    with open(filename, 'r') as f:
        return [list(map(int, line.split())) for line in f]

def generate_matrix(size):
    """Генерирует случайную квадратную матрицу указанного размера."""
    return [[random.randint(0, 10) for _ in range(size)] for _ in range(size)]

def async_matrix_operations(size, stop_event, folder):
    """Генерирует матрицы и перемножает их асинхронно, пока не установлен флаг остановки."""
    iteration = 0
    intermediate_file = os.path.join(folder, "intermediate_results.txt")

    # Удаляем старый файл с промежуточными результатами
    if os.path.exists(intermediate_file):
        os.remove(intermediate_file)

    while not stop_event.is_set():
        iteration += 1
        matrix1 = generate_matrix(size)
        matrix2 = generate_matrix(size)

        matrix1_file = os.path.join(folder, f"matrix1_iter{iteration}.txt")
        matrix2_file = os.path.join(folder, f"matrix2_iter{iteration}.txt")

        save_matrix_to_file(matrix1_file, matrix1)
        save_matrix_to_file(matrix2_file, matrix2)

        print(f"Сгенерированы матрицы iteration {iteration}, сохранены в {matrix1_file} и {matrix2_file}")

        result = matrix_multiplication(matrix1, matrix2, os.cpu_count(), intermediate_file)

        result_file = os.path.join(folder, f"result_matrix_iter{iteration}.txt")
        save_matrix_to_file(result_file, result)
        print(f"Результат iteration {iteration} сохранен в {result_file}")

if __name__ == "__main__":
    # Основное задание
    matrix_size = 5  # Размер матрицы
    folder = "matrix_files"

    # Создаем папку, если её нет
    if not os.path.exists(folder):
        os.makedirs(folder)

    intermediate_file = os.path.join(folder, "intermediate_results.txt")

    matrix1 = generate_matrix(matrix_size)
    matrix2 = generate_matrix(matrix_size)

    matrix1_file = os.path.join(folder, 'matrix1.txt')
    matrix2_file = os.path.join(folder, 'matrix2.txt')

    save_matrix_to_file(matrix1_file, matrix1)
    save_matrix_to_file(matrix2_file, matrix2)

    print(f"Матрицы сгенерированы и сохранены в файлы {matrix1_file} и {matrix2_file}.")

    if len(matrix1[0]) != len(matrix2):
        raise ValueError("Матрицы нельзя перемножить: число столбцов первой матрицы не равно числу строк второй.")

    # Определяем количество потоков
    pool_size = os.cpu_count()

    result_matrix = matrix_multiplication(matrix1, matrix2, pool_size, intermediate_file)
    result_file = os.path.join(folder, 'result_matrix.txt')
    save_matrix_to_file(result_file, result_matrix)
    print(f"Результат сохранен в {result_file}. Промежуточные результаты записаны в {intermediate_file}.")

    # Дополнительное задание 2
    stop_event = multiprocessing.Event()
    process = multiprocessing.Process(target=async_matrix_operations, args=(matrix_size, stop_event, folder))

    process.start()
    time.sleep(10)  # Даем программе поработать 10 секунд
    stop_event.set()
    process.join()
    print("Асинхронные операции завершены.")
