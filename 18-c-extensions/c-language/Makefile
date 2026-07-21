CC ?= clang
CFLAGS := -std=c17 -Wall -Wextra -Wpedantic -g
BUILD := build
EXAMPLES := $(wildcard examples/*.c)
SINGLE_EXAMPLES := $(filter-out examples/18_mathlib.c examples/21_http_client.c,$(EXAMPLES))
EXAMPLE_BINS := $(patsubst examples/%.c,$(BUILD)/examples/%,$(SINGLE_EXAMPLES))
SOLUTION_SOURCES := $(wildcard solutions/*.c)
SOLUTION_BINS := $(patsubst solutions/%.c,$(BUILD)/solutions/%,$(SOLUTION_SOURCES))
EXERCISE_SOURCES := $(wildcard exercises/*.c)
EXERCISE_BINS := $(patsubst exercises/%.c,$(BUILD)/exercises/%,$(EXERCISE_SOURCES))

PROJECT10 := examples/10-multi-file-project
CURL_CFLAGS := $(shell curl-config --cflags)
CURL_LIBS := $(shell curl-config --libs)
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
SHARED_LIBRARY := $(BUILD)/examples/libmathlib.dylib
SHARED_FLAGS := -dynamiclib
DL_LIBS :=
else
SHARED_LIBRARY := $(BUILD)/examples/libmathlib.so
SHARED_FLAGS := -shared
DL_LIBS := -ldl
endif
PROJECT10_BUILD := $(abspath $(BUILD)/examples/10-multi-file-project)

.PHONY: help examples exercises solutions test project10-test sanitize clean

help:
	@echo "make examples   编译全部示例"
	@echo "make exercises  编译练习起始文件"
	@echo "make solutions  编译参考答案"
	@echo "make test       编译并测试参考答案"
	@echo "make sanitize   使用 ASan/UBSan 运行示例"
	@echo "make clean      删除构建产物"

examples: $(EXAMPLE_BINS) $(PROJECT10_BUILD)/tasker $(BUILD)/examples/21_http_client

exercises: $(EXERCISE_BINS)

solutions: $(SOLUTION_BINS)

$(BUILD)/examples/%: examples/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

$(PROJECT10_BUILD)/tasker: $(shell find $(PROJECT10) -type f \( -name '*.c' -o -name '*.h' -o -name Makefile \))
	$(MAKE) -C $(PROJECT10) CC="$(CC)" CFLAGS="$(CFLAGS)" BUILD="$(PROJECT10_BUILD)" all

$(BUILD)/examples/21_http_client: examples/21_http_client.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(CURL_CFLAGS) $< $(CURL_LIBS) -o $@

$(BUILD)/examples/16_threads: examples/16_threads.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -pthread $< -o $@

$(BUILD)/examples/18_shared_libs: examples/18_shared_libs.c $(SHARED_LIBRARY)
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< $(DL_LIBS) -o $@

$(SHARED_LIBRARY): examples/18_mathlib.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(SHARED_FLAGS) -fPIC $< -lm -o $@

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

test: examples solutions project10-test
	bash scripts/test.sh

project10-test:
	$(MAKE) -C $(PROJECT10) CC="$(CC)" CFLAGS="$(CFLAGS)" BUILD="$(PROJECT10_BUILD)" test

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" examples
	bash scripts/run_examples.sh

clean:
	rm -rf $(BUILD)
