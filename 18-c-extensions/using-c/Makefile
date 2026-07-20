PYTHON ?= python3
CC ?= clang
BUILD := build
EXT_SUFFIX := $(shell $(PYTHON)-config --extension-suffix)
PY_CFLAGS := $(shell $(PYTHON)-config --cflags)
PY_LDFLAGS := $(shell $(PYTHON)-config --ldflags)
CFLAGS := -std=c17 -O3 -Wall -Wextra -Wpedantic

ifeq ($(shell uname -s),Darwin)
SHARED_LIB := $(BUILD)/libarithmetic.dylib
SHARED_FLAGS := -dynamiclib
EXTENSION_FLAGS := -bundle -undefined dynamic_lookup
else
SHARED_LIB := $(BUILD)/libarithmetic.so
SHARED_FLAGS := -shared -fPIC
EXTENSION_FLAGS := -shared -fPIC
endif

EXTENSION := $(BUILD)/mymath$(EXT_SUFFIX)

.PHONY: all ctypes extension cython test benchmark clean help

all: ctypes extension

ctypes: $(SHARED_LIB)

extension: $(EXTENSION)

$(BUILD):
	mkdir -p $(BUILD)

$(SHARED_LIB): arithmetic.c arithmetic.h | $(BUILD)
	$(CC) $(CFLAGS) $(SHARED_FLAGS) arithmetic.c -o $@

$(EXTENSION): mymath_module.c | $(BUILD)
	$(CC) $(CFLAGS) $(PY_CFLAGS) $(EXTENSION_FLAGS) $< $(PY_LDFLAGS) -o $@

cython:
	$(PYTHON) setup_cython.py build_ext --build-lib $(BUILD) --build-temp $(BUILD)/temp

test: all
	PYTHONPATH=$(BUILD) USING_C_BUILD=$(BUILD) $(PYTHON) -m unittest -v test_using_c.py

benchmark: all
	PYTHONPATH=$(BUILD) USING_C_BUILD=$(BUILD) $(PYTHON) benchmark.py

clean:
	rm -rf $(BUILD) cython_example.c

help:
	@echo "make all        构建 ctypes 动态库和 Python/C API 扩展"
	@echo "make test       运行正确性和错误契约测试"
	@echo "make benchmark  比较 Python、ctypes 和 C 扩展性能"
	@echo "make cython     构建可选 Cython 示例（需安装 Cython/setuptools）"
	@echo "make clean      删除构建产物"
