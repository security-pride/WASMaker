import inspect
import random
import struct

import numpy as np

from WASMaker.fuzzer.AST import *
from WASMaker.fuzzer.emit_binary import EmitBinary
from WASMaker.fuzzer.mutator import primitive2simd, module_mutation as module_mutator
from WASMaker.parser.instruction import Instruction, BlockArgs, IfArgs, MemArg, BrTableArgs
from WASMaker.parser.module import Module, Locals, Global, Data, Code, Elem, Export, ExportDesc
from WASMaker.parser.opnames import *
from WASMaker.parser.types import FuncType, FtTag, Limits, GlobalType, TableType
from WASMaker.settings import AST_NUM


def generate_random_number(valtype):
    rand_prob = random.random()
    if valtype == ValTypeI32:
        if rand_prob < 0.7:
            return random.randint(0, 2 ** 31 - 1)
        elif rand_prob < 0.85:
            return 0
        else:
            return 2 ** 31 - 1
    elif valtype == ValTypeI64:
        if rand_prob < 0.7:
            return random.randint(0, 2 ** 63 - 1)
        elif rand_prob < 0.85:
            return 0
        else:
            return 2 ** 63 - 1
    elif valtype == ValTypeF32:
        if rand_prob < 0.7:
            random_float = struct.unpack('f', struct.pack('I', random.randint(0, 2 ** 31 - 1)))[0]
            return random_float
        elif rand_prob < 0.85:
            return 0.0
        else:
            max_float = struct.unpack('f', struct.pack('I', 2 ** 31 - 1))[0]
            return max_float
    elif valtype == ValTypeF64:
        if rand_prob < 0.7:
            random_int64 = random.getrandbits(64)
            random_float = float(random_int64)
            return random_float
        elif rand_prob < 0.85:
            return 0.0
        else:
            max_float = float(2 ** 64 - 1)
            return max_float
    elif valtype == ValTypeV128:
        if rand_prob < 0.7:
            return random.randint(0, 2 ** 128 - 1)
        elif rand_prob < 0.85:
            return 0
        else:
            return 2 ** 128 - 1


def get_stack_depth():
    current_frame = inspect.currentframe()
    stack_depth = 0
    while current_frame.f_back is not None:
        stack_depth += 1
        current_frame = current_frame.f_back
    return stack_depth


def get_avail_ASTs():
    avail_ASTs = []

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    runtime_fuzz_db = myclient["runtime-fuzz"]

    collist = runtime_fuzz_db.list_collection_names()

    for i in range(len(collist)):
        instr_collection = runtime_fuzz_db[collist[i]]
        AST_count = instr_collection.count_documents({})
        if AST_count != 0:
            all_AST_json = list(instr_collection.find())
            avail_ASTs.append(all_AST_json)

    myclient.close()
    return avail_ASTs


def generate_random_string(length):
    random_data = np.random.bytes(length)
    random_string = random_data.decode('utf-8', errors='ignore')

    return random_string


def emit_funcbody(AST_num, module, avail_ASTs, AST_mutation, functype=None):
    local_list = []

    AST_nodes = []

    for i in range(AST_num):

        instr_index = random.randint(0, len(avail_ASTs) - 1)

        instr_collection = avail_ASTs[instr_index]

        AST_count = len(instr_collection)

        if AST_count == 1:
            random_AST_json = instr_collection[0]
        else:
            random_index = random.randint(0, AST_count - 1)
            all_AST_json = instr_collection

            random_AST_json = all_AST_json[random_index]

        random_AST = json_to_ast(random_AST_json)

        if AST_mutation == True:
            random_AST = primitive2simd(random_AST)

        if functype != None:
            emit_node_context(module, local_list, random_AST, avail_ASTs, AST_mutation, functype)
        else:
            emit_node_context(module, local_list, random_AST, avail_ASTs, AST_mutation)
        AST_nodes.append(random_AST)

    funcbody = convert_instrs(AST_nodes)

    results_type = []
    for ast in AST_nodes:
        results_type.extend(ast.type["results"])

    all_local_list = []

    if functype != None:
        for param_type in functype.param_types:
            all_local_list.append(Locals(1, param_type))

    all_local_list = all_local_list + local_list

    if functype != None:
        handle_return(funcbody, functype.result_types, all_local_list)

    return funcbody, local_list, results_type


