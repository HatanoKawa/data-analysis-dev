# A project can be used to do data analysis jobs

## Disclaimer
The content related to this repo may involve the actual interests of certain companies. This repo is only used for mobile application security research and learning. Do not use this tool for commercial or illegal purposes, or publish anything related to 非公開情報 in a public place (such as SNS). If you are willing to continue reading, please promise to take full responsibility for your actions.
## Usage
***IMPORTANT: create a branch before you start to use, if you want to see diff with git***
### init
1. run generate_base_files.py

### collect data
1. change version_hash (if you don't know how to get version hash, use VNET to catch it)
2. run

### operate data
1. create dump.cs (if you don't know how to get dump.cs, see this repo [il2CppDumper](https://github.com/Perfare/Il2CppDumper))
2. run generate_struct.py
3. run operate_data.py

binary files will be placed by version, others can be diffed with git

## Libs
- [flat-compile](https://github.com/google/flatbuffers)
- [il2CppDumper](https://github.com/Perfare/Il2CppDumper)