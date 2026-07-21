# 21 Multi-File Project

This example builds a small persistent task manager from independently compiled modules.

```text
include/             public module contracts
src/                 domain and storage implementations
app/main.c            CLI composition root
tests/                module integration tests
build/libtasker.a     static library
build/tasker          final executable
```

Build and test from this directory:

```bash
make
make test
```

Try the CLI without writing into the source tree:

```bash
TASKER_FILE=/tmp/tasks.tsv build/tasker add "learn the linker"
TASKER_FILE=/tmp/tasks.tsv build/tasker list
TASKER_FILE=/tmp/tasks.tsv build/tasker done 1
TASKER_FILE=/tmp/tasks.tsv build/tasker remove 1
```

The Makefile generates dependency files with `-MMD -MP`. Changing a public header therefore rebuilds every object that includes it, while changing one `.c` file recompiles only that translation unit before relinking.
