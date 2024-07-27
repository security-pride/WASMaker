import random
import string
import struct

import numpy

from WASMaker.fuzzer.AST import Node
from WASMaker.fuzzer.stack_mapping import *
from WASMaker.parser.instruction import Instruction, MemArg, MemLaneArg
from WASMaker.parser.module import Export, ExportDesc
from WASMaker.parser.types import BlockTypeV128


def generate_random_number(valtype):
    rand_prob = random.random()
    if valtype == ValTypeI32:
        if rand_prob < 0.7:
            return random.randint(0, 1)
        elif rand_prob < 0.95:
            return 0
        else:
            return 2 ** 31 - 1
    elif valtype == ValTypeI64:
        if rand_prob < 0.7:
            return random.randint(0, 2 ** 64 - 1)
        elif rand_prob < 0.95:
            return 0
        else:
            return 2 ** 64 - 1
    elif valtype == ValTypeF32:
        if rand_prob < 0.7:
            random_float = struct.unpack('f', struct.pack('I', random.randint(0, 2 ** 31 - 1)))[0]
            return random_float
        elif rand_prob < 0.95:
            return 0.0
        else:
            max_float = struct.unpack('f', struct.pack('I', 2 ** 31 - 1))[0]
            return max_float
    elif valtype == ValTypeF64:
        if rand_prob < 0.7:
            random_int64 = random.getrandbits(64)
            random_float = float(random_int64)
            return random_float
        elif rand_prob < 0.95:
            return 0.0
        else:
            max_float = float(2 ** 64 - 1)
            return max_float
    elif valtype == ValTypeV128:
        if rand_prob < 0.7:
            return random.randint(0, 2 ** 128 - 1)
        elif rand_prob < 0.95:
            return 0
        else:
            return 2 ** 128 - 1


def get_substitute_instrs(params_type, results_type):
    for instrs in instrs_list:
        if instrs['stack_type'][0] == params_type and instrs['stack_type'][1] == results_type:
            return random.choice(instrs['instrs'])

    return None


