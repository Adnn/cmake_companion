#!/usr/bin/python

import re, argparse, os

class CMakeFile:
    metadata = {
        "headers" :         {"regex" : "(?P<declaration>set(\w)*\((\w)*\${PROJECT_NAME}_HEADERS)(?P<files>.*?)\)", "ext" : ".h"},
        "implementations" : {"regex" : "(?P<declaration>set(\w)*\((\w)*\${PROJECT_NAME}_SOURCES)(?P<files>.*?)\)", "ext" : ".cpp"},
        }

    def __init__(self, filename):
        self.filename = filename
        self.outro = "";
        self.groups = [];

        with open(self.filename, "r") as cmfile:
            text_file = cmfile.read()

            found_dict = {}
            for key, value in CMakeFile.metadata.iteritems():
                match = re.search(value["regex"], text_file, re.DOTALL)
                found_dict[match.end()] = value
                found_dict[match.end()].update({"match" : match})
                found_dict[match.end()].update({"category" : key})

            previous_match_end = 0

            for key in sorted(found_dict.keys()):
                entry = found_dict[key]
                match = entry["match"] 
                self.groups.append( (text_file[previous_match_end:match.start()],
                                     match.group("declaration"),
                                     FileList(match.group("files"), entry["category"]),
                                     "\n)", 
                                     ))
                previous_match_end = match.end()

            self.outro = text_file[previous_match_end:]

    def insert_names(self, name_list, category_filter_list):
        new_files = \
            [file_list.insert_names(name_list)
            for file_list in [group[2] for group in self.groups]
            if file_list.category in category_filter_list]

        [open(filename, "a") for filename_list in new_files for filename in filename_list]

    def remove_names(self, name_list):
        removed_files = \
            [group[2].remove_names(name_list) for group in self.groups]
        
        [os.remove(filename) for filename_list in removed_files for filename in filename_list]

    def save_file(self):
        output_file = ''.join(str(i) for group in self.groups for i in group)
        output_file = output_file + self.outro

        with open(self.filename, "w") as cmfile:
            cmfile.write(output_file)


class FileList:
    def __init__(self, string_list, category):
        self.category = category
        self.metaref = CMakeFile.metadata[self.category]
        self.file_list = string_list.split()

    def insert_names(self, name_list):
        new_names = [basename + self.metaref["ext"]
                     for basename in name_list]
        self.file_list.extend(new_names)
        self.file_list = sorted(self.file_list)
        return new_names

    def remove_names(self, name_list) :
        removed_names = [name 
                         for name in [basename + self.metaref["ext"] for basename in name_list]
                         if name in self.file_list]
        [self.file_list.remove(name) for name in removed_names]
        return removed_names
        
    def __str__(self):
        #prepend an empty element, to get the separator before the first elem in file_list
        return "\n    ".join(['']+self.file_list)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Add classes to a project.')
    parser.add_argument ("classname", nargs="+", help="The name of the class that will be added to the current project")
    parser.add_argument ("--headers", action="store_true", help="Create header files only for listed names.")
    parser.add_argument ("--remove", action="store_true", help="Remove the entries from the CMake file, and delete the corresponding files from the directory.")

    args = parser.parse_args()

    cm_file = CMakeFile("CMakeLists.txt")

    if args.remove :
        cm_file.remove_names(args.classname)
    else :
        if args.headers :
            filter = ["headers"]
        else :
            filter = ["headers", "implementations"]

        cm_file.insert_names(args.classname, filter)

    cm_file.save_file()

    
'''
    with open("CMakeLists.txt", "r") as cmfile:
            text_file = cmfile.read()
            

            for entry in filtered_data :
                match = re.search(entry[0], text_file, re.DOTALL)
                found_dict[match.end()] = entry + (match,)

            
            previous_marker = 0

            for key in sorted(found_dict.keys()):
                match = found_dict[key][2]

                updated_list = match.group("files")
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
'''
