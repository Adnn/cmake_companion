#!/usr/bin/python

import re, argparse

metadata = [
("(?P<declaration>set(\w)*\((\w)*\${PROJECT_NAME}_HEADERS)(?P<files>.*?)\)", ".h"),
("(?P<declaration>set(\w)*\((\w)*\${PROJECT_NAME}_SOURCES)(?P<files>.*?)\)", ".cpp"),
]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Add classes to a project.')
    parser.add_argument ("classname", nargs="+", help="The name of the class that will be added to the current project")
    parser.add_argument ("--headers", action="store_true", help="Create header files only for all lister class names.")

    args = parser.parse_args()

    found_dict = {}

    output_file = ""

    if args.headers :
        filtered_data = [metadata[0]]
    else :
        filtered_data = metadata

    with open("CMakeLists.txt", "r") as cmfile:
            text_file = cmfile.read()
            

            for entry in filtered_data :
                match = re.search(entry[0], text_file, re.DOTALL)
                found_dict[match.end()] = entry + (match,)

            
            previous_marker = 0

            for key in sorted(found_dict.keys()):
                match = found_dict[key][2]

                updated_list = match.group("files").split()
                new_filenames = [basename + found_dict[key][1] for basename in args.classname]
                [open(filename, "a") for filename in new_filenames]
                updated_list.extend(new_filenames)

                output_file += text_file[previous_marker:match.start()]
#We add an empty element at the begining of the list, because we need the joining string before the first non-empty element.
                output_file += match.group("declaration") + "\n    ".join(sorted(['']+updated_list)) + "\n)"
                previous_marker = match.end()

            output_file += text_file[previous_marker:]
    
    with open("CMakeLists.txt", "w") as cmfile:
        cmfile.write(output_file)

