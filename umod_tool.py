
from util_umod import umod_in
from os.path import exists
from os import makedirs
import sys

OPS_LIST = ["-ex", "-exall", "-files", "-fmeta", "-man", "-mant", "-man2", "-meta"]
OPS_PATH_FILE = ["-files", "-fmeta", "-meta"]

def printHelp():
    print("umod_tool.py by Pummelator")
    print("Usage:\n  python3 umod_tool.py [UMOD_PATH] [OPTION] [OUT_PATH]")
    print("Options: -ex, -files, -fmeta, -man, -mant, -man2, -meta")
    print("\nRead doc/cmd_usage.txt for more information")

def argproc(args_in):
    if (len(args_in) <= 1):
        printHelp()
        return "done", {}, ""
    elif (len(args_in) > 4):
        print("Error: Too many arguments")
        return "done", {}, ""
    else:
        file_data = {}
        try:
            file_data = umod_in.umod_path_to_dict(args_in[1])
        except IOError as ex:
            print(ex)
            return "done", {}, ""
        except Exception as ex:
            print(ex)
            return "done", {}, ""
        else:
            if (len(args_in) == 2):
                return "fmeta", file_data, ""
            option = args_in[2]
            if (option not in args_in):
                print("Error: Invalid option '{}'".format(option))
                return "done", {}, ""
            elif (len(args_in) == 3):
                return option.strip('-'), file_data, ""
            if (args_in[3] in OPS_PATH_FILE):
                if (exists(args_in[3])):
                    print("Error: File exists: " + args_in[3])
                    return "done", {}, ""
            else:
                if (not exists(args_in[3])):
                    makedirs(args_in[3])
            return option.strip('-'), file_data, args_in[3]

# Take the metadata from the UMOD and create a nice string output
def strMeta(umod_meta):
    out_str = ""
    namelens = "No"
    if (umod_meta["stores_name_lengths"]):
        namelens = "Yes"
    out_str += "File Size : {} Bytes\n".format(umod_meta["file_size"])
    out_str += "UMOD Ver. : {}\n".format(umod_meta["umod_ver"])
    out_str += "CRC32     : {}\n".format(hex(umod_meta["crc32"]).upper())
    out_str += "File Count: {}\n".format(umod_meta["file_count"])
    out_str += "Stores Name Lengths: {}\n".format(namelens)
    if (umod_meta["game_version_info_count"] == -1):
        out_str += "Error when extracting game version info.\n"
    elif (umod_meta["game_version_info_count"] == 0):
        out_str += "No game version info found."
    else:
        for i in range(umod_meta["game_version_info_count"]):
            out_str += "  Game: {}\n  Version: {}\n".format(umod_meta["game_version_info"][i]["game"], umod_meta["game_version_info"][i]["ver"])
    return out_str

# Take the file list from the UMOD and create a nice string output
def strFiles(umod_filels):
    out_str = ""
    for file_curr in umod_filels:
        out_str += "Path: {}\n".format(file_curr["path"])
        out_str += "Group: {}, Flags: {}\n".format(file_curr["group"], hex(file_curr["flags"]).upper())
        out_str += "Start Byte: {}  ({})\n".format(file_curr["offset"], hex(file_curr["offset"]).upper())
        out_str += "Length    : {} Bytes  ({})\n\n".format(file_curr["length"], hex(file_curr["length"]).upper())
    return out_str


def strTextFile(in_bytes):
    out_str = in_bytes.decode(encoding="cp1252")
    return out_str

### Main Code ###
op_mode = "done"
out_path = ""
umod_dict = {}
op_mode, umod_dict, out_path = argproc(sys.argv)

bin_out = False
multi_file = False
multi_list = []
out_info = ""
# Output Metadata
if (op_mode == "meta"):
    out_info = strMeta(umod_dict["meta"])
# Output File List
elif (op_mode == "files"):
    out_info = strFiles(umod_dict["file_list"])
