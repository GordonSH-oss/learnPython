CC ?= clang
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -g
CPPFLAGS := -Iinclude
BUILD := build

.PHONY: all test sanitize clean
all: $(BUILD)/text-analyzer

$(BUILD)/text-analyzer: app/main.c src/analyzer.c | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD)/test: tests/test_analyzer.c src/analyzer.c | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD):
	mkdir -p $(BUILD)

test: all $(BUILD)/test
	$(BUILD)/test
	@tmp=$$(mktemp); printf 'one two one\n' >$$tmp; \
	$(BUILD)/text-analyzer $$tmp 2 | grep -q '2.*one'; rm -f $$tmp

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" test

clean:
	rm -rf $(BUILD)

