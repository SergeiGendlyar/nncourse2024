import json
import xml.etree.ElementTree as ET
import sys
import re


def parse_input_file(input_file):
    graph = {"vertices": set(), "arcs": []}
    error_message = None

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Используем регулярное выражение для извлечения дуг
                    edges = re.findall(r"\((.*?)\)", line.replace(' ', ''))
                    for edge in edges:
                        parts = edge.split(',')
                        if len(parts) != 3:
                            raise ValueError("неправильно заданы номера дуг")

                        a, b, n = parts

                        # Проверяем корректность имен вершин и номера дуги
                        if not n.isdigit():
                            raise ValueError("номер дуги должен быть числом")

                        graph["vertices"].add(a.strip())
                        graph["vertices"].add(b.strip())
                        graph["arcs"].append({"from": a.strip(), "to": b.strip(), "order": int(n)})
                except ValueError as e:
                    error_message = f"Строка {line_number}: {str(e)}"
                    break
    except FileNotFoundError:
        error_message = f"Файл {input_file} не найден."

    return graph, error_message


def parse_operations_file(operations_file):
    operations = {}
    error_message = None

    try:
        with open(operations_file, 'r', encoding='utf-8') as file:
            try:
                operations = json.load(file)
            except json.JSONDecodeError:
                file.seek(0)
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        vertex, operation = line.split(':')
                        vertex = vertex.strip()
                        operation = operation.strip()
                        operations[vertex] = operation
                    except ValueError as e:
                        error_message = f"Ошибка в строке {line_number} файла операций: {str(e)}"
                        break
    except FileNotFoundError:
        error_message = f"Файл {operations_file} не найден."

    return operations, error_message

def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def dfs(vertex):
        if vertex in rec_stack:
            return True
        if vertex in visited:
            return False

        visited.add(vertex)
        rec_stack.add(vertex)

        for arc in graph["arcs"]:
            if arc["from"] == vertex:
                if dfs(arc["to"]):
                    return True

        rec_stack.remove(vertex)
        return False

    for vertex in graph["vertices"]:
        if dfs(vertex):
            return True
    return False


def evaluate_function(graph, operations):
    values = {}

    children_dict = {vertex: [] for vertex in graph["vertices"]}
    parents_count = {vertex: 0 for vertex in graph["vertices"]}

    for arc in graph["arcs"]:
        children_dict[arc["from"]].append((arc["to"], arc["order"]))
        parents_count[arc["to"]] += 1

    def compute_vertex(vertex):
        if vertex in values:
            return values[vertex]

        if vertex not in operations:
            raise ValueError(f"Операция для вершины {vertex} не определена.")

        operation = operations[vertex]
        print(f"Обработка вершины {vertex} с операцией {operation}")

        if operation.isdigit() or (operation.replace('.', '', 1).isdigit()):
            result = float(operation)
        else:

            children = sorted(children_dict[vertex], key=lambda x: x[1])
            child_values = [compute_vertex(child[0]) for child in children]

            if operation == '+':
                result = sum(child_values)
            elif operation == '*':
                result = 1
                for val in child_values:
                    result *= val
            elif operation == 'exp':
                if len(child_values) != 1:
                    raise ValueError(f"Операция 'exp' требует один аргумент, но получено {len(child_values)}")
                result = 2.718281828459045 ** child_values[0]
            else:
                raise ValueError(f"Неизвестная операция: {operation}")

        values[vertex] = result
        print(f"Значение вершины {vertex} вычислено: {result}")
        return result

    total_result = 0
    for vertex in sorted(graph["vertices"]):
        if vertex not in values:
            total_result += compute_vertex(vertex)

    print(f"Итоговое значение функции: {total_result}")
    return total_result


def validate_graph(graph, operations):
    errors = []

    root_vertices = set(graph["vertices"]) - {arc["to"] for arc in graph["arcs"]}

    if len(root_vertices) == 1:
        root = next(iter(root_vertices))
        if root in operations and operations[root].replace('.', '', 1).isdigit():

            if len(graph["vertices"]) > 1:
                errors.append(f"Исток {root} не может быть числовым значением, так как граф содержит другие вершины.")
        elif root not in operations:
            errors.append(f"Для истока {root} не определена операция или значение.")
    else:
        for root in root_vertices:
            if root in operations and not operations[root].replace('.', '', 1).isdigit():
                errors.append(f"Исток {root} не может быть операцией ({operations[root]}).")
            elif root not in operations:
                errors.append(f"Для истока {root} не определена операция или значение.")

    child_vertices = {arc["from"] for arc in graph["arcs"]}
    for vertex in graph["vertices"] - child_vertices:
        if vertex in operations and (operations[vertex] == "+" or
                                     operations[vertex] == "*" or
                                     operations[vertex] == "exp"):
            errors.append(f"Сток {vertex} не может быть операцией ({operations[vertex]}).")
        elif vertex not in operations:
            errors.append(f"Для стока {vertex} не определена операция или значение.")
    for vertex in graph["vertices"]:
        if vertex not in operations:
            errors.append(f"Вершина {vertex} не имеет операции или значения.")

    return errors


def validate_operations(operations):
    valid_operations = {'+', '*', 'exp'}
    errors = []

    for vertex, operation in operations.items():
        if not (operation.replace('.', '', 1).isdigit() or operation in valid_operations):
            errors.append(f"Недопустимая операция для вершины {vertex}: {operation}")

    return errors

def main():
    input_file1 = "input.txt"
    input_file2 = None
    output_file1 = "output.json"

    for arg in sys.argv[1:]:
        key, value = arg.split('=')
        if key == "input1":
            input_file1 = value
        elif key == "input2":
            input_file2 = value
        elif key == "output1":
            output_file1 = value

    graph, error_message = parse_input_file(input_file1)
    if error_message:
        print(error_message)
        return

    if input_file2 is None:
        print("Второй входной файл не указан.")
        return

    operations, error_message = parse_operations_file(input_file2)
    if error_message:
        print(error_message)
        return

    graph_errors = validate_graph(graph, operations)
    operation_errors = validate_operations(operations)

    if graph_errors or operation_errors:
        errors = graph_errors + operation_errors
        print("Ошибки в графе или операциях:")
        for error in errors:
            print(f"- {error}")
        with open(output_file1, 'w', encoding='utf-8') as file:
            file.write("Ошибки:\n" + "\n".join(errors))
        return

    if has_cycle(graph):
        print("Граф содержит циклы. Вычисление невозможно.")
        with open(output_file1, 'w', encoding='utf-8') as file:
            file.write("Граф содержит циклы. Вычисление невозможно.")
        return

    try:
        result = evaluate_function(graph, operations)
        with open(output_file1, 'w', encoding='utf-8') as file:
            file.write(f"Результат вычисления функции: {result}")
        print(f"Результат вычисления функции: {result}")
    except ValueError as e:
        print(f"Ошибка вычисления: {e}")
        with open(output_file1, 'w', encoding='utf-8') as file:
            file.write(f"Ошибка вычисления: {e}")

if __name__ == "__main__":
    main()
