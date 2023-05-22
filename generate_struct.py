import os
import re
import subprocess
from typing import TextIO

ROOT_DIR = os.path.join(os.path.dirname(__file__))
FLATC_PATH = os.path.join(os.path.dirname(__file__), 'libs', 'flatc.exe')
FBS_PATH = os.path.join(os.path.dirname(__file__), 'data-struct.fbs')

special_key_list = ['From']
duplicate_keys_set = set(special_key_list)
def convert_continuous_uppercase(string):
    pattern = r'[A-Z]{2,}'
    matches = re.findall(pattern, string)
    for match in matches:
        converted = match[0] + match[1:].lower()
        string = string.replace(match, converted)

    if string in duplicate_keys_set:
        return f'{string}_'
    return string


struct_re = re.compile(r'''struct ([^{]*) : [^{]*IFlatbufferObject[^{]*
\{
(.+?)
}''', re.S)
struct_property_re = re.compile(r'''public (.+) (.+?) \{ get; }''', re.M)


def get_struct_dict(source_data):
    struct_dict = {}
    for struct_name, struct_content_str in struct_re.findall(source_data):
        cur_struct = {}
        for prop_res in struct_property_re.finditer(struct_content_str):
            prop_name = prop_res[2]
            prop_type = prop_res[1]
            prop_is_list = False
            if prop_name == 'ByteBuffer':
                continue
            if len(prop_name) > 6 and prop_name.endswith('Length'):
                list_name = prop_name[:-6]
                match = re.search(f'public (.+?) {list_name}\(int j\) {{ }}', struct_content_str)
                if match:
                    prop_type = match[1]
                    prop_name = list_name
                    prop_is_list = True
            if prop_type.startswith('Nullable<'):
                prop_type = prop_type[9:-1]
            if prop_is_list:
                prop_type = f'[{prop_type}]'
            cur_struct[prop_name] = prop_type

        if cur_struct:
            struct_dict[struct_name] = cur_struct

    for struct_key in struct_dict:
        for special_key in special_key_list:
            if special_key in struct_dict[struct_key]:
                struct_dict[struct_key][f'{special_key}_'] = struct_dict[struct_key][special_key]
                del struct_dict[struct_key][special_key]
    return struct_dict


def write_structs_to_fbs(structs: dict, enums: dict, fbs_file: TextIO):
    for key, struct in structs.items():
        fbs_file.write(f"table {key}{{\n")
        for pname, ptype in struct.items():
            if ptype[0] == "[":
                typ = ptype[1:-1]
                if typ.endswith("Length"):
                    typ = typ[:-6]
                if typ not in structs and typ not in enums and typ not in types:
                    continue
                # if pname == typ:
                #     duplicate_keys_set.add(pname)
                #     pname += "_"
            if pname in structs:
                duplicate_keys_set.add(pname)
                pname += '_'
            fbs_file.write(f"    {pname}: {ptype};\n")
        fbs_file.write("}\n\n")


types = ["bool", "byte", "int", "long", "uint", "ulong", "float", "double", "string"]
enum_re = re.compile(r'''// Namespace: FlatData
public enum ([^{]*) // TypeDefIndex: \d+?
\{
	// Fields
	public (.+?) value__; // 0x0
(.+?)
}''', re.S)
enum_field = re.compile(r'public const (.+?) (.+?) = (-?\d+?);')


def get_enum_dict(source_data):
    enum_tree = {}
    for enum_name, enum_type, enum_content_str in enum_re.findall(source_data):
        if '.' in enum_name:
            continue
        fields = {}
        cur_enum = {'format': enum_type, 'fields': fields}
        enum_tree[enum_name] = cur_enum

        for _, field_name, field_num in enum_field.findall(enum_content_str):
            if field_name in fields:
                input()  # don't know why
            fields[field_num] = field_name
    return enum_tree


def write_enums_to_fbs(enums: dict, fbs_file: TextIO):
    for name, enum in enums.items():
        fbs_file.write(
            "enum %s: %s{\n    %s\n}\n\n"
            % (
                name,
                enum['format'],
                ",\n    ".join(
                    f"{key} = {value}" for value, key in enum["fields"].items()
                ),
            )
        )


