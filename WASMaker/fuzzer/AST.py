import json

import pymongo

from WASMaker.fuzzer.instructions import *
from WASMaker.parser.instruction import Instruction
from WASMaker.parser.opnames import *


class Node:
    def __init__(self, instr, instr_type, context=None):
        self.id = None
        self.instr = instr
        self.opcode = self.instr.opcode
        self.sub_instrs = []
        self.type = instr_type
        self.context = context

    def copy(self, node):
        self.id = node.id
        self.instr = node.instr
        self.opcode = node.instr.opcode
        self.type = node.type
        self.context = node.context
        self.sub_instrs = node.sub_instrs


def compare_json_node(p, q):
    if p["instr"] != q["instr"]:
        return False

    if len(p["sub_instrs"]) != len(q["sub_instrs"]):
        return False

    for i in range(len(p["sub_instrs"])):
        if not compare_json_node(p["sub_instrs"][i], q["sub_instrs"][i]):
            return False

    return True


class FunctionAST():
    def __init__(self, binary, inner_func_id):
        self.binary = binary
        self.inner_func_id = inner_func_id
        self.AST = None

    def init_AST(self, instrs):
        AST_nodes = []
        for _, i in enumerate(instrs):
            # Block Loop
            if i.opcode in [Block, Loop]:
                instr_type, instr_context = instr_table[i.opcode](self.binary, i.args, self.inner_func_id)
                node = Node(i, instr_type, instr_context)
                node.sub_instrs = self.init_AST(i.args.instrs)
                AST_nodes.append(node)
                continue
            # If
            elif i.opcode == If:
                instr_type, instr_context = instr_table[i.opcode](self.binary, i.args, self.inner_func_id)
                node = Node(i, instr_type, instr_context)

                result = AST_nodes[-1].type["results"]
                if result == [ValTypeI32]:
                    judge_condition_node = AST_nodes.pop()
                    node.sub_instrs.append(judge_condition_node)

                node.sub_instrs.extend(self.init_AST(i.args.instrs1))
                else_instr = Instruction(Else_, None)
                else_instr_type, else_instr_context = instr_table[else_instr.opcode](self.binary, else_instr.args,
                                                                                     self.inner_func_id)
                node.sub_instrs.append(Node(else_instr, else_instr_type, else_instr_context))
                node.sub_instrs.extend(self.init_AST(i.args.instrs2))
                AST_nodes.append(node)
                continue
            # other instrs
            instr_type, instr_context = instr_table[i.opcode](self.binary, i.args, self.inner_func_id)
            node = Node(i, instr_type, instr_context)
            if not AST_nodes:
                AST_nodes.append(node)
            else:
                # select
                if i.opcode == Select:
                    if len(AST_nodes[-1].type["results"]) > 1:
                        j = 0
                        for result in reversed(AST_nodes[-1].type["results"]):
                            j += 1
                            if j == 2:
                                node.type["params"][0] = result
                                node.type["params"][1] = result
                                node.type["results"][0] = result
                                break
                    else:
                        for result in reversed(AST_nodes[-2].type["results"]):
                            node.type["params"][0] = result
                            node.type["params"][1] = result
                            node.type["results"][0] = result
                            break
                params = instr_type["params"].copy()
                while params != []:
                    for _, result in enumerate(reversed(AST_nodes[-1].type["results"])):
                        if result == params[-1] or params[-1] == ValTypeAny or result == ValTypeAny:
                            params.pop()
                        else:
                            raise Exception("something error!")
                    sub_node = AST_nodes.pop()
                    node.sub_instrs.insert(0, sub_node)
                AST_nodes.append(node)
        self.AST = AST_nodes
        return AST_nodes


class NodeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Node):
            serializable = {'id': obj.id, 'instr': obj.instr.to_json(), 'type': obj.type, 'opcode': obj.opcode}
            if obj.context is not None:
                serializable['context'] = obj.context.to_json()
            else:
                serializable['context'] = None
            serializable['sub_instrs'] = []
            for sub_instr in obj.sub_instrs:
                serializable['sub_instrs'].append(self.default(sub_instr))
            return serializable
        else:
            pass
        return json.JSONEncoder.default(self, obj)


def ast_to_json(ast_tree):
    return json.dumps(ast_tree, cls=NodeEncoder)


def store_mongodb(AST_nodes_json):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxRecursionDepth=1000")
    runtime_fuzz_db = myclient["runtime-fuzz"]

    for node in AST_nodes_json:
        instr_opcode = node["opcode"]
        instr_name = opnames[instr_opcode]
        instr_col = runtime_fuzz_db[instr_name]

        exist_count = instr_col.count_documents({})
        if exist_count == 0:
            instr_col.insert_one(node)

        is_equal = False
        for mongo_node in instr_col.find():
            if compare_json_node(node, mongo_node):
                is_equal = True
                break

        if not is_equal:
            instr_col.insert_one(node)
