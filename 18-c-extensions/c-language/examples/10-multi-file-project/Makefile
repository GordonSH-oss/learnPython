CC ?= clang
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -g
CPPFLAGS ?= -Iinclude
AR ?= ar
ARFLAGS := rcs
BUILD ?= build

LIB_SOURCES := src/task.c src/task_list.c src/task_store.c
LIB_OBJECTS := $(patsubst src/%.c,$(BUILD)/src/%.o,$(LIB_SOURCES))
LIBRARY := $(BUILD)/libtasker.a
APP := $(BUILD)/tasker
TEST := $(BUILD)/test_tasker

.PHONY: all test clean

all: $(APP)

$(BUILD)/src/%.o: src/%.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -c $< -o $@

$(BUILD)/app/main.o: app/main.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -c $< -o $@

$(BUILD)/tests/test_task_list.o: tests/test_task_list.c
	@mkdir -p $(@D)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -c $< -o $@

$(LIBRARY): $(LIB_OBJECTS)
	@mkdir -p $(@D)
	$(AR) $(ARFLAGS) $@ $^

$(APP): $(BUILD)/app/main.o $(LIBRARY)
	$(CC) $(CFLAGS) $< -L$(BUILD) -ltasker -o $@

$(TEST): $(BUILD)/tests/test_task_list.o $(LIBRARY)
	$(CC) $(CFLAGS) $< -L$(BUILD) -ltasker -o $@

test: $(TEST)
	$(TEST)

clean:
	rm -rf $(BUILD)

-include $(LIB_OBJECTS:.o=.d) $(BUILD)/app/main.d $(BUILD)/tests/test_task_list.d
