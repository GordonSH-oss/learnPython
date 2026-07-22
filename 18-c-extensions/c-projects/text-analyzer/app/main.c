#include "analyzer.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

static bool parse_top(const char *text, size_t *top) {
    char *end;
    errno = 0;
    unsigned long value = strtoul(text, &end, 10);
    if (errno || end == text || *end || value == 0 || value > 1000) return false;
    *top = (size_t)value;
    return true;
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "usage: %s FILE [TOP_N]\n", argv[0]);
        return 2;
    }
    size_t top = 10;
    if (argc == 3 && !parse_top(argv[2], &top)) {
        fputs("TOP_N must be between 1 and 1000\n", stderr);
        return 2;
    }
    FILE *input = fopen(argv[1], "rb");
    if (input == NULL) {
        perror(argv[1]);
        return 1;
    }
    TextAnalyzer analyzer;
    text_analyzer_init(&analyzer);
    bool success = text_analyzer_process(&analyzer, input);
    if (fclose(input) != 0) success = false;
    if (!success) {
        fputs("failed to analyze input (word may be too long or memory exhausted)\n", stderr);
        text_analyzer_destroy(&analyzer);
        return 1;
    }

    printf("lines=%zu words=%zu bytes=%zu unique=%zu\n",
           analyzer.statistics.lines, analyzer.statistics.words,
           analyzer.statistics.bytes, text_analyzer_unique_words(&analyzer));
    WordFrequency *frequencies = malloc(top * sizeof *frequencies);
    if (frequencies == NULL) {
        text_analyzer_destroy(&analyzer);
        return 1;
    }
    size_t count = text_analyzer_top(&analyzer, frequencies, top);
    for (size_t index = 0; index < count; ++index)
        printf("%zu\t%s\n", frequencies[index].count, frequencies[index].word);
    free(frequencies);
    text_analyzer_destroy(&analyzer);
    return 0;
}

