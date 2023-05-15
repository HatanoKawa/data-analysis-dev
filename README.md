# A project can be used to do data analysis jobs

## Disclaimer
The content related to this repo may involve the actual interests of certain companies. This repo is only used for mobile application security research and learning. Do not use this tool for commercial or illegal purposes, or publish anything related to 非公開情報 in a public place (such as SNS). If you are willing to continue reading, please promise to take full responsibility for your actions.
## Usage
***IMPORTANT: create a branch before you start to use, if you want to see diff with git***
### init
1. run generate_base_files.py to create database and example  file

### collect data
1. change version_hash (if you don't know how to get version hash, use VNET to catch it)
2. run collect_data.py, and if the process suspend frequently, change proxy settings in options.json

### handle data
*scripts handling data don't depend on database*
#### handle bundle data
1. run handle_bundle_files.py

*The handle_bundle_files.py script still has many issues, but since I'm not particularly interested in AB assets, I won't make any further adjustments to this script in the short term (and maybe never). If anyone is interested in this and has any suggestions, or would like to contribute code, please feel free to do so.*
*If you want data immediately, use [AssetRipper](https://github.com/AssetRipper/AssetRipper)(**recommend**, still under maintenance) or [AssetStudioGUI](https://github.com/Perfare/AssetStudio)(archived) or [UtinyRipper](https://github.com/mafaca/UtinyRipper)(seems to be out of maintenance) to get what you want.*

#### handle table data
1. create dump.cs (if you don't know how to get dump.cs, see this repo [il2CppDumper](https://github.com/Perfare/Il2CppDumper))
2. run generate_struct.py
3. run handle_table_files.py
4. commit all changes and write version_hash and update time in commit message to show diffrences between different versions 

#### handle binary data
**need to run handle_table_data.py first to enable character name translator**
1. run handle_binary_files.py, and it will automatically create symlink folders.

binary files will be grouped by version, others can be diffed with git

## Libs
- [flat-compile](https://github.com/google/flatbuffers)
- [il2CppDumper](https://github.com/Perfare/Il2CppDumper)