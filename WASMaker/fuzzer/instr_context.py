from WASMaker.parser.types import ValTypeF64, ValTypeF32, ValTypeI32, ValTypeI64, ValTypeAny, ValTypeV128


class Context:
    def __init__(self, local_variable=None, functype=None, global_variable=None, memory=None):
        self.local_variable = local_variable
        self.functype = functype
        self.global_variable = global_variable
        self.memory = memory

    def to_json(self):
        if self.local_variable:
            return {'local_variable_type': self.local_variable}
        elif self.functype:
            return {'param_types': self.functype.param_types, 'result_types': self.functype.result_types}
        elif self.global_variable:
            return {'global_variable_type': self.global_variable}
        elif self.memory:
            return {'min': self.memory[0].min, 'max': self.memory[0].max}
        else:
            raise Exception("error")

    def to_object(self, json_dict):
        if 'local_variable_type' in json_dict:

            context = Context(local_variable=json_dict)
        elif 'param_types' in json_dict and 'result_types' in json_dict:
            context = Context(functype=json_dict)
        elif 'global_variable_type' in json_dict:
            context = Context(global_variable=json_dict)
        elif 'min' in json_dict and 'max' in json_dict:
            context = Context(memory=json_dict)
        else:
            raise Exception("error")
        return context


def unreachable(binary, args, inner_func_id):
    stack_type = {'params': [], 'results': []}
    return stack_type, None


def nop(binary, args, inner_func_id):
    stack_type = {'params': [], 'results': []}
    return stack_type, None