def primitive2simd(root):
    stack = [(root, None)]  # Stack to keep track of nodes and their parents
    visited = set()  # Set to keep track of visited nodes

    while stack:
        node, parent_node = stack[-1]  # Peek at the top of the stack

        # If node has unvisited children, push them onto the stack
        if node.sub_instrs and all(child in visited for child in node.sub_instrs) is False:
            for child in reversed(node.sub_instrs):
                if child not in visited:
                    stack.append((child, node))
        elif node in visited:
            stack.pop()
            if parent_node != None and parent_node.instr.opcode in [If, Block, Loop, BrIf, BrTable, Call,
                                                                    CallIndirect] and parent_node not in visited:
                visited.add(parent_node)
                if parent_node.type["params"] != [] and parent_node.instr.opcode in [If, BrTable, BrIf, CallIndirect]:
                    if parent_node.instr.opcode == CallIndirect:
                        drop_instr = Node(Instruction(Drop, None), instr_type={'params': [ValTypeAny], 'results': []})
                        drop_instr.sub_instrs.append(parent_node.sub_instrs[-1])
                        visited.add(drop_instr)
                        i32const_instr = Node(Instruction(I32Const, random.randint(0, 1)),
                                              instr_type={'params': [], 'results': [ValTypeI32]})
                        i32const_instr.sub_instrs.append(drop_instr)
                        visited.add(i32const_instr)
                        parent_node.sub_instrs[-1] = i32const_instr
                    else:
                        drop_instr = Node(Instruction(Drop, None), instr_type={'params': [ValTypeAny], 'results': []})
                        drop_instr.sub_instrs.append(parent_node.sub_instrs[0])
                        visited.add(drop_instr)
                        i32const_instr = Node(Instruction(I32Const, random.randint(0, 1)),
                                              instr_type={'params': [], 'results': [ValTypeI32]})
                        i32const_instr.sub_instrs.append(drop_instr)
                        visited.add(i32const_instr)
                        parent_node.sub_instrs[0] = i32const_instr
                    if parent_node.instr.opcode == If and parent_node.type["results"] != []:
                        parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])
                        parent_node.instr.args = BlockTypeV128
                elif parent_node.instr.opcode in [Block, Loop] and parent_node.type["results"] != []:
                    parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])
                    parent_node.instr.args = BlockTypeV128

                if parent_node.instr.opcode in [Call, CallIndirect]:
                    parent_node.context.functype["param_types"] = [ValTypeV128] * len(
                        parent_node.context.functype["param_types"])
                    parent_node.context.functype["result_types"] = [ValTypeV128] * len(
                        parent_node.context.functype["result_types"])
                    if parent_node.instr.opcode == CallIndirect:
                        parent_node.type["params"] = [ValTypeV128] * (
                                len(parent_node.type["params"]) - 1) + [ValTypeI32]
                    else:
                        parent_node.type["params"] = [ValTypeV128] * len(parent_node.type["params"])
                    parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])
        else:
            # If node has no children or all children are visited, process the node
            node, parent_node = stack.pop()  # Remove the node from the stack
            visited.add(node)  # Mark node as visited

            if parent_node != None and parent_node.instr.opcode in [If, Block, Loop, BrTable, BrIf,
                                                                    Call, CallIndirect] and parent_node not in visited:
                visited.add(parent_node)
                if parent_node.type["params"] != [] and parent_node.instr.opcode in [If, BrTable, BrIf, CallIndirect]:
                    if parent_node.instr.opcode == CallIndirect:
                        drop_instr = Node(Instruction(Drop, None), instr_type={'params': [ValTypeAny], 'results': []})
                        drop_instr.sub_instrs.append(parent_node.sub_instrs[-1])
                        visited.add(drop_instr)
                        i32const_instr = Node(Instruction(I32Const, random.randint(0, 1)),
                                              instr_type={'params': [], 'results': [ValTypeI32]})
                        i32const_instr.sub_instrs.append(drop_instr)
                        visited.add(i32const_instr)
                        parent_node.sub_instrs[-1] = i32const_instr
                    else:
                        drop_instr = Node(Instruction(Drop, None), instr_type={'params': [ValTypeAny], 'results': []})
                        drop_instr.sub_instrs.append(parent_node.sub_instrs[0])
                        visited.add(drop_instr)
                        i32const_instr = Node(Instruction(I32Const, random.randint(0, 1)),
                                              instr_type={'params': [], 'results': [ValTypeI32]})
                        i32const_instr.sub_instrs.append(drop_instr)
                        visited.add(i32const_instr)
                        parent_node.sub_instrs[0] = i32const_instr
                    if parent_node.instr.opcode == If and parent_node.type["results"] != []:
                        parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])
                        parent_node.instr.args = BlockTypeV128
                elif parent_node.instr.opcode in [Block, Loop] and parent_node.type["results"] != []:
                    parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])
                    parent_node.instr.args = BlockTypeV128

                if parent_node.instr.opcode in [Call, CallIndirect]:
                    parent_node.context.functype["param_types"] = [ValTypeV128] * len(
                        parent_node.context.functype["param_types"])
                    parent_node.context.functype["result_types"] = [ValTypeV128] * len(
                        parent_node.context.functype["result_types"])
                    if parent_node.instr.opcode == CallIndirect:
                        parent_node.type["params"] = [ValTypeV128] * (len(parent_node.type["params"]) - 1) + [
                            ValTypeI32]
                    else:
                        parent_node.type["params"] = [ValTypeV128] * len(parent_node.type["params"])
                    parent_node.type["results"] = [ValTypeV128] * len(parent_node.type["results"])

            if node.instr.opcode not in [Block, Loop, Else_, If, End_, LocalSet, LocalGet, LocalTee, Call, CallIndirect,
                                         Br, BrIf, BrTable, GlobalSet, GlobalGet, Select]:
                instr_type = node.type

                if len(instr_type['params']) == 0 and len(instr_type['results']) == 1:
                    subs_node = Node(Instruction(V128Const, generate_random_number(ValTypeV128)),
                                     instr_type={'params': [], 'results': [ValTypeV128]})
                    subs_node.sub_instrs = node.sub_instrs
                    node.copy(subs_node)

                elif len(instr_type['params']) == 1 and len(instr_type['results']) == 1:
                    instrs_1_to_1 = I32_to_V128['instrs'] + I64_to_V128['instrs'] + F32_to_V128['instrs'] + F64_to_V128[
                        'instrs'] + V128_to_I32['instrs'] + V128_to_I64['instrs'] + V128_to_F32['instrs'] + V128_to_F64[
                                        'instrs'] + V128_to_V128['instrs']
                    if parent_node == None:
                        subs_instr = random.choice(
                            I32_to_V128['instrs'] + I64_to_V128['instrs'] + F32_to_V128['instrs'] + F64_to_V128[
                                'instrs'] + V128_to_V128['instrs'])
                    else:
                        subs_instr = random.choice(instrs_1_to_1)
                    subs_instr_name = opnames[subs_instr]
                    if subs_instr in I32_to_V128['instrs']:
                        if subs_instr_name.find("load") == -1:

                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeI32], 'results': [ValTypeV128]})
                        else:

                            subs_node = Node(Instruction(subs_instr, MemArg(align=0, offset=random.randint(0, 10000))),
                                             instr_type={'params': [ValTypeI32], 'results': [ValTypeV128]},
                                             context=Context(memory={"min": 10, "max": 32768}))
                        subs_node.sub_instrs.append(Node(Instruction(I32Const, generate_random_number(ValTypeI32)),
                                                         instr_type={'params': [], 'results': [ValTypeI32]}))
                        node.copy(subs_node)
                    elif subs_instr in I64_to_V128['instrs'] + F32_to_V128['instrs'] + F64_to_V128['instrs']:
                        if subs_instr in I64_to_V128['instrs']:
                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeI64], 'results': [ValTypeV128]})
                            subs_node.sub_instrs.append(Node(Instruction(I64Const, generate_random_number(ValTypeI32)),
                                                             instr_type={'params': [], 'results': [ValTypeI64]}))
                        elif subs_instr in F32_to_V128['instrs']:
                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeF32], 'results': [ValTypeV128]})
                            subs_node.sub_instrs.append(Node(Instruction(F32Const, generate_random_number(ValTypeF32)),
                                                             instr_type={'params': [], 'results': [ValTypeF32]}))
                        elif subs_instr in F64_to_V128['instrs']:
                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeF64], 'results': [ValTypeV128]})
                            subs_node.sub_instrs.append(
                                Node(Instruction(F64Const, generate_random_number(ValTypeF64)),
                                     instr_type={'params': [], 'results': [ValTypeF64]}))
                        node.copy(subs_node)
                    elif subs_instr in V128_to_I32['instrs'] + V128_to_I64['instrs'] + V128_to_F32['instrs'] + \
                            V128_to_F64['instrs']:

                        if opnames[subs_instr].find("lane") != -1:

                            if subs_instr in V128_to_I32['instrs']:
                                subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                                 instr_type={'params': [ValTypeV128], 'results': [ValTypeI32]})
                                subs_node.sub_instrs = node.sub_instrs

                                node.copy(subs_node)
                                if parent_node not in visited or parent_node == None or (
                                        parent_node in visited and parent_node.instr.opcode in [Call, CallIndirect, If,
                                                                                                Block]):
                                    if parent_node.instr.opcode == CallIndirect and (
                                            len(parent_node.type["params"]) == 1 or node not in parent_node.sub_instrs[
                                                                                                :-1]):
                                        pass
                                    elif parent_node.instr.opcode == If and (node not in parent_node.sub_instrs[1:]):
                                        pass
                                    else:
                                        parent_instr = random.choice(I32_to_V128['instrs'])
                                        if opnames[parent_instr].find("load") == -1:
                                            subs_parent_node = Node(
                                                Instruction(parent_instr, None),
                                                instr_type={'params': [ValTypeI32], 'results': [ValTypeV128]})
                                        else:
                                            subs_parent_node = Node(Instruction(parent_instr, MemArg(align=0,
                                                                                                     offset=random.randint(
                                                                                                         0, 10000))),
                                                                    instr_type={'params': [ValTypeI32],
                                                                                'results': [ValTypeV128]},
                                                                    context=Context(memory={"min": 10, "max": 32768}))
                                        if parent_node == None:
                                            parent_node = subs_parent_node
                                            root = parent_node
                                        else:
                                            index = parent_node.sub_instrs.index(node)
                                            parent_node.sub_instrs[index] = subs_parent_node
                                        subs_parent_node.sub_instrs.append(node)
                                        # Mark the parent node as visited
                                        visited.add(subs_parent_node)
                            elif subs_instr in V128_to_I64['instrs']:
                                subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                                 instr_type={'params': [ValTypeV128], 'results': [ValTypeI64]})
                                subs_node.sub_instrs = node.sub_instrs
                                node.copy(subs_node)
                                if parent_node not in visited or parent_node == None or (
                                        parent_node in visited and parent_node.instr.opcode in [Call, CallIndirect, If,
                                                                                                Block]):
                                    if parent_node.instr.opcode == CallIndirect and (
                                            len(parent_node.type["params"]) == 1 or node not in parent_node.sub_instrs[
                                                                                                :-1]):
                                        pass
                                    elif parent_node.instr.opcode == If and (node not in parent_node.sub_instrs[1:]):
                                        pass
                                    else:
                                        parent_instr = random.choice(I64_to_V128['instrs'])
                                        subs_parent_node = Node(Instruction(parent_instr, None),
                                                                instr_type={'params': [ValTypeI64],
                                                                            'results': [ValTypeV128]})
                                        if parent_node == None:
                                            parent_node = subs_parent_node
                                            root = parent_node
                                        else:
                                            index = parent_node.sub_instrs.index(node)
                                            parent_node.sub_instrs[index] = subs_parent_node
                                        subs_parent_node.sub_instrs.append(node)

                                        visited.add(subs_parent_node)
                            elif subs_instr in V128_to_F32['instrs']:
                                subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                                 instr_type={'params': [ValTypeV128], 'results': [ValTypeF32]})
                                subs_node.sub_instrs = node.sub_instrs
                                node.copy(subs_node)
                                if parent_node not in visited or parent_node == None or (
                                        parent_node in visited and parent_node.instr.opcode in [Call, CallIndirect, If,
                                                                                                Block]):
                                    if parent_node.instr.opcode == CallIndirect and (
                                            len(parent_node.type["params"]) == 1 or node not in parent_node.sub_instrs[
                                                                                                :-1]):
                                        pass
                                    elif parent_node.instr.opcode == If and (node not in parent_node.sub_instrs[1:]):
                                        pass
                                    else:
                                        parent_instr = random.choice(F32_to_V128['instrs'])
                                        subs_parent_node = Node(Instruction(parent_instr, None),
                                                                instr_type={'params': [ValTypeF32],
                                                                            'results': [ValTypeV128]})
                                        if parent_node == None:
                                            parent_node = subs_parent_node
                                            root = parent_node
                                        else:
                                            index = parent_node.sub_instrs.index(node)
                                            parent_node.sub_instrs[index] = subs_parent_node
                                        subs_parent_node.sub_instrs.append(node)

                                        visited.add(subs_parent_node)
                            elif subs_instr in V128_to_F64['instrs']:
                                subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                                 instr_type={'params': [ValTypeV128], 'results': [ValTypeF64]})
                                subs_node.sub_instrs = node.sub_instrs
                                node.copy(subs_node)
                                if parent_node not in visited or parent_node == None or (
                                        parent_node in visited and parent_node.instr.opcode in [Call, CallIndirect, If,
                                                                                                Block]):
                                    if parent_node.instr.opcode == CallIndirect and (
                                            len(parent_node.type["params"]) == 1 or node not in parent_node.sub_instrs[
                                                                                                :-1]):
                                        pass
                                    elif parent_node.instr.opcode == If and (node not in parent_node.sub_instrs[1:]):
                                        pass
                                    else:
                                        parent_instr = random.choice(F64_to_V128['instrs'])
                                        subs_parent_node = Node(Instruction(parent_instr, None),
                                                                instr_type={'params': [ValTypeF64],
                                                                            'results': [ValTypeV128]})
                                        if parent_node == None:
                                            parent_node = subs_parent_node
                                            root = parent_node
                                        else:
                                            index = parent_node.sub_instrs.index(node)
                                            parent_node.sub_instrs[index] = subs_parent_node
                                        subs_parent_node.sub_instrs.append(node)

                                        visited.add(subs_parent_node)
                        else:
                            if subs_instr in V128_to_I32['instrs']:
                                target_type = ValTypeI32
                                parent_instr = random.choice(I32_to_V128['instrs'])
                            elif subs_instr in V128_to_I64['instrs']:
                                target_type = ValTypeI64
                                parent_instr = random.choice(I64_to_V128['instrs'])
                            elif subs_instr in V128_to_F32['instrs']:
                                target_type = ValTypeF32
                                parent_instr = random.choice(F32_to_V128['instrs'])
                            elif subs_instr in V128_to_F64['instrs']:
                                target_type = ValTypeF64
                                parent_instr = random.choice(F64_to_V128['instrs'])
                            else:
                                print(opnames[subs_instr] + "throw the trap")
                                pass

                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeV128], 'results': [target_type]})
                            subs_node.sub_instrs = node.sub_instrs
                            node.copy(subs_node)
                            if parent_node not in visited or parent_node == None or (
                                    parent_node in visited and parent_node.instr.opcode in [Call, CallIndirect, If,
                                                                                            Block]):
                                if parent_node.instr.opcode == CallIndirect and (
                                        len(parent_node.type["params"]) == 1 or node not in parent_node.sub_instrs[
                                                                                            :-1]):
                                    pass
                                elif parent_node.instr.opcode == If and (node not in parent_node.sub_instrs[1:]):
                                    pass
                                else:
                                    if opnames[parent_instr].find("load") == -1:
                                        subs_parent_node = Node(
                                            Instruction(parent_instr),
                                            instr_type={'params': [target_type], 'results': [ValTypeV128]})
                                    else:
                                        subs_parent_node = Node(
                                            Instruction(parent_instr, MemArg(align=0, offset=random.randint(0, 10000))),
                                            instr_type={'params': [target_type], 'results': [ValTypeV128]},
                                            context=Context(memory={"min": 10, "max": 32768}))
                                    if parent_node == None:
                                        parent_node = subs_parent_node
                                        root = parent_node
                                    else:
                                        index = parent_node.sub_instrs.index(node)
                                        parent_node.sub_instrs[index] = subs_parent_node
                                    subs_parent_node.sub_instrs.append(node)

                                    visited.add(subs_parent_node)
                    elif subs_instr in V128_to_V128['instrs']:
                        subs_node = Node(Instruction(subs_instr, None),
                                         instr_type={'params': [ValTypeV128], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        node.copy(subs_node)

                elif len(instr_type['params']) == 2 and len(instr_type['results']) == 0:
                    instrs_2_to_0 = I32_V128_to_['instrs']
                    subs_instr = random.choice(instrs_2_to_0)
                    if subs_instr == V128Store:
                        # memarg
                        subs_node = Node(Instruction(subs_instr, MemArg(align=0, offset=random.randint(0, 10000))),
                                         instr_type={'params': [ValTypeI32, ValTypeV128], 'results': []},
                                         context=Context(memory={"min": 10, "max": 32768}))
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-2] = Node(Instruction(I32Const, random.randint(0, 10000)),
                                                        instr_type={'params': [], 'results': [ValTypeI32]})
                        node.copy(subs_node)
                    else:
                        # memarg lane
                        subs_node = Node(Instruction(subs_instr,
                                                     MemLaneArg(MemArg(align=0, offset=random.randint(0, 10000)),
                                                                random.randint(0, 1))),
                                         instr_type={'params': [ValTypeI32, ValTypeV128], 'results': []},
                                         context=Context(memory={"min": 10, "max": 32768}))
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-2] = Node(Instruction(I32Const, random.randint(0, 10000)),
                                                        instr_type={'params': [], 'results': [ValTypeI32]})
                        node.copy(subs_node)

                elif len(instr_type['params']) == 2 and len(instr_type['results']) == 1:
                    instrs_2_to_1 = V128_V128_to_V128['instrs'] + V128_I32_to_V128['instrs'] + V128_I64_to_V128[
                        'instrs'] + V128_F32_to_V128['instrs'] + V128_F64_to_V128['instrs'] + I32_V128_to_V128['instrs']
                    subs_instr = random.choice(instrs_2_to_1)
                    if subs_instr == I8x16Shuffle:
                        # lane16
                        lane16_args = b''.join(bytes([random.randint(0, 15)]) for _ in range(16))
                        subs_node = Node(Instruction(subs_instr, int.from_bytes(lane16_args, byteorder='little')),
                                         instr_type={'params': [ValTypeI32, ValTypeV128], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        node.copy(subs_node)
                    elif subs_instr in I32_V128_to_V128['instrs']:
                        # memarg lane
                        subs_node = Node(Instruction(subs_instr,
                                                     MemLaneArg(MemArg(align=0, offset=random.randint(0, 10000)),
                                                                random.randint(0, 1))),
                                         instr_type={'params': [ValTypeI32, ValTypeV128], 'results': [ValTypeV128]},
                                         context=Context(memory={"min": 10, "max": 32768}))
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-2] = Node(Instruction(I32Const, random.randint(0, 10000)),
                                                        instr_type={'params': [], 'results': [ValTypeI32]})
                        node.copy(subs_node)
                    elif subs_instr in V128_I32_to_V128['instrs']:
                        if opnames[subs_instr].find("lane") != -1:
                            subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                             instr_type={'params': [ValTypeV128, ValTypeI32], 'results': [ValTypeV128]})
                        else:
                            subs_node = Node(Instruction(subs_instr, None),
                                             instr_type={'params': [ValTypeV128, ValTypeI32], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-1] = Node(Instruction(I32Const, random.randint(0, 10000)),
                                                        instr_type={'params': [], 'results': [ValTypeI32]})
                        node.copy(subs_node)
                    elif subs_instr in V128_I64_to_V128['instrs']:
                        subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                         instr_type={'params': [ValTypeV128, ValTypeI64], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-1] = Node(Instruction(I64Const, random.randint(0, 10000)),
                                                        instr_type={'params': [], 'results': [ValTypeI64]})
                        node.copy(subs_node)
                    elif subs_instr in V128_F32_to_V128['instrs']:
                        subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                         instr_type={'params': [ValTypeV128, ValTypeF32], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-1] = Node(Instruction(F32Const, numpy.float32(numpy.random.random())),
                                                        instr_type={'params': [], 'results': [ValTypeF32]})
                        node.copy(subs_node)
                    elif subs_instr in V128_F64_to_V128['instrs']:
                        subs_node = Node(Instruction(subs_instr, random.randint(0, 1)),
                                         instr_type={'params': [ValTypeV128, ValTypeF64], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        subs_node.sub_instrs[-1] = Node(Instruction(F64Const, numpy.float64(numpy.random.random())),
                                                        instr_type={'params': [], 'results': [ValTypeF64]})
                        node.copy(subs_node)

                    else:
                        # no args and [v128, v128] -> [v128]
                        subs_node = Node(Instruction(subs_instr),
                                         instr_type={'params': [ValTypeV128, ValTypeV128], 'results': [ValTypeV128]})
                        subs_node.sub_instrs = node.sub_instrs
                        node.copy(subs_node)
            elif node.instr.opcode == Select:
                node.sub_instrs.append(Node(Instruction(Drop, None),
                                            instr_type={'params': [ValTypeAny], 'results': []}))
                node.sub_instrs.append(Node(Instruction(I32Const, random.randint(0, 1)),
                                            instr_type={'params': [], 'results': [ValTypeI32]}))

            elif node.instr.opcode == Call:
                node.context.functype["result_types"] = [ValTypeV128] * len(node.context.functype["result_types"])
                node.type["results"] = [ValTypeV128] * len(node.type["results"])

            elif node.instr.opcode in [LocalGet, LocalSet, LocalTee]:
                node.context.local_variable = {"local_variable_type": ValTypeV128}
                if node.instr.opcode == LocalSet:
                    node.type["params"] = [ValTypeV128]
                elif node.instr.opcode == LocalTee:
                    node.type["params"] = [ValTypeV128]
                    node.type["results"] = [ValTypeV128]
                else:
                    node.type["results"] = [ValTypeV128]
            elif node.instr.opcode in [GlobalSet, GlobalGet]:
                node.context.global_variable = {"global_variable_type": ValTypeV128}
                if node.instr.opcode == GlobalSet:
                    node.type["params"] = [ValTypeV128]
                else:
                    node.type["results"] = [ValTypeV128]
    return root


def instr_substitute(root):
    stack = [(root, None)]  # Stack to keep track of nodes and their parents
    visited = set()  # Set to keep track of visited nodes

    while stack:
        node, parent_node = stack[-1]  # Peek at the top of the stack

        # If node has unvisited children, push them onto the stack
        if node.sub_instrs and all(child in visited for child in node.sub_instrs) is False:
            for child in reversed(node.sub_instrs):
                if child not in visited:
                    stack.append((child, node))
        elif node in visited:
            stack.pop()
        else:
            node, parent_node = stack.pop()
            visited.add(node)  # Mark node as visited

            if parent_node != None and parent_node.instr.opcode in [If, Block, Loop, BrTable, BrIf,
                                                                    Call, CallIndirect] and parent_node not in visited:
                pass
            if node.instr.opcode not in [Block, Loop, Else_, If, End_, LocalSet, LocalGet, LocalTee, Call, CallIndirect,
                                         Br, BrIf, BrTable, GlobalSet, GlobalGet, Select]:
                instr_type = node.type

                substitute_instr = get_substitute_instrs(instr_type['params'], instr_type['results'])
                if substitute_instr != None:

                    subs_instr_name = opnames[substitute_instr]
                    if (subs_instr_name.find("store") != -1 or subs_instr_name.find(
                            "load") != -1) and (
                            substitute_instr <= 0xFD0B or substitute_instr in [V128Load64Zero, V128Load32Zero]):

                        subs_node = Node(
                            Instruction(substitute_instr, MemArg(align=0, offset=random.randint(0, 10000))),
                            instr_type={'params': instr_type['params'], 'results': instr_type['results']},
                            context=Context(memory={"min": 10, "max": 32768}))
                    elif substitute_instr >= 0xFD54 and substitute_instr <= 0xFD5B:
                        subs_node = Node(Instruction(substitute_instr,
                                                     MemLaneArg(MemArg(align=0, offset=random.randint(0, 10000)),
                                                                random.randint(0, 1))),
                                         instr_type={'params': instr_type['params'], 'results': instr_type['results']},
                                         context=Context(memory={"min": 10, "max": 32768}))

                    elif subs_instr_name.find("local") != -1:
                        if instr_type['params'] != []:
                            local_type = instr_type['params'][0]
                        else:
                            local_type = instr_type['results'][0]
                        subs_node = Node(Instruction(substitute_instr, 0),
                                         instr_type={'params': instr_type['params'],
                                                     'results': instr_type['results']},
                                         context=Context(local_variable={"local_variable_type": local_type}))
                    elif subs_instr_name.find("global") != -1:
                        if instr_type['params'] != []:
                            global_type = instr_type['params'][0]
                        else:
                            global_type = instr_type['results'][0]
                        subs_node = Node(Instruction(substitute_instr, 0),
                                         instr_type={'params': instr_type['params'],
                                                     'results': instr_type['results']},
                                         context=Context(global_variable={"global_variable_type": global_type}))
                    elif subs_instr_name.find("table") != -1:
                        subs_node = node
                    elif subs_instr_name.find("select") != -1:
                        subs_node = node
                    elif subs_instr_name.find("const") != -1:
                        const_type = instr_type['results'][0]
                        subs_node = Node(Instruction(substitute_instr, generate_random_number(const_type)),
                                         instr_type={'params': instr_type['params'],
                                                     'results': instr_type['results']})
                    elif substitute_instr >= 0xFD08 and substitute_instr <= 0xFC11:
                        subs_node = Node(Instruction(substitute_instr,
                                                     MemLaneArg(MemArg(align=0, offset=random.randint(0, 10000)),
                                                                random.randint(0, 1))),
                                         instr_type={'params': [ValTypeI32, ValTypeV128], 'results': []},
                                         context=Context(memory={"min": 10, "max": 32768}))
                    elif subs_instr_name.find("lane") != -1:
                        subs_node = Node(Instruction(substitute_instr, random.randint(0, 1)),
                                         instr_type={'params': instr_type['params'],
                                                     'results': instr_type['results']})
                    else:
                        subs_node = Node(Instruction(substitute_instr, None),
                                         instr_type={'params': instr_type['params'], 'results': instr_type['results']})
                    subs_node.sub_instrs = node.sub_instrs
                    node.copy(subs_node)

            elif node.instr.opcode == Select:
                pass
            elif node.instr.opcode == Call:
                pass
            elif node.instr.opcode in [LocalGet, LocalSet, LocalTee]:
                pass
            elif node.instr.opcode in [GlobalSet, GlobalGet]:
                pass
    return root


def global_mutation(module):
    global_sec = module.global_sec
    if global_sec == []:
        return
    global_item = random.choice(global_sec)
    global_item.type.mut = 1


def import_export_mutation(module):
    num = random.randint(1, 10)
    for i in range(num):
        export_type = random.randint(0, 3)
        if export_type == 0:
            item_idx = random.randint(0, len(module.func_sec) - 1)
        elif export_type == 1:
            if len(module.table_sec) != 0:
                item_idx = random.randint(0, len(module.table_sec) - 1)
            else:
                continue
        elif export_type == 2:
            if len(module.mem_sec) != 0:
                item_idx = random.randint(0, len(module.mem_sec) - 1)
            else:
                continue
        elif export_type == 3:
            if len(module.global_sec) != 0:
                item_idx = random.randint(0, len(module.global_sec) - 1)
            else:
                continue

        export_item = Export(''.join(random.choices(string.ascii_letters + string.digits, k=5)),
                             ExportDesc(export_type, item_idx))

        module.export_sec.append(export_item)


def memory_mutation(module):
    memory_sec = module.mem_sec
    if memory_sec == []:
        return
    memory_item = random.choice(memory_sec)
    memory_item.min = generate_random_number(ValTypeI32)
    memory_item.max = memory_item.min + generate_random_number(ValTypeI32)


def function_mutation(module):
    table_sec = module.table_sec
    if table_sec == []:
        return
    table_item = random.choice(table_sec)
    table_item.min = generate_random_number(ValTypeI32)
    table_item.max = table_item.min + generate_random_number(ValTypeI32)


def module_mutation(module):
    mutation_type = random.randint(0, 4)
    if mutation_type == 0:
        global_mutation(module)
    elif mutation_type == 1:
        import_export_mutation(module)
    elif mutation_type == 2:
        memory_mutation(module)
    elif mutation_type == 3:
        function_mutation(module)
    elif mutation_type == 4:
        pass
