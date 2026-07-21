CC ?= clang
CFLAGS := -std=c17 -Wall -Wextra -Wpedantic -g
BUILD := build
EXAMPLES := $(wildcard examples/*.c)
SINGLE_EXAMPLES := $(filter-out examples/calculator.c examples/10_multi_file.c examples/18_mathlib.c,$(EXAMPLES))
EXAMPLE_BINS := $(patsubst examples/%.c,$(BUILD)/examples/%,$(SINGLE_EXAMPLES))
SOLUTION_SOURCES := $(wildcard solutions/*.c)
SOLUTION_BINS := $(patsubst solutions/%.c,$(BUILD)/solutions/%,$(SOLUTION_SOURCES))
EXERCISE_SOURCES := $(wildcard exercises/*.c)
EXERCISE_BINS := $(patsubst exercises/%.c,$(BUILD)/exercises/%,$(EXERCISE_SOURCES))

PROJECT10 := examples/10-multi-file-project
PROJECT21 := examples/21-multi-file-project
PROJECT21_BUILD := $(abspath $(BUILD)/examples/21-multi-file-project)

.PHONY: help examples exercises solutions test project21-test sanitize clean

help:
	@echo "make examples   编译全部示例"
	@echo "make exercises  编译练习起始文件"
	@echo "make solutions  编译参考答案"
	@echo "make test       编译并测试参考答案"
	@echo "make sanitize   使用 ASan/UBSan 运行示例"
	@echo "make clean      删除构建产物"

examples: $(EXAMPLE_BINS) $(BUILD)/examples/10_multi_file $(PROJECT21_BUILD)/tasker

exercises: $(EXERCISE_BINS)

solutions: $(SOLUTION_BINS)

$(BUILD)/examples/%: examples/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

$(BUILD)/examples/10_multi_file: $(PROJECT10)/10_multi_file.c $(PROJECT10)/calculator.c $(PROJECT10)/calculator.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(PROJECT10)/10_multi_file.c $(PROJECT10)/calculator.c -o $@

$(PROJECT21_BUILD)/tasker: $(shell find $(PROJECT21) -type f \( -name '*.c' -o -name '*.h' -o -name Makefile \))
	$(MAKE) -C $(PROJECT21) CC="$(CC)" CFLAGS="$(CFLAGS)" BUILD="$(PROJECT21_BUILD)" all

$(BUILD)/examples/16_threads: examples/16_threads.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -pthread $< -o $@

$(BUILD)/examples/18_shared_libs: examples/18_shared_libs.c examples/18_mathlib.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -shared -fPIC examples/18_mathlib.c -o $(BUILD)/examples/libmathlib.dylib
	$(CC) $(CFLAGS) $< -o $@

$(BUILD)/exercises/11_thread_pool: exercises/11_thread_pool.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -pthread $< -o $@

$(BUILD)/solutions/11_thread_pool: solutions/11_thread_pool.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -pthread $< -o $@

$(BUILD)/exercises/%: exercises/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

$(BUILD)/solutions/%: solutions/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

test: examples solutions project21-test
	bash scripts/test.sh

project21-test:
	$(MAKE) -C $(PROJECT21) CC="$(CC)" CFLAGS="$(CFLAGS)" BUILD="$(PROJECT21_BUILD)" test

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" examples
	bash scripts/run_examples.sh

clean:
	rm -rf $(BUILD)
