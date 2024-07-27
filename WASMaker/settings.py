## Settings

# Mongodb config
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_CLIENT = 'runtime-fuzz'

# Benchmark config
BENCHMARK_PATH = '../benchmark'

# Fuzzing time
FUZZING_TIME = 86400

# Output path
OUTPUT_PATH = 'runtime_outputs.txt'

# the number of ASTs in a function
AST_NUM = 10

# Log config
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
