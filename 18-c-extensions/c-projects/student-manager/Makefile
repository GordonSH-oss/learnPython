CC ?= clang
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -g
CPPFLAGS := -Iinclude
BUILD := build
SOURCES := src/student.c src/student_registry.c src/student_store.c

# 这些名称表示操作而不是文件。声明为伪目标后，即使出现同名文件，Make 也会执行规则。
.PHONY: all test sanitize clean

# 第一个目标是默认目标，因此 `make` 与 `make all` 等价。
all: $(BUILD)/student-manager

# $^ 展开为全部依赖文件，$@ 展开为当前目标路径。
$(BUILD)/student-manager: app/main.c $(SOURCES) | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

# 单元测试只验证实体和注册表，不需要链接 CLI 与文件存储实现。
$(BUILD)/test: tests/test_student_manager.c src/student.c src/student_registry.c | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

# 竖线后是顺序依赖：必须先创建目录，但目录时间戳变化不会触发程序重建。
$(BUILD):
	mkdir -p $(BUILD)

# 先运行单元测试，再用临时数据文件测试编译后的 CLI。
test: $(BUILD)/student-manager $(BUILD)/test
	$(BUILD)/test
	@tmp=$$(mktemp); \
	$(BUILD)/student-manager $$tmp add 1 Ada 91.5; \
	$(BUILD)/student-manager $$tmp find 1 | grep -q Ada; \
	$(BUILD)/student-manager $$tmp stats | grep -q 'count=1'; \
	rm -f $$tmp

# 重新构建并启用非法内存访问和未定义行为检测。
sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" test

# 只删除可重新生成的构建产物，不删除源代码和数据文件。
clean:
	rm -rf $(BUILD)
