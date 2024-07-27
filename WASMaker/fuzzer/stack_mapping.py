from WASMaker.fuzzer.instructions import *
from WASMaker.parser.opnames import *

"""
Classification of WASM instructions based on their stack operations using formatted constant names.
"""

_to_ = {'stack_type': [[], []],
        'instrs': [Block, Loop, Else_, Call, CallIndirect, LocalGet, LocalSet, LocalTee, GlobalGet, GlobalSet, DataDrop,
                   ElemDrop]}

I32_to_ = {'stack_type': [[ValTypeI32], []], 'instrs': [If]}

I32_to_I32 = {'stack_type': [[ValTypeI32], [ValTypeI32]],
              'instrs': [I32Load, I32Load8S, I32Load8U, I32Load16S, I32Load16U, I32Eqz, I32Clz, I32Ctz, I32PopCnt,
                         I32Extend8S,
                         I32Extend16S, TableGrow, I32Load8S, I32Load8U, I32Load16S, I32Load16U, I32Extend8S,
                         I32Extend16S]}

I32_to_I64 = {'stack_type': [[ValTypeI32], [ValTypeI64]],
              'instrs': [I64Load, I64Load8S, I64Load8U, I64Load16S, I64Load16U, I64Load32S, I64Load32U, I64ExtendI32S,
                         I64ExtendI32U, I64Extend8S, I64Extend16S, I64Extend32S, I64Load8S, I64Load8U, I64Load16S,
                         I64Load16U,
                         I64Load32S, I64Load32U]}

I32_to_F32 = {'stack_type': [[ValTypeI32], [ValTypeF32]],
              'instrs': [F32Load, F32ConvertI32S, F32ConvertI32U, F32ReinterpretI32]}

I32_to_F64 = {'stack_type': [[ValTypeI32], [ValTypeF64]], 'instrs': [F64Load, F64ConvertI32S, F64ConvertI32U]}

I32_I32_to_ = {'stack_type': [[ValTypeI32, ValTypeI32], []],
               'instrs': [I32Store, I32Store8, I32Store16, TableFill, I32Store8, I32Store16]}

I32_I64_to_ = {'stack_type': [[ValTypeI32, ValTypeI64], []],
               'instrs': [I64Store, I64Store8, I64Store16, I64Store32, I64Store8, I64Store16, I64Store32]}

I32_F32_to_ = {'stack_type': [[ValTypeI32, ValTypeF32], []], 'instrs': [F32Store]}

I32_F64_to_ = {'stack_type': [[ValTypeI32, ValTypeF64], []], 'instrs': [F64Store]}

Any_to_ = {'stack_type': [[ValTypeAny], []], 'instrs': [Drop]}

Any_Any_I32_to_Any = {'stack_type': [[ValTypeAny, ValTypeAny, ValTypeI32], [ValTypeAny]], 'instrs': [Select, SelectT]}

_to_I32 = {'stack_type': [[], [ValTypeI32]], 'instrs': [I32Const, TableSize]}

_to_I64 = {'stack_type': [[], [ValTypeI64]], 'instrs': [I64Const]}

_to_F32 = {'stack_type': [[], [ValTypeF32]], 'instrs': [F32Const]}

_to_F64 = {'stack_type': [[], [ValTypeF64]], 'instrs': [F64Const]}

I32_I32_to_I32 = {'stack_type': [[ValTypeI32, ValTypeI32], [ValTypeI32]],
                  'instrs': [I32Eq, I32Ne, I32LtS, I32LtU, I32GtS, I32GtU, I32LeS, I32LeU, I32GeS, I32GeU, I32Add,
                             I32Sub, I32Mul,
                             I32DivS, I32DivU, I32RemS, I32RemU, I32And, I32Or, I32Xor, I32Shl, I32ShrS, I32ShrU,
                             I32Rotl, I32Rotr]}

I64_to_I32 = {'stack_type': [[ValTypeI64], [ValTypeI32]], 'instrs': [I64Eqz, I32WrapI64]}

I64_I64_to_I32 = {'stack_type': [[ValTypeI64, ValTypeI64], [ValTypeI32]],
                  'instrs': [I64Eq, I64Ne, I64LtS, I64LtU, I64GtS, I64GtU, I64LeS, I64LeU, I64GeS, I64GeU]}

F32_F32_to_I32 = {'stack_type': [[ValTypeF32, ValTypeF32], [ValTypeI32]],
                  'instrs': [F32Eq, F32Ne, F32Lt, F32Gt, F32Le, F32Ge]}

F64_F64_to_I32 = {'stack_type': [[ValTypeF64, ValTypeF64], [ValTypeI32]],
                  'instrs': [F64Eq, F64Ne, F64Lt, F64Gt, F64Le, F64Ge]}

