import os

import pymongo
from BREWasm import *

from WASMaker.fuzzer.AST import *
from WASMaker.parser.opnames import *
from WASMaker.settings import *

my_client = pymongo.MongoClient(MONGODB_URI)
runtime_fuzz_db = my_client[MONGODB_CLIENT]


def clear_mongodb():
    db = my_client[MONGODB_CLIENT]

    collections = db.list_collection_names()

    for collection in collections:
        db[collection].drop()


def init_mongodb():
    collection_names = opnames

    for collection_name in collection_names:
        if collection_name:
            runtime_fuzz_db[collection_name].insert_one({})
            runtime_fuzz_db[collection_name].delete_many({})


clear_mongodb()
init_mongodb()

try:
    for root, dirs, files in os.walk(BENCHMARK_PATH):
        for file in files:
            file_path = os.path.join(root, file)

            wasm_binary = BREWasm(file_path)

            internal_func_num = len(wasm_binary.module.code_sec)

            for i in range(internal_func_num):
                function_AST = FunctionAST(wasm_binary, i)
                AST_list = function_AST.init_AST(function_AST.binary.module.code_sec[i].expr)

                json_string = ast_to_json(AST_list)
                AST_nodes_json = json.loads(json_string)

                store_mongodb(AST_nodes_json)
                print("function :" + str(i))
except Exception as e:
    print(e)