def handle_return(instrs, results_type, all_local_list):
    i = 0
    while i < len(instrs):

        if instrs[i].opcode in [Block, Loop]:
            args = instrs[i].args
            handle_return(args.instrs, results_type, all_local_list)
        elif instrs[i].opcode == If:
            args = instrs[i].args
            handle_return(args.instrs1, results_type, all_local_list)
            handle_return(args.instrs2, results_type, all_local_list)
        else:
            if instrs[i].opcode == Return:

                for result in results_type:
                    is_exist = False
                    optional_local = []
                    for _, local in enumerate(all_local_list):
                        if result == local.type:
                            optional_local.append(_)
                            is_exist = True
                    if is_exist:
                        instrs.insert(i, Instruction(LocalGet, random.choice(optional_local)))
                    else:
                        if result == ValTypeI32:
                            instrs.insert(i, Instruction(I32Const, generate_random_number(ValTypeI32)))
                        elif result == ValTypeI64:
                            instrs.insert(i, Instruction(I64Const, generate_random_number(ValTypeI64)))
                        elif result == ValTypeF32:
                            instrs.insert(i, Instruction(F32Const, generate_random_number(ValTypeF32)))
                        elif result == ValTypeF64:
                            instrs.insert(i, Instruction(F64Const, generate_random_number(ValTypeF64)))
                        elif result == ValTypeV128:
                            instrs.insert(i, Instruction(V128Const, generate_random_number(ValTypeV128)))
                    i += 1
        i += 1


def convert_instrs(AST_nodes):
    func_instrs = []

    for _, node in enumerate(AST_nodes):
        if node.instr.opcode in [Block, Loop]:
            instr = node.instr

            instr.args = BlockArgs(node.instr.args, convert_instrs(node.sub_instrs))
            func_instrs.append(instr)
            continue
        elif node.instr.opcode == If:
            instr = node.instr

            condition_instrs = convert_instrs([node.sub_instrs.pop(0)])

            end_index = None
            for _, i in enumerate(node.sub_instrs):
                if i.opcode == Else_:
                    end_index = _

            instr.args = IfArgs(node.instr.args, convert_instrs(node.sub_instrs[0: end_index]),
                                convert_instrs(node.sub_instrs[end_index + 1:]))

            func_instrs.extend(condition_instrs)
            func_instrs.append(instr)
            continue
        elif node.instr.opcode == BrTable:
            func_instrs.extend(convert_instrs(node.sub_instrs))

            node.instr = Instruction(BrTable, BrTableArgs(node.instr.args, 0))
            func_instrs.append(node.instr)

        else:
            func_instrs.extend(convert_instrs(node.sub_instrs))

            if node.instr.opcode == Unreachable:
                node.instr.opcode = Nop
            func_instrs.append(node.instr)
    return func_instrs


def json_to_ast(json_ast):
    stack = []
    result = json_to_ast_convert(json_ast)
    stack.append((json_ast, result))

    while stack:
        curr_json_ast, curr_node = stack.pop()

        sub_instrs = curr_json_ast.get('sub_instrs', [])

        for sub_instr_data in sub_instrs:
            sub_instr_node = json_to_ast_convert(sub_instr_data)
            curr_node.sub_instrs.append(sub_instr_node)
            stack.append((sub_instr_data, sub_instr_node))

    return result


def json_to_ast_convert(json_ast):
    instr = Instruction(json_ast.get('instr')['opcode'], json_ast.get('instr')['args'])
    type = json_ast.get('type')
    context = json_ast.get('context')
    if context is not None:
        context = Context().to_object(context)

    node = Node(instr, type, context)
    return node


