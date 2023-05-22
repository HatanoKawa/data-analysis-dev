import json
import logging
import os
import re
import UnityPy
import logger_helper

logger = logger_helper.get_logger(logging.INFO)


def handle_bundle_files():
    for version_hash, source_version_path, output_version_path in [
        (version_hash,
         os.path.join(os.path.dirname(__file__), 'raw', version_hash, 'bundles'),
         os.path.join(os.path.dirname(__file__), 'output', 'bundle_files', version_hash))
        for version_hash in os.listdir(os.path.join(os.path.dirname(__file__), 'raw'))
        if re.match(r'^r[0-9]{2}_[0-9a-zA-Z]{20}$', version_hash)
        and os.path.exists(os.path.join(os.path.dirname(__file__), 'raw', version_hash, 'bundles'))
    ]:
        logger.info(f'handling files of version: {version_hash}')
        bundle_file_list = [
            (file_name,
             os.path.join(source_version_path, file_name))
            for file_name in os.listdir(source_version_path)
        ]
        bundle_file_cnt = 0
        bundle_file_total = len(bundle_file_list)
        for bundle_file_name, source_bundle_path in bundle_file_list:
            bundle_file_cnt += 1
            logger.info(f'Handling bundle file: ({bundle_file_cnt}/{bundle_file_total}) {bundle_file_name}')
            env = UnityPy.load(source_bundle_path)
            for path, obj in env.container.items():
                output_path = os.path.join(output_version_path, path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                try:
                    data = obj.read()
                except AttributeError:
                    logger.error(f'bundle file read fail: {bundle_file_name}')
                    continue
                if obj.type.name in ['Texture2D', 'Sprite']:
                    data.image.save(f'{output_path}.png')
                elif obj.type.name == 'TextAsset':
                    with open(output_path, 'wb') as f:
                        f.write(bytes(data.script))
                elif obj.type.name == 'Mesh':
                    with open(f'{output_path}.obj', 'wt', encoding='utf-8') as f:
                        f.write(data.export())
                elif obj.type.name == 'AudioClip':
                    for name, clip_data in data.samples.items():
                        with open(output_path, 'wb') as f:
                            f.write(clip_data)
                elif obj.type.name == 'Font':
                    path_without_ext, ext = os.path.splitext(output_path)
                    if data.m_FontData:
                        ext = ".ttf"
                        if data.m_FontData[0:4] == b"OTTO":
                            ext = ".otf"
                        with open(path_without_ext[0]+ext, "wb") as f:
                            f.write(data.m_FontData)
                elif obj.type.name == 'Cubemap':
                    fp = os.path.join(os.path.dirname(output_path), f'{output_path}.json')
                    dict_data = data.to_dict()
                    for key in dict_data:
                        if type(dict_data[key]) == memoryview:
                            logger.warning(f'unsupported file type: {obj.type.name}, file path: {path}')
                            dict_data[key] = str(dict_data[key].tobytes())
                    with open(fp, 'wt', encoding='utf-8') as f:
                        json.dump(dict_data, f, ensure_ascii=False, indent=4)
                else:
                    # obj.type.name == 'MonoBehaviour'
                    # MonoBehaviour and others
                    try:
                        if obj.serialized_type.nodes:
                            tree = obj.read_typetree()
                            fp = os.path.join(os.path.dirname(output_path), f'{output_path}.json')
                            with open(fp, 'wt', encoding='utf-8') as f:
                                json.dump(tree, f, ensure_ascii=False, indent=4)
                            continue
                    except TypeError as e:
                        logger.error(f'ERROR: {obj.type.name}:{output_path}:{e}')
                    fp = os.path.join(os.path.dirname(output_path), f'{output_path}.bin')
                    with open(fp, 'wb') as f:
                        f.write(data.raw_data)


if __name__ == '__main__':
    handle_bundle_files()
