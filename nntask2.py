import json
import xml.etree.ElementTree as ET
import sys

def parse_input_file(input_file):
    graph = {"vertices": set(), "arcs": []}
    error_message = None

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                print(f"Чтение строки {line_number}: {line}")

                try:

                    line = line.replace(" ", "").replace("\t", "")
                    arcs = line.split('),(')
                    for arc in arcs:
                        arc = arc.strip('()')
                        a, b, n = arc.split(',')
                        graph["vertices"].add(a)
                        graph["vertices"].add(b)
                        graph["arcs"].append({"from": a, "to": b, "order": int(n)})
                except Exception as e:
                    error_message = f"Ошибка в строке {line_number}: {str(e)}"
                    break
    except FileNotFoundError:
        error_message = f"Файл {input_file} не найден."

    return graph, error_message

def serialize_to_json(graph):
    graph["vertices"] = list(graph["vertices"])
    return json.dumps(graph, indent=4)

def serialize_to_xml(graph):
    root = ET.Element("graph")

    for vertex in graph["vertices"]:
        vertex_element = ET.SubElement(root, "vertex")
        vertex_element.text = vertex

    for arc in graph["arcs"]:
        arc_element = ET.SubElement(root, "arc")
        from_element = ET.SubElement(arc_element, "from")
        from_element.text = arc["from"]
        to_element = ET.SubElement(arc_element, "to")
        to_element.text = arc["to"]
        order_element = ET.SubElement(arc_element, "order")
        order_element.text = str(arc["order"])

    return ET.tostring(root, encoding='utf-8').decode('utf-8')

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

def to_prefix_notation(graph):

    children_dict = {vertex: [] for vertex in graph["vertices"]}

    for arc in graph["arcs"]:
        children_dict[arc["from"]].append((arc["to"], arc["order"]))

    visited = set()
    result = []

    def dfs(vertex):
        visited.add(vertex)
        children = children_dict[vertex]


        if children:
            child_strings = []
            for child, order in sorted(children):
                if child not in visited:
                    child_strings.append(dfs(child))
                else:
                    child_strings.append(f"{child}()")
            return f"{vertex}({','.join(child_strings)})"
        else:
            return vertex

    for vertex in sorted(graph["vertices"]):
        if vertex not in visited:
            result.append(dfs(vertex))

    return ''.join(result)

def main():
    input_file1 = "input.txt"
    output_file1 = "output.txt"

    for arg in sys.argv[1:]:
        key, value = arg.split('=')
        if key == "input1":
            input_file1 = value
        elif key == "output1":
            output_file1 = value

    graph, error_message = parse_input_file(input_file1)

    if error_message:
        print(error_message)
        return

    print(f"Граф: {graph}")

    if has_cycle(graph):
        cycle_message = "Граф содержит циклы."
        print(cycle_message)
        result_message = f"{cycle_message}\nПрефиксная запись не может быть получена из-за наличия циклов."
    else:
        prefix_notation = to_prefix_notation(graph)
        result_message = f"Префиксная запись: {prefix_notation}"

    with open(output_file1, 'w', encoding='utf-8') as file:
        file.write(result_message)

    print(result_message)

if __name__ == "__main__":
    main()