def emit_node_context(module, local_list, node, avail_ASTs, is_simd, functype=None):
    node_stack = []
    node_stack.append(node)

    while node_stack != []:
        node = node_stack.pop()
        context = node.context

        if context is not None:

            if context.local_variable:

                local_type = context.local_variable['local_variable_type']

                all_local_list = []

                if functype != None:
                    for param_type in functype.param_types:
                        all_local_list.append(Locals(1, param_type))

                all_local_list = all_local_list + local_list

                is_exist = False
                local_id = None

                for _, local in enumerate(all_local_list):
                    if local.type == local_type:
                        is_exist = True
                        local_id = _

                if is_exist == False:
                    local = Locals(1, local_type)
                    local_list.append(local)

                    if functype != None:
                        node.instr.args = len(functype.param_types) + len(local_list) - 1
                    else:
                        node.instr.args = len(local_list) - 1
                else:
                    node.instr.args = local_id


            elif context.functype:

                invoked_functype = FuncType(FtTag, context.functype['param_types'].copy(),
                                            context.functype['result_types'].copy())

                functype_id = None
                for _, type_item in enumerate(module.type_sec):
                    if type_item == invoked_functype:
                        functype_id = _
                if functype_id is None:
                    module.type_sec.append(invoked_functype)
                    functype_id = len(module.type_sec) - 1

                stack_depth = get_stack_depth()

                if stack_depth >= 16:

                    for param in invoked_functype.param_types:
                        if param == ValTypeI32:
                            node.sub_instrs.append(
                                Node(Instruction(Drop), instr_type={'params': [ValTypeI32], 'results': []}))
                        elif param == ValTypeI64:
                            node.sub_instrs.append(
                                Node(Instruction(Drop), instr_type={'params': [ValTypeI64], 'results': []}))
                        elif param == ValTypeF32:
                            node.sub_instrs.append(
                                Node(Instruction(Drop), instr_type={'params': [ValTypeF32], 'results': []}))
                        elif param == ValTypeF64:
                            node.sub_instrs.append(
                                Node(Instruction(Drop), instr_type={'params': [ValTypeF64], 'results': []}))
                        elif param == ValTypeV128:
                            node.sub_instrs.append(
                                Node(Instruction(Drop), instr_type={'params': [ValTypeV128], 'results': []}))

                    if node.instr.opcode == CallIndirect:
                        node.sub_instrs.append(
                            Node(Instruction(Drop), instr_type={'params': [ValTypeI32], 'results': []}))

                    for result in invoked_functype.result_types:
                        if result == ValTypeI32:
                            node.sub_instrs.append(Node(Instruction(I32Const, generate_random_number(ValTypeI32)),
                                                        instr_type={'params': [], 'results': [ValTypeI32]}))
                        elif result == ValTypeI64:
                            node.sub_instrs.append(Node(Instruction(I64Const, generate_random_number(ValTypeI64)),
                                                        instr_type={'params': [], 'results': [ValTypeI64]}))
                        elif result == ValTypeF32:
                            node.sub_instrs.append(Node(Instruction(F32Const, generate_random_number(ValTypeF32)),
                                                        instr_type={'params': [], 'results': [ValTypeF32]}))
                        elif result == ValTypeF64:
                            node.sub_instrs.append(Node(Instruction(F64Const, generate_random_number(ValTypeF64)),
                                                        instr_type={'params': [], 'results': [ValTypeF64]}))
                        elif result == ValTypeV128:
                            node.sub_instrs.append(Node(Instruction(V128Const, generate_random_number(ValTypeV128)),
                                                        instr_type={'params': [], 'results': [ValTypeV128]}))

                    node.instr = Instruction(Nop)
                else:
                    funcbody, func_local_list, results_type = emit_funcbody(random.randint(1, 10), module, avail_ASTs,
                                                                            is_simd, invoked_functype)

                    for _, local in enumerate(func_local_list):
                        if local.type == ValTypeI32:
                            funcbody.insert(0, Instruction(I32Const, generate_random_number(ValTypeI32)))
                            funcbody.insert(1, Instruction(LocalSet, _ + len(invoked_functype.param_types)))
                        elif local.type == ValTypeI64:
                            funcbody.insert(0, Instruction(I64Const, generate_random_number(ValTypeI64)))
                            funcbody.insert(1, Instruction(LocalSet, _ + len(invoked_functype.param_types)))
                        elif local.type == ValTypeF32:
                            funcbody.insert(0, Instruction(F32Const, generate_random_number(ValTypeF32)))
                            funcbody.insert(1, Instruction(LocalSet, _ + len(invoked_functype.param_types)))
                        elif local.type == ValTypeF64:
                            funcbody.insert(0, Instruction(F64Const, generate_random_number(ValTypeF64)))
                            funcbody.insert(1, Instruction(LocalSet, _ + len(invoked_functype.param_types)))
                        elif local.type == ValTypeV128:
                            funcbody.insert(0, Instruction(V128Const, generate_random_number(ValTypeV128)))
                            funcbody.insert(1, Instruction(LocalSet, _ + len(invoked_functype.param_types)))

                    funcbody.extend([Instruction(Drop)] * len(results_type))

                    all_local_list = []

                    for param_type in invoked_functype.param_types:
                        all_local_list.append(Locals(1, param_type))

                    all_local_list = all_local_list + func_local_list

                    for result in invoked_functype.result_types:
                        is_exist = False
                        optional_local = []
                        for _, local in enumerate(all_local_list):
                            if result == local.type:
                                optional_local.append(_)
                                is_exist = True
                        if is_exist:
                            funcbody.append(Instruction(LocalGet, random.choice(optional_local)))
                        else:
                            if result == ValTypeI32:
                                funcbody.append(Instruction(I32Const, generate_random_number(ValTypeI32)))
                            elif result == ValTypeI64:
                                funcbody.append(Instruction(I64Const, generate_random_number(ValTypeI64)))
                            elif result == ValTypeF32:
                                funcbody.append(Instruction(F32Const, generate_random_number(ValTypeF32)))
                            elif result == ValTypeF64:
                                funcbody.append(Instruction(F64Const, generate_random_number(ValTypeF64)))
                            elif result == ValTypeV128:
                                funcbody.append(Instruction(V128Const, generate_random_number(ValTypeV128)))

                    code_item = Code(expr=funcbody, locals_vec=func_local_list)

                    module.func_sec.append(functype_id)

                    module.code_sec.append(code_item)
                    if node.instr.opcode == Call:

                        node.instr.args = len(module.func_sec) - 1
                    else:

                        drop_node = Node(Instruction(Drop), instr_type={'params': [ValTypeI32], 'results': []})

                        node.instr.args = functype_id

                        if module.table_sec == []:

                            module.table_sec.append(TableType(limits=Limits(1, 200, 200)))
                            module.elem_sec.append(
                                Elem(offset_expr=[Instruction(I32Const, 1)], vec_init=[len(module.func_sec) - 1]))
                        else:
                            module.elem_sec[0].init.append(len(module.func_sec) - 1)

                        i32Const_node = Node(Instruction(I32Const, len(module.elem_sec[0].init)),
                                             instr_type={'params': [], 'results': [ValTypeI32]})

                        node.sub_instrs.append(drop_node)
                        node.sub_instrs.append(i32Const_node)
            elif context.global_variable:

                global_variable_type = context.global_variable['global_variable_type']
                is_exist = False

                for _, global_item in enumerate(module.global_sec):
                    if global_item.type.val_type == global_variable_type:
                        node.instr.args = _
                        is_exist = True
                        break
                if is_exist != True:

                    if global_variable_type == ValTypeI32:
                        global_variable_init = [Instruction(I32Const, generate_random_number(ValTypeI32))]
                    elif global_variable_type == ValTypeI64:
                        global_variable_init = [Instruction(I64Const, generate_random_number(ValTypeI64))]
                    elif global_variable_type == ValTypeF32:
                        global_variable_init = [Instruction(F32Const, generate_random_number(ValTypeF32))]
                    elif global_variable_type == ValTypeF64:
                        global_variable_init = [Instruction(F64Const, generate_random_number(ValTypeF64))]
                    elif global_variable_type == ValTypeV128:
                        global_variable_init = [Instruction(V128Const, generate_random_number(ValTypeV128))]
                    global_variable = Global(GlobalType(val_type=global_variable_type, mut=1), global_variable_init)
                    module.global_sec.append(global_variable)
                    node.instr.args = len(module.global_sec) - 1
            elif context.memory:
                if module.mem_sec == []:
                    max = context.memory['max']
                    if max == 0:
                        memory_limit = Limits(1, 65536, 65536)
                        offset_expr = [Instruction(I32Const, random.randint(200, 1000000))]
                        init_data = bytearray(generate_random_string(random.randint(0, 10000)).encode())
                    else:
                        memory_limit = Limits(1, 65536, 65536)
                        offset_expr = [Instruction(I32Const, random.randint(200, 64 * 1024 * max - 1))]

                        init_data = bytearray(generate_random_string(random.randint(0, 10000)).encode())
                    module.mem_sec.append(memory_limit)
                    linear_data = Data(offset_expr=offset_expr, vec_init=init_data)
                    module.data_sec.append(linear_data)
                else:

                    max = module.mem_sec[0].max
                    if max < context.memory['max']:
                        module.mem_sec[0].tag = 1
                        module.mem_sec[0].max = context.memory['max']
                        max = module.mem_sec[0].max
                        offset_expr = [Instruction(I32Const, random.randint(200, 64 * 1024 * max - 1))]

                        init_data = bytearray(generate_random_string(random.randint(0, 10)).encode())
                        linear_data = Data(offset_expr=offset_expr, vec_init=init_data)

                        module.data_sec.append(linear_data)
                if I32Load <= node.instr.opcode <= MemoryGrow:

                    if "8" in opnames[node.instr.opcode]:
                        node.instr.args = MemArg(align=0, offset=random.randint(0, 10000))
                    elif "16" in opnames[node.instr.opcode]:
                        node.instr.args = MemArg(align=random.randint(0, 1), offset=random.randint(0, 10000))
                    else:
                        node.instr.args = MemArg(align=random.randint(0, 2), offset=random.randint(0, 10000))
        node_stack.extend(node.sub_instrs)