def block(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    if args.bt > 0:
        for param_type in binary.module.type_sec[args.bt].param_types:
            instr_params.append(param_type)
        for result_type in binary.module.type_sec[args.bt].result_types:
            instr_results.append(result_type)
    elif args.bt == -1:
        instr_results.append(ValTypeI32)
    elif args.bt == -2:
        instr_results.append(ValTypeI64)
    elif args.bt == -3:
        instr_results.append(ValTypeF32)
    elif args.bt == -4:
        instr_results.append(ValTypeF64)
    elif args.bt == -64:
        pass

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def loop(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    if args.bt > 0:
        for param_type in binary.module.type_sec[args.bt].param_types:
            instr_params.append(param_type)
        for result_type in binary.module.type_sec[args.bt].result_types:
            instr_results.append(result_type)
    elif args.bt == -1:
        instr_results.append(ValTypeI32)
    elif args.bt == -2:
        instr_results.append(ValTypeI64)
    elif args.bt == -3:
        instr_results.append(ValTypeF32)
    elif args.bt == -4:
        instr_results.append(ValTypeF64)
    elif args.bt == -64:
        pass

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def control_if(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = []
    if args.bt > 0:
        for param_type in binary.module.type_sec[args.bt].param_types:
            instr_params.append(param_type)
        for result_type in binary.module.type_sec[args.bt].result_types:
            instr_results.append(result_type)
    elif args.bt == -1:
        instr_results.append(ValTypeI32)
    elif args.bt == -2:
        instr_results.append(ValTypeI64)
    elif args.bt == -3:
        instr_results.append(ValTypeF32)
    elif args.bt == -4:
        instr_results.append(ValTypeF64)
    elif args.bt == -64:
        pass

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def control_else(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def br(binary, args, inner_func_id):
    stack_type = {'params': [], 'results': []}
    return stack_type, None


def br_if(binary, args, inner_func_id):
    stack_type = {'params': [ValTypeI32], 'results': []}
    return stack_type, None


def br_table(binary, args, inner_func_id):
    stack_type = {'params': [ValTypeI32], 'results': []}
    return stack_type, None


def control_return(binary, args, inner_func_id):
    stack_type = {'params': [], 'results': []}
    return stack_type, None


def call(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    functype = None

    import_func_list = binary.get_import_func_list()
    if args <= (binary.get_import_func_num() - 1):
        for param_type in binary.module.type_sec[import_func_list[args].desc.func_type].param_types:
            instr_params.append(param_type)
        for result_type in binary.module.type_sec[import_func_list[args].desc.func_type].result_types:
            instr_results.append(result_type)
        functype = binary.module.type_sec[import_func_list[args].desc.func_type]
    else:
        for param_type in binary.module.type_sec[
            binary.module.func_sec[args - binary.get_import_func_num()]].param_types:
            instr_params.append(param_type)
        for result_type in binary.module.type_sec[
            binary.module.func_sec[args - binary.get_import_func_num()]].result_types:
            instr_results.append(result_type)
        functype = binary.module.type_sec[binary.module.func_sec[args - binary.get_import_func_num()]]

    stack_type = {'params': instr_params, 'results': instr_results}
    context = Context(functype=functype)
    return stack_type, context


def call_indirect(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    functype = None

    for param_type in binary.module.type_sec[args].param_types:
        instr_params.append(param_type)
    for result_type in binary.module.type_sec[args].result_types:
        instr_results.append(result_type)
    instr_params.append(ValTypeI32)

    functype = binary.module.type_sec[args]

    stack_type = {'params': instr_params, 'results': instr_results}
    context = Context(functype=functype)
    return stack_type, context


def memory_size(binary, args, inner_func_id):
    stack_type = {'params': [], 'results': [ValTypeI32]}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)

    context = Context(memory=memory_limit)
    return stack_type, context


def memory_grow(binary, args, inner_func_id):
    stack_type = {'params': [ValTypeI32], 'results': [ValTypeI32]}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_load(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def f32_load(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def f64_load(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_load_8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_load_8_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_load_16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_load_16_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_8_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_16_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_load_32_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_store(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_store(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def f32_store(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeF32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def f64_store(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeF64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_store_8(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i32_store_16(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_store_8(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_store_16(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def i64_store_32(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    memory_limit = binary.module.mem_sec
    if memory_limit == []:
        for import_item in binary.module.import_sec:
            if import_item.desc.mem is not None:
                memory_limit.append(import_item.desc.mem)
    context = Context(memory=memory_limit)
    return stack_type, context


def drop(binary, args, inner_func_id):
    instr_params = [ValTypeAny]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def _select(binary, args, inner_func_id):
    instr_params = [ValTypeAny, ValTypeAny, ValTypeI32]
    instr_results = [ValTypeAny]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def local_get(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    local_variable = None

    func_type = binary.module.type_sec[binary.module.func_sec[inner_func_id]]
    if args in range(len(func_type.param_types)):
        instr_results.append(func_type.param_types[args])
        local_variable = func_type.param_types[args]
    else:
        locals_num = 0
        for item in binary.module.code_sec[inner_func_id].locals:
            locals_num += item.n
            if locals_num >= (args - len(func_type.param_types) + 1):
                instr_results.append(item.type)
                local_variable = item.type
                break
    stack_type = {'params': instr_params, 'results': instr_results}

    context = Context(local_variable=local_variable)
    return stack_type, context


def local_set(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    local_variable = None

    func_type = binary.module.type_sec[binary.module.func_sec[inner_func_id]]
    if args in range(len(func_type.param_types)):
        instr_params.append(func_type.param_types[args])
        local_variable = func_type.param_types[args]
    else:
        locals_num = 0
        for item in binary.module.code_sec[inner_func_id].locals:
            locals_num += item.n
            if locals_num >= (args - len(func_type.param_types) + 1):
                instr_params.append(item.type)
                local_variable = item.type
                break
    stack_type = {'params': instr_params, 'results': instr_results}
    context = Context(local_variable=local_variable)
    return stack_type, context


def local_tee(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    local_variable = None

    func_type = binary.module.type_sec[binary.module.func_sec[inner_func_id]]
    if args in range(len(func_type.param_types)):
        instr_params.append(func_type.param_types[args])
        instr_results.append(func_type.param_types[args])
        local_variable = func_type.param_types[args]
    else:
        locals_num = 0
        for item in binary.module.code_sec[inner_func_id].locals:
            locals_num += item.n
            if locals_num >= (args - len(func_type.param_types) + 1):
                instr_params.append(item.type)
                instr_results.append(item.type)
                local_variable = item.type
                break
    stack_type = {'params': instr_params, 'results': instr_results}
    context = Context(local_variable=local_variable)
    return stack_type, context


def global_get(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    global_variable = None

    import_global_num = -1
    for _, import_item in enumerate(binary.module.import_sec):
        if import_item.desc.global_type != None:
            import_global_num += 1
            if import_global_num == args:
                instr_results.append(import_item.desc.global_type)
                global_variable = import_item.desc.global_type
                break
    for _, global_item in enumerate(binary.module.global_sec):
        import_global_num += 1
        if import_global_num == args:
            instr_results.append(global_item.type.val_type)
            global_variable = global_item.type.val_type
            break
    stack_type = {'params': instr_params, 'results': instr_results}

    context = Context(global_variable=global_variable)
    return stack_type, context


def global_set(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    global_variable = None

    import_global_num = -1
    for _, import_item in enumerate(binary.module.import_sec):
        if import_item.desc.global_type != None:
            import_global_num += 1
            if import_global_num == args:
                instr_params.append(import_item.desc.global_type)
                global_variable = import_item.desc.global_type
                break
    for _, global_item in enumerate(binary.module.global_sec):
        import_global_num += 1
        if import_global_num == args:
            instr_params.append(global_item.type.val_type)
            global_variable = global_item.type.val_type
            break
    stack_type = {'params': instr_params, 'results': instr_results}
    context = Context(global_variable=global_variable)
    return stack_type, context


def i32_const(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_const(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_const(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_const(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_eqz(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_eq(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_ne(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_lt_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_gt_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_le_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_ge_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_eqz(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_eq(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_ne(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_lt_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_gt_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_le_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_ge_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_eq(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_ne(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_lt(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_gt(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_le(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_ge(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_eq(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_ne(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_lt(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_gt(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_le(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_ge(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_clz(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_ctz(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_pop_cnt(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_add(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_sub(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_mul(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_div_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_div_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_rem_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_rem_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_and(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_or(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_xor(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_shl(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_rotl(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_rotr(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_clz(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_ctz(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_pop_cnt(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_add(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_sub(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_mul(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_div_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_div_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_rem_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_rem_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_and(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_or(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_xor(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_shl(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_rotl(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_rotr(binary, args, inner_func_id):
    instr_params = [ValTypeI64, ValTypeI64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_abs(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_neg(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_ceil(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_floor(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_trunc(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_nearest(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_sqrt(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_add(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_sub(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_mul(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_div(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_min(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_max(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_copysign(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_abs(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_neg(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_ceil(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_floor(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_trunc(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_nearest(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_sqrt(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_add(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_sub(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_mul(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_div(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_min(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_max(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_copysign(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_wrap_i64(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_f32_s(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_f32_u(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_f64_s(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_f64_u(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend_i32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend_i32_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_f32_s(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_f32_u(interprefter, args, stack):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_f64_s(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_f64_u(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_convert_i32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_convert_i32_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_convert_i64_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_convert_i64_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_demote_f64(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_convert_i32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_convert_i32_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_convert_i64_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_convert_i64_u(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_promote_f32(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_reinterpret_f32(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_reinterpret_f64(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_reinterpret_i32(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeF32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_reinterpret_i64(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeF64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_extend_8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_extend_16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend_8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend_16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend_32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_sat_f32_s(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_sat_f32_u(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_sat_f64_s(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_trunc_sat_f64_u(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_sat_f32_s(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_sat_f32_u(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_sat_f64_s(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_trunc_sat_f64_u(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeI64]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def memory_init(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def data_drop(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def memory_copy(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def memory_fill(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_init(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def elem_drop(binary, args, inner_func_id):
    instr_params = []
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_copy(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_grow(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_size(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeI32]
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_fill(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []
    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def select_t(binary, args, inner_func_id):
    instr_params = [ValTypeAny, ValTypeAny, ValTypeAny]
    instr_results = [ValTypeAny]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_get(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeAny]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def table_set(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeAny]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_load8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_load8_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_load16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_load16_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load8_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load16_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_load32_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_store8(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_store16(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI32]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_store8(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_store16(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_store32(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeI64]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32_copy_sign(binary, args, inner_func_id):
    instr_params = [ValTypeF32, ValTypeF32]
    instr_results = [ValTypeF32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64_copy_sign(binary, args, inner_func_id):
    instr_params = [ValTypeF64, ValTypeF64]
    instr_results = [ValTypeF64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_extend8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32_extend16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend16_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64_extend32_s(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def ref_null(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeAny]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def ref_is_null(binary, args, inner_func_id):
    instr_params = [ValTypeAny]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def ref_func(binary, args, inner_func_id):
    pass


def v128_load(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load8x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load8x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load16x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load16x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load32x2_s(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load32x2_u(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load8_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load16_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load32_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load64_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_store(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_const(binary, args, inner_func_id):
    instr_params = []
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_shuffle(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_swizzle(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_splat(binary, args, inner_func_id):
    instr_params = [ValTypeI64]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_splat(binary, args, inner_func_id):
    instr_params = [ValTypeF32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_splat(binary, args, inner_func_id):
    instr_params = [ValTypeF64]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_extract_lane_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_extract_lane_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extract_lane_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extract_lane_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extract_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extract_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI64]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_extract_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeF32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeF32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_extract_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeF64]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_replace_lane(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeF64]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_lt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_gt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_le_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_ge_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_lt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_gt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_le_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_ge_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_lt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_gt_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_le_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_ge_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_lt(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_gt(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_le(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_ge(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_lt(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_gt(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_le(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_ge(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_not(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_and(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_and_not(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_or(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_xor(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_bit_select(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_any_true(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load8_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load16_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load32_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load64_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_store8_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_store16_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_store32_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_store64_lane(binary, args, inner_func_id):
    instr_params = [ValTypeI32, ValTypeV128]
    instr_results = []

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load32_zero(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def v128_load64_zero(binary, args, inner_func_id):
    instr_params = [ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_demote_f64x2_zero(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_promote_low_f32x4(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_popcnt(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_all_true(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_bitmask(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_narrow_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_narrow_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_ceil(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_floor(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_trunc(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_nearest(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_shl(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_add_sat_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_add_sat_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_sub_sat_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_sub_sat_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_ceil(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_floor(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_min_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_min_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_max_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_max_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_trunc(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i8x16_avgr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extadd_pairwise_i8x16_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extadd_pairwise_i8x16_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extadd_pairwise_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extadd_pairwise_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_q15mulr_sat_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_all_true(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_bitmask(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_narrow_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_narrow_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extend_low_i8x16_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extend_high_i8x16_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extend_low_i8x16_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extend_high_i8x16_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_shl(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_add_sat_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_add_sat_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_sub_sat_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_sub_sat_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_nearest(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_mul(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_min_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_min_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_max_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_max_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_avgr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extmul_low_i8x16_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extmul_high_i8x16_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extmul_low_i8x16_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i16x8_extmul_high_i8x16_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_all_true(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_bitmask(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extend_low_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extend_high_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extend_low_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extend_high_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_shl(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_mul(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_min_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_min_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_max_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_max_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_dot_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extmul_low_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extmul_high_i16x8_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extmul_low_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_extmul_high_i16x8_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_all_true(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_bitmask(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeI32]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extend_low_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extend_high_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extend_low_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extend_high_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_shl(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_shr_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_shr_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeI32]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_mul(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_eq(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_ne(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_lt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_gt_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_le_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_ge_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extmul_low_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extmul_high_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extmul_low_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i64x2_extmul_high_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_sqrt(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_mul(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_div(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_min(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_max(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_pmin(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_pmax(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_abs(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_neg(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_sqrt(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_add(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_sub(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_mul(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_div(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_min(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_max(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_pmin(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_pmax(binary, args, inner_func_id):
    instr_params = [ValTypeV128, ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_trunc_sat_f32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_trunc_sat_f32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_convert_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f32x4_convert_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_trunc_sat_f64x2_s_zero(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def i32x4_trunc_sat_f64x2_u_zero(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_convert_low_i32x4_s(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None


def f64x2_convert_low_i32x4_u(binary, args, inner_func_id):
    instr_params = [ValTypeV128]
    instr_results = [ValTypeV128]

    stack_type = {'params': instr_params, 'results': instr_results}
    return stack_type, None
