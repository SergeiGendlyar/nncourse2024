import json
import sys
import numpy


def load_weights(file_path):
    weights = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                matrix = eval(line.split(':')[1].strip())
                weights.append(numpy.array(matrix))
    return weights


def load_input_vector(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        if line:
            return numpy.array([float(x) for x in line.split(',')])
    return None


def save_output_vector(output_vector, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(', '.join(map(str, output_vector)))


def serialize_network(weights):
    network_structure = {
        'layers': []
    }
    for i, weight in enumerate(weights):
        network_structure['layers'].append({
            'layer': i + 1,
            'weights': weight.tolist()
        })
    return json.dumps(network_structure, indent=4)


def feedforward(weights, input_vector):
    output = input_vector
    for weight in weights:
        output = numpy.dot(output, weight)
    return output


def main():
    input1 = 'input.txt'
    input2 = 'input_vector.txt'
    output1 = 'output.json'
    output2 = 'output_vector.txt'

    for arg in sys.argv[1:]:
        key, value = arg.split('=')
        if key == 'input1':
            input1 = value
        elif key == 'input2':
            input2 = value
        elif key == 'output1':
            output1 = value
        elif key == 'output2':
            output2 = value

    try:
        weights = load_weights(input1)
        input_vector = load_input_vector(input2)

        if input_vector is None:
            raise ValueError("Ошибка: неверный формат входного вектора.")

        output_vector = feedforward(weights, input_vector)
        network_json = serialize_network(weights)

        with open(output1, 'w', encoding='utf-8') as f:
            f.write(network_json)

        save_output_vector(output_vector, output2)

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
