import json
import xml.etree.ElementTree as ET
import sys


def parse_input_file(input_file):
    graph = {"vertices": set(), "arcs": set()}
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
                        arc_tuple = (a, b, int(n))

                        if arc_tuple in graph["arcs"]:
                            error_message = f"Ошибка: повторяющаяся дуга {arc_tuple} в строке {line_number}."
                            break
                        graph["arcs"].add(arc_tuple)
                except Exception as e:
                    error_message = f"Ошибка в строке {line_number}: {str(e)}"
                    break
    except FileNotFoundError:
        error_message = f"Файл {input_file} не найден."

    return graph, error_message


def serialize_to_json(graph):
    graph["vertices"] = list(graph["vertices"])
    graph["arcs"] = [list(arc) for arc in graph["arcs"]]
    return json.dumps(graph, indent=4)


def serialize_to_xml(graph):
    root = ET.Element("graph")

    for vertex in graph["vertices"]:
        vertex_element = ET.SubElement(root, "vertex")
        vertex_element.text = vertex

    for arc in graph["arcs"]:
        arc_element = ET.SubElement(root, "arc")
        from_element = ET.SubElement(arc_element, "from")
        from_element.text = arc[0]  # Изменяем на индекс кортежа
        to_element = ET.SubElement(arc_element, "to")
        to_element.text = arc[1]  # Изменяем на индекс кортежа
        order_element = ET.SubElement(arc_element, "order")
        order_element.text = str(arc[2])  # Изменяем на индекс кортежа

    return ET.tostring(root, encoding='utf-8').decode('utf-8')


def main():
    input_file = "input.txt"
    output_file = "output.json"

    for arg in sys.argv[1:]:
        key, value = arg.split('=')
        if key == "input1":
            input_file = value
        elif key == "output1":
            output_file = value

    graph, error_message = parse_input_file(input_file)

    if error_message:
        print(error_message)
        return

    print(f"Граф: {graph}")

    json_output = serialize_to_json(graph)
    xml_output = serialize_to_xml(graph)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(json_output)

    print(xml_output)


if __name__ == "__main__":
    main()