def create_dumper_wrappers(structs, enums, f):
    typ_to_convert = {
        "string": "ConvertString",
        "int": "ConvertInt",
        "long": "ConvertLong",
        "uint": "ConvertUInt",
        "ulong": "ConvertULong",
        "float": "ConvertFloat",
        "double": "ConvertDouble",
    }
    f.write("from libs.TableEncryptionService import *\n\n")
    f.write("def dump_table(obj) -> list:\n")
    f.write("    typ_name = obj.__class__.__name__[:-5]\n")
    f.write(
        "    try:\n"
    )
    f.write(
        "        dump_func = next(f for x,f in globals().items() if x == f'dump_{typ_name}')\n"
    )
    f.write(
        "    except:\n"
    )
    f.write(
        "        dump_func = None\n"
    )
    f.write(
        "    if not dump_func:\n"
    )
    f.write(
        "       dump_func = next(f for x,f in globals().items() if x.endswith(typ_name))\n"
    )
    f.write("    password = CreateKey(typ_name[:-5])\n")
    f.write(
        "    return [\n        dump_func(obj.DataList(j), password)\n        for j in range(obj.DataListLength())\n    ]\n\n"
    )
    for name, struct in structs.items():
        if name.endswith("Table") and name != 'AnimationBlendTable':
            pass
        #    f.write(f"function dump_{name}(obj) -> list:\n")
        #    f.write("    return [obj.DataList(j) for j in range(obj.DataListLength())]\n\n")
        else:
            f.write(f"def dump_{name}(obj, password) -> dict:\n")
            f.write("    return {\n")

            for pname, ptype in struct.items():
                is_list = False
                if ptype[0] == "[":
                    ptype = ptype[1:-1]
                    is_list = True

                if ptype in typ_to_convert:
                    convert = typ_to_convert[ptype]
                    val_func = f"{convert}(obj.{convert_continuous_uppercase(pname)}(%s), password)"
                elif ptype in enums:
                    convert = typ_to_convert[enums[ptype]["format"]]
                    val_func = f"{ptype}({convert}(obj.{convert_continuous_uppercase(pname)}(%s), password)).name"
                elif ptype == "bool":
                    val_func = f"obj.{convert_continuous_uppercase(pname)}(%s)"
                elif ptype in structs:
                    val_func = f"dump_{ptype}(obj.{convert_continuous_uppercase(pname)}(%s), password)"
                else:
                    raise NotImplementedError(f"{convert_continuous_uppercase(pname)}")
                if is_list:
                    val_func = f"[{val_func % ('j')} for j in range(obj.{convert_continuous_uppercase(pname)}Length())]"
                else:
                    val_func = val_func % ""
                f.write(f"        '{convert_continuous_uppercase(pname)}': {val_func},\n")
            f.write("    }\n\n")

    f.write("from enum import IntEnum\n\n\n")
    for name, enum in enums.items():
        f.write(f"class {name}(IntEnum):\n")
        for value, key in enum["fields"].items():
            if key == "None":
                key = "none"
            f.write(f"    {key} = {value}\n")
        f.write("\n")


if __name__ == '__main__':
    with open('dump.cs', 'r', encoding='utf-8') as f:
        dump_data = f.read()

    struct_dict = get_struct_dict(dump_data)
    enum_dict = get_enum_dict(dump_data)

    with open(os.path.join(ROOT_DIR, 'data-struct.fbs'), 'wt', encoding='utf-8') as f:
        # write namespace header
        f.write("namespace FlatData;\n\n")
        # write enums
        write_enums_to_fbs(enum_dict, f)
        # write structs
        write_structs_to_fbs(struct_dict, enum_dict, f)

    # compile fbs schema to python
    print(subprocess.run(f'"{FLATC_PATH}" --python --scoped-enums "{FBS_PATH}"'))

    # write init file
    init_fp = os.path.join(ROOT_DIR, "FlatData", "__init__.py")
    with open(init_fp, "wt", encoding="utf8") as f:
        for fn in os.listdir(os.path.join(ROOT_DIR, "FlatData")):
            if fn.endswith(".py") and fn not in ["dump.py", "__init__.py"]:
                f.write("from .{n} import {n}\n".format(n=fn[:-3]))

        # write dump helper
        init_fp = os.path.join(ROOT_DIR, "FlatData", "dump.py")
    with open(init_fp, "wt", encoding="utf8") as f:
        create_dumper_wrappers(struct_dict, enum_dict, f)
    # print(duplicate_keys_set)
    # print(struct_dict)
    # print(enum_dict)


# MANY codes are borrowed from K0lb3's repo, really thanks to him.
