#include "analyzer.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *input = tmpfile();
    assert(input != NULL);
    assert(fputs("Hello C\nhello, memory!", input) != EOF);
    rewind(input);

    TextAnalyzer analyzer;
    text_analyzer_init(&analyzer);
    assert(text_analyzer_process(&analyzer, input));
    assert(analyzer.statistics.lines == 2);
    assert(analyzer.statistics.words == 4);
    assert(text_analyzer_unique_words(&analyzer) == 3);

    WordFrequency top[3];
    assert(text_analyzer_top(&analyzer, top, 3) == 3);
    assert(strcmp(top[0].word, "hello") == 0);
    assert(top[0].count == 2);
    text_analyzer_destroy(&analyzer);
    assert(fclose(input) == 0);
}

