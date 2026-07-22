#ifndef TEXT_ANALYZER_ANALYZER_H
#define TEXT_ANALYZER_ANALYZER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

typedef struct {
    size_t lines;
    size_t words;
    size_t bytes;
} TextStatistics;

typedef struct {
    const char *word;
    size_t count;
} WordFrequency;

typedef struct WordSlot WordSlot;

typedef struct {
    TextStatistics statistics;
    WordSlot *slots;
    size_t slot_count;
    size_t used;
} TextAnalyzer;

void text_analyzer_init(TextAnalyzer *analyzer);
void text_analyzer_destroy(TextAnalyzer *analyzer);
bool text_analyzer_process(TextAnalyzer *analyzer, FILE *input);
size_t text_analyzer_unique_words(const TextAnalyzer *analyzer);
size_t text_analyzer_top(const TextAnalyzer *analyzer,
                         WordFrequency *output, size_t capacity);

#endif