I64_to_I64 = {'stack_type': [[ValTypeI64], [ValTypeI64]],
              'instrs': [I64Clz, I64Ctz, I64PopCnt, I64Extend8S, I64Extend16S, I64Extend32S]}

I64_I64_to_I64 = {'stack_type': [[ValTypeI64, ValTypeI64], [ValTypeI64]],
                  'instrs': [I64Add, I64Sub, I64Mul, I64DivS, I64DivU, I64RemS, I64RemU, I64And, I64Or, I64Xor, I64Shl,
                             I64ShrS,
                             I64ShrU, I64Rotl, I64Rotr]}

F32_to_F32 = {'stack_type': [[ValTypeF32], [ValTypeF32]],
              'instrs': [F32Abs, F32Neg, F32Ceil, F32Floor, F32Trunc, F32Nearest, F32Sqrt]}

F32_F32_to_F32 = {'stack_type': [[ValTypeF32, ValTypeF32], [ValTypeF32]],
                  'instrs': [F32Add, F32Sub, F32Mul, F32Div, F32Min, F32Max, F32CopySign, F32CopySign]}

F64_to_F64 = {'stack_type': [[ValTypeF64], [ValTypeF64]],
              'instrs': [F64Abs, F64Neg, F64Ceil, F64Floor, F64Trunc, F64Nearest, F64Sqrt]}

F64_F64_to_F64 = {'stack_type': [[ValTypeF64, ValTypeF64], [ValTypeF64]],
                  'instrs': [F64Add, F64Sub, F64Mul, F64Div, F64Min, F64Max, F64CopySign, F64CopySign]}

F32_to_I32 = {'stack_type': [[ValTypeF32], [ValTypeI32]],
              'instrs': [I32TruncF32S, I32TruncF32U, I32ReinterpretF32, I32TruncSatF32S, I32TruncSatF32U]}

F64_to_I32 = {'stack_type': [[ValTypeF64], [ValTypeI32]],
              'instrs': [I32TruncF64S, I32TruncF64U, I32TruncSatF64S, I32TruncSatF64U]}

F32_to_I64 = {'stack_type': [[ValTypeF32], [ValTypeI64]],
              'instrs': [I64TruncF32S, I64TruncF32U, I64TruncSatF32S, I64TruncSatF32U]}

F64_to_I64 = {'stack_type': [[ValTypeF64], [ValTypeI64]],
              'instrs': [I64TruncF64S, I64TruncF64U, I64ReinterpretF64, I64TruncSatF64S, I64TruncSatF64U]}

I64_to_F32 = {'stack_type': [[ValTypeI64], [ValTypeF32]], 'instrs': [F32ConvertI64S, F32ConvertI64U]}

F64_to_F32 = {'stack_type': [[ValTypeF64], [ValTypeF32]], 'instrs': [F32DemoteF64]}

I64_to_F64 = {'stack_type': [[ValTypeI64], [ValTypeF64]], 'instrs': [F64ConvertI64S, F64ConvertI64U, F64ReinterpretI64]}

F32_to_F64 = {'stack_type': [[ValTypeF32], [ValTypeF64]], 'instrs': [F64PromoteF32]}

I32_I32_I32_to_ = {'stack_type': [[ValTypeI32, ValTypeI32, ValTypeI32], []],
                   'instrs': [MemoryInit, MemoryCopy, MemoryFill, TableInit, TableCopy]}

I32_to_Any = {'stack_type': [[ValTypeI32], [ValTypeAny]], 'instrs': [TableGet]}

I32_Any_to_ = {'stack_type': [[ValTypeI32, ValTypeAny], []], 'instrs': [TableSet]}

_to_Any = {'stack_type': [[], [ValTypeAny]], 'instrs': [RefNull]}

Any_to_I32 = {'stack_type': [[ValTypeAny], [ValTypeI32]], 'instrs': [RefIsNull]}
# zero给看看，这些的参数都是memarg
I32_to_V128 = {'stack_type': [[ValTypeI32], [ValTypeV128]],
               'instrs': [V128Load, V128Load8x8S, V128Load8x8U, V128Load16x4S, V128Load16x4U, V128Load32x2S,
                          V128Load32x2U,
                          V128Load8Splat, V128Load16Splat, V128Load32Splat, V128Load64Splat, I8x16Splat, I16x8Splat,
                          I32x4Splat,
                          V128Load32Zero, V128Load64Zero]}

I32_V128_to_ = {'stack_type': [[ValTypeI32, ValTypeV128], []],
                'instrs': [V128Store, V128Store8Lane, V128Store16Lane, V128Store32Lane, V128Store64Lane]}

