CC ?= clang
CFLAGS ?= -std=c17 -Wall -Wextra -Wpedantic -g
CPPFLAGS := -Iinclude
BUILD := build
SOURCES := src/ledger.c src/ledger_store.c

.PHONY: all test sanitize clean
all: $(BUILD)/expense-tracker

$(BUILD)/expense-tracker: app/main.c $(SOURCES) | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD)/test: tests/test_ledger.c src/ledger.c | $(BUILD)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $@

$(BUILD):
	mkdir -p $(BUILD)

test: all $(BUILD)/test
	$(BUILD)/test
	@tmp=$$(mktemp); \
	$(BUILD)/expense-tracker $$tmp add 1 2026-07-01 income 100.00 salary demo; \
	$(BUILD)/expense-tracker $$tmp summary | grep -q 'balance=100.00'; \
	rm -f $$tmp

sanitize: clean
	$(MAKE) CFLAGS="$(CFLAGS) -fsanitize=address,undefined -fno-omit-frame-pointer" test

clean:
	rm -rf $(BUILD)

