#include "analyzer.h"

#include <ctype.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define INITIAL_SLOT_COUNT 32
#define WORD_CAPACITY 128

struct WordSlot {
    char *word;
    size_t count;
};

static uint64_t hash_word(const char *word) {
    uint64_t hash = UINT64_C(1469598103934665603);
    while (*word != '\0') {
        hash ^= (unsigned char)*word++;
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static char *duplicate_word(const char *word) {
    size_t length = strlen(word) + 1;
    char *copy = malloc(length);
    if (copy != NULL) memcpy(copy, word, length);
    return copy;
}

void text_analyzer_init(TextAnalyzer *analyzer) {
    if (analyzer == NULL) return;
    analyzer->statistics = (TextStatistics){0};
    analyzer->slots = NULL;
    analyzer->slot_count = 0;
    analyzer->used = 0;
}

void text_analyzer_destroy(TextAnalyzer *analyzer) {
    if (analyzer == NULL) return;
    for (size_t index = 0; index < analyzer->slot_count; ++index)
        free(analyzer->slots[index].word);
    free(analyzer->slots);
    text_analyzer_init(analyzer);
}

static bool insert_existing(WordSlot *slots, size_t slot_count,
                            char *word, size_t count) {
    size_t index = (size_t)(hash_word(word) % slot_count);
    while (slots[index].word != NULL) index = (index + 1) % slot_count;
    slots[index].word = word;
    slots[index].count = count;
    return true;
}

static bool resize_table(TextAnalyzer *analyzer, size_t slot_count) {
    if (slot_count > SIZE_MAX / sizeof *analyzer->slots) return false;
    WordSlot *slots = calloc(slot_count, sizeof *slots);
    if (slots == NULL) return false;
    for (size_t index = 0; index < analyzer->slot_count; ++index) {
        WordSlot *old = &analyzer->slots[index];
        if (old->word != NULL) insert_existing(slots, slot_count, old->word, old->count);
    }
    free(analyzer->slots);
    analyzer->slots = slots;
    analyzer->slot_count = slot_count;
    return true;
}

static bool record_word(TextAnalyzer *analyzer, const char *word) {
    if (analyzer->slot_count == 0 && !resize_table(analyzer, INITIAL_SLOT_COUNT))
        return false;
    if ((analyzer->used + 1) * 10 >= analyzer->slot_count * 7) {
        if (analyzer->slot_count > SIZE_MAX / 2 ||
            !resize_table(analyzer, analyzer->slot_count * 2)) return false;
    }
    size_t index = (size_t)(hash_word(word) % analyzer->slot_count);
    while (analyzer->slots[index].word != NULL) {
        if (strcmp(analyzer->slots[index].word, word) == 0) {
            ++analyzer->slots[index].count;
            return true;
        }
        index = (index + 1) % analyzer->slot_count;
    }
    char *copy = duplicate_word(word);
    if (copy == NULL) return false;
    analyzer->slots[index].word = copy;
    analyzer->slots[index].count = 1;
    ++analyzer->used;
    return true;
}

bool text_analyzer_process(TextAnalyzer *analyzer, FILE *input) {
    if (analyzer == NULL || input == NULL) return false;
    char word[WORD_CAPACITY];
    size_t length = 0;
    bool saw_data = false;
    bool last_was_newline = false;
    int character;
    while ((character = fgetc(input)) != EOF) {
        saw_data = true;
        ++analyzer->statistics.bytes;
        last_was_newline = character == '\n';
        if (last_was_newline) ++analyzer->statistics.lines;

        if (isalnum((unsigned char)character)) {
            if (length + 1 >= sizeof word) return false;
            word[length++] = (char)tolower((unsigned char)character);
        } else if (length > 0) {
            word[length] = '\0';
            if (!record_word(analyzer, word)) return false;
            ++analyzer->statistics.words;
            length = 0;
        }
    }
    if (ferror(input)) return false;
    if (length > 0) {
        word[length] = '\0';
        if (!record_word(analyzer, word)) return false;
        ++analyzer->statistics.words;
    }
    if (saw_data && !last_was_newline) ++analyzer->statistics.lines;
    return true;
}

size_t text_analyzer_unique_words(const TextAnalyzer *analyzer) {
    return analyzer == NULL ? 0 : analyzer->used;
}

static int frequency_descending(const void *left, const void *right) {
    const WordFrequency *a = left;
    const WordFrequency *b = right;
    if (a->count != b->count) return (a->count < b->count) - (a->count > b->count);
    return strcmp(a->word, b->word);
}

size_t text_analyzer_top(const TextAnalyzer *analyzer,
                         WordFrequency *output, size_t capacity) {
    if (analyzer == NULL || output == NULL || capacity == 0) return 0;
    if (analyzer->used == 0) return 0;
    WordFrequency *all = malloc(analyzer->used * sizeof *all);
    if (all == NULL) return 0;
    size_t count = 0;
    for (size_t index = 0; index < analyzer->slot_count; ++index) {
        if (analyzer->slots[index].word != NULL) {
            all[count++] = (WordFrequency){analyzer->slots[index].word,
                                           analyzer->slots[index].count};
        }
    }
    qsort(all, count, sizeof *all, frequency_descending);
    size_t result_count = count < capacity ? count : capacity;
    memcpy(output, all, result_count * sizeof *output);
    free(all);
    return result_count;
}
