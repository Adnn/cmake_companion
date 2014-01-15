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

    def move_name(self, source_name, dest_name):
        moved_files = [group[2].move_name(source_name, dest_name) for group in self.groups]
        [os.rename(file_pair[0], file_pair[1]) for file_pair in moved_files if file_pair]

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

    def sort_unicity_filelist(self):
        self.file_list = sorted(list(set(self.file_list)))

    def complete_filename(self, basename):
        return basename + self.metaref["ext"]
    
    def generate_filelist(self, name_list):
        return [self.complete_filename(basename) for basename in name_list]
        
    def insert_names(self, name_list):
        new_names = self.generate_filelist(name_list)
        self.file_list.extend(new_names)
        self.sort_unicity_filelist()
        return new_names

    def remove_names(self, name_list) :
        removed_names = [name 
                         for name in self.generate_filelist(name_list)
                         if name in self.file_list]
        [self.file_list.remove(name) for name in removed_names]
        return removed_names
        
    def move_name(self, source_name, dest_name) :
        source_file = self.complete_filename(source_name)
        dest_file = self.complete_filename(dest_name)
        if self.file_list.count(source_file):
            self.file_list.remove(source_file)
            self.file_list.append(dest_file)
            self.sort_filelist()
            return (source_file, dest_file)
        else:
            return None
    
    def __str__(self):
        #prepend an empty element, to get the separator before the first elem in file_list
        return "\n    ".join(['']+self.file_list)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Add classes to a project.')
    parser.add_argument ("command", choices=['add', 'mv', 'remove'],
                         help="The action that will be taken on the provided classname(s)")
    parser.add_argument ("classname", nargs="+", help="The name of the class(es) to apply the command onto, in the current project directory.")
    parser.add_argument ("--headers", action="store_true", help="Create header files only. Has the precedence over other filters.")
    parser.add_argument ("--implementations", action="store_true", help="Create implementation files only.")

    args = parser.parse_args()

    cm_file = CMakeFile("CMakeLists.txt")

    if args.command == 'mv' :
        if len(args.classname) != 2:
            sys.exit(1)
        cm_file.move_name(*args.classname)

    elif args.command == 'remove' :
        cm_file.remove_names(args.classname)

    else :
        if args.headers :
            filter = ["headers"]
        elif args.implementations :
            filter = ["implementations"]
        else :
            filter = ["headers", "implementations"]

        cm_file.insert_names(args.classname, filter)

    cm_file.save_file()
