CXX ?= clang++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -g
BUILD := build
EXAMPLE_SOURCES := $(wildcard examples/*.cpp)
EXAMPLE_BINS := $(patsubst examples/%.cpp,$(BUILD)/examples/%,$(EXAMPLE_SOURCES))
SOLUTION_SOURCES := $(wildcard solutions/*.cpp)
SOLUTION_BINS := $(patsubst solutions/%.cpp,$(BUILD)/solutions/%,$(SOLUTION_SOURCES))

.PHONY: help examples solutions test sanitize clean

help:
	@echo "make examples   编译全部示例"
	@echo "make solutions  编译练习答案"
	@echo "make test       编译并运行示例和答案检查"
	@echo "make sanitize   使用 ASan/UBSan 运行示例"
	@echo "make clean      删除构建产物"

examples: $(EXAMPLE_BINS)

solutions: $(SOLUTION_BINS)

$(BUILD)/examples/%: examples/%.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BUILD)/solutions/%: solutions/%.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BUILD)/examples/13_concurrency: examples/13_concurrency.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) -pthread $< -o $@

test: examples solutions
	bash scripts/test.sh

sanitize: clean
	$(MAKE) CXXFLAGS="$(CXXFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" examples
	bash scripts/run_examples.sh

clean:
	rm -rf $(BUILD)

