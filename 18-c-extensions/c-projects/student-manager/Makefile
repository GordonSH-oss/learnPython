CC ?= clang
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -g
CPPFLAGS := -Iinclude
BUILD := build
SOURCES := src/student.c src/student_registry.c src/student_store.c

.PHONY: all test sanitize clean

all: $(BUILD)/student-manager

$(BUILD)/student-manager: app/main.c $(SOURCES) | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD)/test: tests/test_student_manager.c src/student.c src/student_registry.c | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD):
	mkdir -p $(BUILD)

test: $(BUILD)/student-manager $(BUILD)/test
	$(BUILD)/test
	@tmp=$$(mktemp); \
	$(BUILD)/student-manager $$tmp add 1 Ada 91.5; \
	$(BUILD)/student-manager $$tmp find 1 | grep -q Ada; \
	$(BUILD)/student-manager $$tmp stats | grep -q 'count=1'; \
	rm -f $$tmp

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" test

clean:
	rm -rf $(BUILD)