_to_V128 = {'stack_type': [[], [ValTypeV128]], 'instrs': [V128Const]}
# shuffle lane16
V128_V128_to_V128 = {'stack_type': [[ValTypeV128, ValTypeV128], [ValTypeV128]],
                     'instrs': [I8x16Shuffle, I8x16Swizzle, I8x16Eq, I8x16Ne, I8x16LtS, I8x16LtU, I8x16GtS, I8x16GtU,
                                I8x16LeS,
                                I8x16LeU, I8x16GeS, I8x16GeU, I16x8Eq, I16x8Ne, I16x8LtS, I16x8LtU, I16x8GtS, I16x8GtU,
                                I16x8LeS,
                                I16x8LeU, I16x8GeS, I16x8GeU, I32x4Eq, I32x4Ne, I32x4LtS, I32x4LtU, I32x4GtS, I32x4GtU,
                                I32x4LeS,
                                I32x4LeU, I32x4GeS, I32x4GeU, F32x4Eq, F32x4Ne, F32x4Lt, F32x4Gt, F32x4Le, F32x4Ge,
                                F64x2Eq,
                                F64x2Ne, F64x2Lt, F64x2Gt, F64x2Le, F64x2Ge, V128And, V128AndNot, V128Or, V128Xor,
                                I8x16NarrowI16x8S, I8x16NarrowI16x8U, I8x16Add, I8x16AddSatS, I8x16AddSatU, I8x16Sub,
                                I8x16SubSatS,
                                I8x16SubSatU, I8x16MinS, I8x16MinU, I8x16MaxS, I8x16MaxU, I8x16AvgrU, I16x8Q15mulrSatS,
                                I16x8NarrowI32x4S, I16x8NarrowI32x4U, I16x8Add, I16x8AddSatS, I16x8AddSatU, I16x8Sub,
                                I16x8SubSatS,
                                I16x8SubSatU, I16x8Mul, I16x8MinS, I16x8MinU, I16x8MaxS, I16x8MaxU, I16x8AvgrU,
                                I16x8ExtmulLowI8x16S, I16x8ExtmulHighI8x16S, I16x8ExtmulLowI8x16U,
                                I16x8ExtmulHighI8x16U, I32x4Add,
                                I32x4Sub, I32x4Mul, I32x4MinS, I32x4MinU, I32x4MaxS, I32x4MaxU, I32x4DotI16x8S,
                                I32x4ExtmulLowI16x8S, I32x4ExtmulHighI16x8S, I32x4ExtmulLowI16x8U,
                                I32x4ExtmulHighI16x8U, I64x2Add,
                                I64x2Sub, I64x2Mul, I64x2Eq, I64x2Ne, I64x2LtS, I64x2GtS, I64x2LeS, I64x2GeS,
                                I64x2ExtmulLowI32x4S,
                                I64x2ExtmulHighI32x4S, I64x2ExtmulLowI32x4U, I64x2ExtmulHighI32x4U, F32x4Add, F32x4Sub,
                                F32x4Mul,
                                F32x4Div, F32x4Min, F32x4Max, F32x4Pmin, F32x4Pmax, F64x2Add, F64x2Sub, F64x2Mul,
                                F64x2Div,
                                F64x2Min, F64x2Max, F64x2Pmin, F64x2Pmax]}

I64_to_V128 = {'stack_type': [[ValTypeI64], [ValTypeV128]], 'instrs': [I64x2Splat]}

F32_to_V128 = {'stack_type': [[ValTypeF32], [ValTypeV128]], 'instrs': [F32x4Splat]}

F64_to_V128 = {'stack_type': [[ValTypeF64], [ValTypeV128]], 'instrs': [F64x2Splat]}

V128_to_I32 = {'stack_type': [[ValTypeV128], [ValTypeI32]],
               'instrs': [I8x16ExtractLaneS, I8x16ExtractLaneU, I16x8ExtractLaneS, I16x8ExtractLaneU, I32x4ExtractLane,
                          V128AnyTrue, I8x16AllTrue, I8x16Bitmask, I16x8AllTrue, I16x8Bitmask, I32x4AllTrue,
                          I32x4Bitmask,
                          I64x2AllTrue, I64x2Bitmask]}

V128_I32_to_V128 = {'stack_type': [[ValTypeV128, ValTypeI32], [ValTypeV128]],
                    'instrs': [I8x16ReplaceLane, I16x8ReplaceLane, I32x4ReplaceLane, I8x16Shl, I8x16ShrS, I8x16ShrU,
                               I16x8Shl,
                               I16x8ShrS, I16x8ShrU, I32x4Shl, I32x4ShrS, I32x4ShrU, I64x2Shl, I64x2ShrS, I64x2ShrU]}
V128_to_I64 = {'stack_type': [[ValTypeV128], [ValTypeI64]], 'instrs': [I64x2ExtractLane]}

