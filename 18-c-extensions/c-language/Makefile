CC ?= clang
CFLAGS := -std=c17 -Wall -Wextra -Wpedantic -g
BUILD := build
EXAMPLES := $(wildcard examples/*.c)
SINGLE_EXAMPLES := $(filter-out examples/calculator.c examples/10_multi_file.c,$(EXAMPLES))
EXAMPLE_BINS := $(patsubst examples/%.c,$(BUILD)/examples/%,$(SINGLE_EXAMPLES))
SOLUTION_SOURCES := $(wildcard solutions/*.c)
SOLUTION_BINS := $(patsubst solutions/%.c,$(BUILD)/solutions/%,$(SOLUTION_SOURCES))
EXERCISE_SOURCES := $(wildcard exercises/*.c)
EXERCISE_BINS := $(patsubst exercises/%.c,$(BUILD)/exercises/%,$(EXERCISE_SOURCES))

.PHONY: help examples exercises solutions test sanitize clean

help:
	@echo "make examples   编译全部示例"
	@echo "make exercises  编译练习起始文件"
	@echo "make solutions  编译参考答案"
	@echo "make test       编译并测试参考答案"
	@echo "make sanitize   使用 ASan/UBSan 运行示例"
	@echo "make clean      删除构建产物"

examples: $(EXAMPLE_BINS) $(BUILD)/examples/10_multi_file

exercises: $(EXERCISE_BINS)

solutions: $(SOLUTION_BINS)

$(BUILD)/examples/%: examples/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

$(BUILD)/examples/10_multi_file: examples/10_multi_file.c examples/calculator.c examples/calculator.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) examples/10_multi_file.c examples/calculator.c -o $@

$(BUILD)/exercises/%: exercises/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

$(BUILD)/solutions/%: solutions/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $< -o $@

test: examples solutions
	bash scripts/test.sh

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" examples
	bash scripts/run_examples.sh

clean:
	rm -rf $(BUILD)
