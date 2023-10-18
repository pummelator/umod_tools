
from os.path import isfile

UMOD_MAGIC = 0x9FE3C5A3
STD_TOP_PATHS = ["system", "system64", "systemlocalized", "help", "manual", "maps", "music", "patches", "sounds", "textures", "web"]

# UMOD format uses a compacted system for storing the number of files
# and the length of file names
# https://beyondunrealwiki.github.io/pages/package-file-format-data-de.html
def index_interpret(in_bytes):
    int_out = 0
    negate = 1
    length = 1
    # Determine if number is positive or negative
    if (in_bytes[0] & 0x80):
        negate = -1
    # Process first byte
    if (in_bytes[0] & 0x40):
        int_out = (in_bytes[0] & 0x3F)
    else:
        return {"value":((in_bytes[0] & 0x3F) * negate), "self_length":length}
    # Process the used middle bytes
    for i in range(1,4):
        int_out |= int(in_bytes[i] & 0x7F) << ((7*(i-1))+6)
        length += 1
        if not (in_bytes[i] & 0x80):
            break
    # Process the last byte if used
    if ((in_bytes[3] & 0x80) and length == 4):
        int_out |= int(in_bytes[4]) << 27
    #
    return {"value":(int_out * negate), "self_length":length}

# Processes the remaining data from a file listing
def complete_file_listing(in_name, last_bytes):
    offset = int.from_bytes(last_bytes[0:4], "little")
    fleng = int.from_bytes(last_bytes[4:8], "little")
    flags = int.from_bytes(last_bytes[8:12], "little")
    top_level = (in_name.split('\\'))[0]
    group = "(Other)"
    if (top_level.lower() in STD_TOP_PATHS):
        group = top_level
    out_dict = {
        "path": in_name,
        "group": group,
        "offset": offset,
        "length": fleng,
        "flags": flags
    }
    return out_dict

# Takes a file path and processes the file as a UMOD, returning the data in
# a more convenient-to-use dictionary
def umod_path_to_dict(file_path):
    # Begin processing file
    if not (isfile(file_path)):
        raise IOError("File not found")
    in_bytes = bytes()
    with open(file_path, 'rb') as f_in:
        in_bytes = f_in.read()

    # Process header
    hloc = len(in_bytes) - 20     # header location
    magic_in = int.from_bytes(in_bytes[hloc:hloc+4], "little")
    if not (magic_in == UMOD_MAGIC):
        raise Exception("Magic value does not match. Is the file either a UMOD or UT2MOD?")
    filedir_offset = int.from_bytes(in_bytes[hloc+4:hloc+8], "little")
    file_size = int.from_bytes(in_bytes[hloc+8:hloc+12], "little")
    umod_ver = int.from_bytes(in_bytes[hloc+12:hloc+16], "little")
    crc32_checksum = int.from_bytes(in_bytes[hloc+16:hloc+20], "little")

    # Process file list
    file_count = index_interpret(in_bytes[filedir_offset:filedir_offset+5])
    curr_loc = filedir_offset + file_count["self_length"]
    # Depending on UMOD version, string lengths for strings may (most) or may not (very old) be stored.
    # With the first file, determine if the first byte is a compacted index giving a length.
    stores_lengths = False
    name_length = index_interpret(in_bytes[curr_loc:curr_loc+5])
    # Check for null terminator
    if not (in_bytes[curr_loc + name_length["self_length"] + name_length["value"]]):
        stores_lengths = True
    file_list = []
    if (stores_lengths):
        for i in range(file_count["value"]):
            name_length = index_interpret(in_bytes[curr_loc:curr_loc+5])
            curr_loc += name_length["self_length"]
            curr_name = in_bytes[curr_loc:curr_loc+name_length["value"]-1].decode(encoding="cp1252")
            curr_loc += name_length["value"]
            curr_dict = curr_dict = complete_file_listing(curr_name, in_bytes[curr_loc:curr_loc+12])
            file_list.append(curr_dict)
            curr_loc += 12
    else:
        for i in range(file_count["value"]):
            curr_name_b = bytes()
            while (in_bytes[curr_loc]):
                curr_name_b.append(in_bytes[curr_loc])
                curr_loc += 1
            curr_name = curr_name_b.decode(encoding="cp1252")
            curr_loc += 1   # Still pointing to null term after the while loop
            curr_dict = complete_file_listing(curr_name, in_bytes[curr_loc:curr_loc+12])
            file_list.append(curr_dict)
            curr_loc += 12

    # Comb through Manifest.ini to find product and version information
    manifest_present = False
    manifest_start = 0
    manifest_len = 0
    detected_game = []
    detected_version = []
    for curr_dict in file_list:
        if (curr_dict["path"].lower() == "system\\manifest.ini"):
            manifest_present = True
            manifest_start = curr_dict["offset"]
            manifest_len = curr_dict["length"]
            break
    if (manifest_present):
        manifest_strlist = in_bytes[manifest_start:manifest_len].decode(encoding="cp1252").split('\r\n')
        for line in manifest_strlist:
            lowline = line.lower()
            if ("product" in lowline):
                detected_game.append(line.split('=')[1].strip())
            elif ("version" in lowline):
                detected_version.append(line.split('=')[1].strip())

    num_detected = 0
    game_version_info = []
    if (len(detected_game) == len(detected_version)):
        num_detected = len(detected_game)
        for i in range(num_detected):
            curr_dict = {
                "game": detected_game[i],
                "ver": detected_version[i]
            }
            game_version_info.append(curr_dict)
    else:
        num_detected = -1

    # Collect processed information into return dictionary
    out_dict_meta = {
        "files_offset": filedir_offset,
        "file_size": file_size,
        "umod_ver": umod_ver,
        "crc32": crc32_checksum,
        "file_count": file_count["value"],
        "stores_name_lengths": stores_lengths,
        "game_version_info_count": num_detected,
        "game_version_info": game_version_info
    }
    out_dict = {
        "meta": out_dict_meta,
        "file_list": file_list,
        "data_bytes": in_bytes[0:filedir_offset]
    }
    return out_dict