def emit_wasm_bianry(file_name, avail_ASTs, AST_mutation, module_mutation):
    module = Module(1836278016, 1)

    AST_num = AST_NUM

    # generate function body for the function main
    funcbody, locals_list, results_type = emit_funcbody(AST_num, module, avail_ASTs, AST_mutation)

    # generate function type for the function main
    functype = FuncType(FtTag, [], results_type)
    module.type_sec.append(functype)
    functype_id = len(module.type_sec) - 1

    funcbody.append(Instruction(Return))

    handle_return(funcbody, functype.result_types, locals_list)

    # generate local variables for the function main
    for _, local in enumerate(locals_list):
        if local.type == ValTypeI32:
            funcbody.insert(0, Instruction(I32Const, generate_random_number(ValTypeI32)))
            funcbody.insert(1, Instruction(LocalSet, _))
        elif local.type == ValTypeI64:
            funcbody.insert(0, Instruction(I64Const, generate_random_number(ValTypeI64)))
            funcbody.insert(1, Instruction(LocalSet, _))
        elif local.type == ValTypeF32:
            funcbody.insert(0, Instruction(F32Const, generate_random_number(ValTypeF32)))
            funcbody.insert(1, Instruction(LocalSet, _))
        elif local.type == ValTypeF64:
            funcbody.insert(0, Instruction(F64Const, generate_random_number(ValTypeF64)))
            funcbody.insert(1, Instruction(LocalSet, _))
        elif local.type == ValTypeV128:
            funcbody.insert(0, Instruction(V128Const, generate_random_number(ValTypeV128)))
            funcbody.insert(1, Instruction(LocalSet, _))

    # generate code item for the function main
    code_item = Code(expr=funcbody, locals_vec=locals_list)
    module.func_sec.append(functype_id)
    module.code_sec.append(code_item)

    # export the function main
    module.export_sec.append(Export("main", ExportDesc(idx=len(module.func_sec) - 1)))

    # module mutation
    if module_mutation:
        module_mutator(module)

    # write the module to the file
    EmitBinary(file_name, module).emit_binary()
