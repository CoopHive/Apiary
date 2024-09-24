"""Filter out .dot file for classes relationship plotting."""

file_path = "docs/img/classes_apiary.dot"

search_string = 'arrowhead="diamond"'

with open(file_path, "r") as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if search_string not in line]

with open(file_path, "w") as file:
    file.writelines(filtered_lines)