# Output Metadata and File List
elif (op_mode == "fmeta"):
    out_info = strMeta(umod_dict["meta"]) + "\n"
    out_info += strFiles(umod_dict["file_list"])
# Output Manifest.ini
elif (op_mode == "man"):
    if not (out_path == ""):
        out_path += "/Manifest.ini"
    out_info = "No Manifest.ini found."
    for file_curr in umod_dict["file_list"]:
        if (file_curr["path"].lower() == "system\\manifest.ini"):
            c_off = file_curr["offset"]
            c_len = file_curr["length"]
            out_info = strTextFile(umod_dict["data_bytes"][c_off:c_off+c_len])
            break
# Output Manifest.int
elif (op_mode == "mant"):
    if not (out_path == ""):
        out_path += "/Manifest.int"
    out_info = "No Manifest.int found."
    for file_curr in umod_dict["file_list"]:
        if (file_curr["path"].lower() == "system\\manifest.int"):
            c_off = file_curr["offset"]
            c_len = file_curr["length"]
            out_info = strTextFile(umod_dict["data_bytes"][c_off:c_off+c_len])
            break
# Output Manifest.ini and Manifest.int
elif (op_mode == "man2"):
    if not (out_path == ""):
        multi_file = True
        bin_out = True
    for file_curr in umod_dict["file_list"]:
        if (file_curr["path"].lower() == "system\\manifest.ini" or file_curr["path"].lower() == "system\\manifest.int"):
            c_off = file_curr["offset"]
            c_len = file_curr["length"]
            if (multi_file):
                multi_list.append({
                    "path": out_path + file_curr["path"],
                    "data": umod_dict["data_bytes"][c_off:c_off+c_len]
                })
            else:
                out_info += "\nFILE: " + out_path + file_curr["path"] + "\n"
                out_info += strTextFile(umod_dict["data_bytes"][c_off:c_off+c_len])
# Output files that aren't the Manifest files
elif (op_mode == "ex"):
    multi_file = True
    bin_out = True
    for file_curr in umod_dict["file_list"]:
        if not (file_curr["path"].lower() == "system\\manifest.int" or file_curr["path"].lower() == "system\\manifest.int"):
            c_off = file_curr["offset"]
            c_len = file_curr["length"]
            multi_list.append({
                "path": out_path + file_curr["path"],
                "data": umod_dict["data_bytes"][c_off:c_off+c_len]
            })
# Output ALL files
elif (op_mode == "exall"):
    print("Warning: Extracting manifest files into a game installation will break it.")
    print("Only use this option if the files are being extracted to a new directory.")
    print("Otherwise, use the -ex option\n")
    usrin = input("Extract all files including the manifests anyway (y/N): ")
    if (usrin.lower() == "y" or usrin.lower() == "yes"):
        multi_file = True
        bin_out = True
        for file_curr in umod_dict["file_list"]:
            c_off = file_curr["offset"]
            c_len = file_curr["length"]
            multi_list.append({
                "path": out_path + file_curr["path"],
                "data": umod_dict["data_bytes"][c_off:c_off+c_len]
            })
    else:
        op_mode = "done"

# Output is generated, send it out
if (op_mode == "done"):
    pass
elif (out_path == ""):
    print(out_info)
else:
    out_mode = 'w'
    if (bin_out):
        out_mode = 'wb'
    if (multi_file):
        for file_curr in multi_list:
            print("> " + file_curr["path"])
            dirs_needed = file_curr["path"][0:file_curr["path"].replace('\\', '/').rfind('/')]
            if not (exists(dirs_needed)):
                makedirs(dirs_needed)
            with open(file_curr["path"].replace('\\', '/'), out_mode) as out_file:
                out_file.write(file_curr["data"])
        print("Done.")
    else:
        with open(out_path, out_mode) as out_file:
            out_file.write(out_info)
            print("Output written to " + out_path)