V128_I64_to_V128 = {'stack_type': [[ValTypeV128, ValTypeI64], [ValTypeV128]], 'instrs': [I64x2ReplaceLane]}

V128_to_F32 = {'stack_type': [[ValTypeV128], [ValTypeF32]], 'instrs': [F32x4ExtractLane]}

V128_F32_to_V128 = {'stack_type': [[ValTypeV128, ValTypeF32], [ValTypeV128]], 'instrs': [F32x4ReplaceLane]}

V128_to_F64 = {'stack_type': [[ValTypeV128], [ValTypeF64]], 'instrs': [F64x2ExtractLane]}

V128_F64_to_V128 = {'stack_type': [[ValTypeV128, ValTypeF64], [ValTypeV128]], 'instrs': [F64x2ReplaceLane]}

V128_to_V128 = {'stack_type': [[ValTypeV128], [ValTypeV128]],
                'instrs': [V128Not, F32x4DemoteF64x2Zero, F64x2PromoteLowF32x4, I8x16Abs, I8x16Neg, I8x16Popcnt,
                           F32x4Ceil,
                           F32x4Floor, F32x4Trunc, F32x4Nearest, F64x2Ceil, F64x2Floor, F64x2Trunc,
                           I16x8ExtaddPairwiseI8x16S,
                           I16x8ExtaddPairwiseI8x16U, I32x4ExtaddPairwiseI16x8S, I32x4ExtaddPairwiseI16x8U, I16x8Abs,
                           I16x8Neg,
                           I16x8ExtendLowI8x16S, I16x8ExtendHighI8x16S, I16x8ExtendLowI8x16U, I16x8ExtendHighI8x16U,
                           F64x2Nearest,
                           I32x4Abs, I32x4Neg, I32x4ExtendLowI16x8S, I32x4ExtendHighI16x8S, I32x4ExtendLowI16x8U,
                           I32x4ExtendHighI16x8U, I64x2Abs, I64x2Neg, I64x2ExtendLowI32x4S, I64x2ExtendHighI32x4S,
                           I64x2ExtendLowI32x4U, I64x2ExtendHighI32x4U, F32x4Abs, F32x4Neg, F32x4Sqrt, F64x2Abs,
                           F64x2Neg,
                           F64x2Sqrt, I32x4TruncSatF32x4S, I32x4TruncSatF32x4U, F32x4ConvertI32x4S, F32x4ConvertI32x4U,
                           I32x4TruncSatF64x2SZero, I32x4TruncSatF64x2UZero, F64x2ConvertLowI32x4S,
                           F64x2ConvertLowI32x4U]}

V128_V128_V128_to_V128 = {'stack_type': [[ValTypeV128, ValTypeV128, ValTypeV128], [ValTypeV128]], 'instrs': []}

I32_V128_to_V128 = {'stack_type': [[ValTypeI32, ValTypeV128], [ValTypeV128]],
                    'instrs': [V128Load8Lane, V128Load16Lane, V128Load32Lane, V128Load64Lane]}

instrs_list = [_to_, I32_to_, I32_to_I32, I32_to_I64, I32_to_F32, I32_to_F64, I32_I32_to_, I32_I64_to_, I32_F32_to_,
               I32_F64_to_, Any_to_, Any_Any_I32_to_Any, _to_I32, _to_I64, _to_F32, _to_F64, I32_I32_to_I32, I64_to_I32,
               I64_I64_to_I32, F32_F32_to_I32, F64_F64_to_I32, I64_to_I64, I64_I64_to_I64, F32_to_F32, F32_F32_to_F32,
               F64_to_F64, F64_F64_to_F64, F32_to_I32, F64_to_I32, F32_to_I64, F64_to_I64, I64_to_F32, F64_to_F32,
               I64_to_F64, F32_to_F64, I32_I32_I32_to_, I32_to_Any, I32_Any_to_, _to_Any, Any_to_I32, I32_to_V128,
               I32_V128_to_, _to_V128, V128_V128_to_V128, I64_to_V128, F32_to_V128, F64_to_V128, V128_to_I32,
               V128_I32_to_V128, V128_to_I64, V128_I64_to_V128, V128_to_F32, V128_F32_to_V128, V128_to_F64,
               V128_F64_to_V128, V128_to_V128, V128_V128_V128_to_V128, I32_V128_to_V128]

# 1 to 1
# I32_to_V128 + I64_to_V128 + F32_to_V128 + F64_to_V128 + V128_to_I32 + V128_to_I64 + V128_to_F32 + V128_to_F64 + V128_to_V128
# 0 to 1
# _to_V128
# 2 to 0
# I32_V128_to_
# 2 to 1
# V128_V128_to_V128 + V128_I32_to_V128 + V128_I64_to_V128 + V128_F32_to_V128 + V128_F64_to_V128 + I32_V128_to_V128
