import base64
from typing import Union
from zipfile import ZipFile
from xxhash import xxh32_intdigest
from libs.MersenneTwister import MersenneTwister
import utils
import os
import json
from libs.TableEncryptionService import XOR
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Protocol.KDF import PBKDF2

# need to run generate_struct.py first
import FlatData as FlatData
from FlatData.dump import dump_table

lower_name_to_module_dict = {
    key.lower(): value for key, value in FlatData.__dict__.items()
}

SOURCE_DIR = os.path.join(os.path.dirname(__file__), 'raw', 'table')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output', 'table_files')
os.makedirs(OUTPUT_DIR, exist_ok=True)

BlockSize: int = 128 // 8
Keysize: int = 128 // 8
DerivationIterations: int = 1000


def Decrypt(cipherText: str, passPhrase: str) -> str:
    rawCipherText = base64.b64decode(cipherText)
    salt = rawCipherText[:16]
    iv = rawCipherText[16:32]
    rawCipherText = rawCipherText[32:]
    derived = PBKDF2(passPhrase, salt, 16, count=1000)
    cipher = AES.new(key=derived[:16], iv=iv, mode=AES.MODE_CBC)
    return unpad(cipher.decrypt(rawCipherText), BlockSize, style="pkcs7").decode('utf-8')


def calcPass(name: Union[bytes, str]) -> bytes:
    if isinstance(name, str):
        name = name.encode("utf8")
    seed = xxh32_intdigest(name, 0)
    mersenne_twister = MersenneTwister(seed=seed)
    tmp = mersenne_twister.NextBytes(int(3 * 20 / 4))
    return base64.b64encode(tmp)


def main():
    for table_file in os.listdir(SOURCE_DIR):
        # only process .zip files
        if not table_file.endswith(".zip"):
            continue

        table_dir_fp = os.path.join(OUTPUT_DIR, table_file[:-4])
        os.makedirs(table_dir_fp, exist_ok=True)
        table_zip_file = ZipFile(os.path.join(SOURCE_DIR, table_file))
        table_zip_file.setpassword(calcPass(table_file))
        for name in table_zip_file.namelist():
            data = table_zip_file.read(name)
            if name.endswith(".json"):
                if name == utils.get_b64_data(b'bG9naWNlZmZlY3RkYXRhLmpzb24='):
                    data = Decrypt(data, utils.get_b64_data(b'TG9naWNFZmZlY3REYXRh')).encode("utf8")
                elif name == utils.get_b64_data(b'bmV3c2tpbGxkYXRhLmpzb24='):
                    data = Decrypt(data, utils.get_b64_data(b'TmV3U2tpbGxEYXRh')).encode("utf8")
            elif table_file == "Excel.zip":
                print(name)
                # these files' struct can't be picked from dump.cs
                if name in [utils.get_b64_data(b'YW5pbWF0aW9uYmxlbmR0YWJsZS5ieXRlcw=='), utils.get_b64_data(b'bmFtZWluZm9leGNlbHRhYmxlLmJ5dGVz')]:
                    print(f'skip {name}')
                    continue
                # flatbuffer_cls = lower_name_to_module_dict[name[:-6]]
                # data = XOR(flatbuffer_cls.__name__, data)
                # flatbuffer = flatbuffer_cls.GetRootAs(data)
                # data = json.dumps(
                #     dump_table(flatbuffer), indent=4, ensure_ascii=False
                # ).encode("utf8")
                # name = f"{flatbuffer_cls.__name__}.json"
                try:
                    flatbuffer_cls = lower_name_to_module_dict[name[:-6]]
                    data = XOR(flatbuffer_cls.__name__, data)
                    flatbuffer = flatbuffer_cls.GetRootAs(data)
                    data = json.dumps(
                        dump_table(flatbuffer), indent=4, ensure_ascii=False
                    ).encode("utf8")
                    name = f"{flatbuffer_cls.__name__}.json"
                except Exception as e:
                    print(e)
                    continue
            fp = os.path.join(table_dir_fp, name)
            with open(fp, "wb") as f:
                f.write(data)


if __name__ == "__main__":
    main()
