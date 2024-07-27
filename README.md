# WASMaker

WASMaker, a novel differential testing framework that can generate complicated Wasm test cases by disassembling and assembling real-world Wasm binaries, which can trigger hidden inconsistencies among Wasm runtimes.


## Getting Started
In order to generate and store AST, you need to first install [MongoDB](https://www.mongodb.com/docs/manual/installation/) and get Wasm binaries from [WasmBench](https://github.com/sola-st/WasmBench).

The script corpus_preprocess.py parses WasmBench binaries and stores ASTs in MongoDB. For convenience, I have pre-imported the ASTs generated from parsing WasmBench into the Docker container.
And the fuzz.py will generate Wasm binaries and feed them to each Wasm runtime for fuzzing. 

Finally, the output of the runtime is stored in `runtime_outputs.txt`.

1.   set environment

WASMaker should run well on a server with Ubuntu 22.04.
Please download [Docker](https://docs.docker.com/get-docker/) first.
```bash
sudo docker build -t wasmaker .
sudo docker run -it wasmaker # run a docker container
```

2. Start fuzzing the Wasm runtimes(Wasmtime,Wasmer,WAMR,WasmEdge)

```bash
# in the docker container 
cd home/ubuntu/WASMaker/
python3 fuzz.py
```

The outputs of the runtimes are stored in `runtime_outputs.txt`, and the generated binaries are stored in /home/ubuntu/binaries.

The outputs are formatted as follows:
```
==================================================
../binaries/file1.wasm
-----------------wasmtime-----------------
warning: using `--invoke` with a function that returns values is experimental and may break in the future
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493

-----------------wasmer-----------------
timeout 5s
-----------------wamr-----------------
fast jit compilation failed: Error: unsupported opcode
failed to compile fast jit function 0
fast jit compilation failed: Error: unsupported opcode
Exception: failed to compile fast jit function

-----------------wasmedge-----------------
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
29419985997212769685300370766333065493
```


## Detailed Description

### Confirmed Issues
The all binaries of the confirmed issues are stored in `home/ubuntu/binaries/confirmed binaries/`.

- **wasmtime**
[#7558](https://github.com/bytecodealliance/wasmtime/issues/7558)
- **wamr**
[#2450](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2450)
[#2555](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2555)
[#2556](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2556)
[#2557](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2557)
[#2561](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2561)
[#2677](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2677)
[#2690](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2690)
[#2720](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2720)
[#2789](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2789)
[#2861](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2861)
[#2862](https://github.com/bytecodealliance/wasm-micro-runtime/issues/2862)
- **WasmEdge**
[#2812](https://github.com/WasmEdge/WasmEdge/issues/2812)
[#2814](https://github.com/WasmEdge/WasmEdge/issues/2814)
[#2815](https://github.com/WasmEdge/WasmEdge/issues/2815)
[#2988](https://github.com/WasmEdge/WasmEdge/issues/2988)
[#2996](https://github.com/WasmEdge/WasmEdge/issues/2996)
[#2997](https://github.com/WasmEdge/WasmEdge/issues/2997)
[#2999](https://github.com/WasmEdge/WasmEdge/issues/2999)
[#3018](https://github.com/WasmEdge/WasmEdge/issues/3018)
[#3019](https://github.com/WasmEdge/WasmEdge/issues/3019)
[#3057](https://github.com/WasmEdge/WasmEdge/issues/3057)
[#3063](https://github.com/WasmEdge/WasmEdge/issues/3063)
[#3068](https://github.com/WasmEdge/WasmEdge/issues/3068)
[#3076](https://github.com/WasmEdge/WasmEdge/issues/3076)

