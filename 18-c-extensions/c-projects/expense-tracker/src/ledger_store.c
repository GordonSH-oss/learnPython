#include "ledger_store.h"

#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

bool ledger_store_load(const char *path, Ledger *ledger) {
    FILE *file = fopen(path, "r");
    if (file == NULL) return errno == ENOENT;
    bool success = true;
    char line[512];
    while (fgets(line, sizeof line, file) != NULL) {
        int id;
        char date[11], type_text[8], category[LEDGER_TEXT_CAPACITY];
        char note[LEDGER_TEXT_CAPACITY];
        int64_t cents;
        char extra;
        if (sscanf(line, "%d,%10[^,],%7[^,],%" SCNd64 ",%63[^,],%63[^\n] %c",
                   &id, date, type_text, &cents, category, note, &extra) != 6) {
            success = false;
            break;
        }
        TransactionType type;
        if (strcmp(type_text, "income") == 0) type = TRANSACTION_INCOME;
        else if (strcmp(type_text, "expense") == 0) type = TRANSACTION_EXPENSE;
        else { success = false; break; }
        Transaction transaction;
        if (!transaction_create(&transaction, id, date, type, cents, category, note) ||
            !ledger_add(ledger, transaction)) {
            success = false;
            break;
        }
    }
    if (ferror(file)) success = false;
    if (fclose(file) != 0) success = false;
    return success;
}

bool ledger_store_save(const char *path, const Ledger *ledger) {
    FILE *file = fopen(path, "w");
    if (file == NULL) return false;
    bool success = true;
    for (size_t index = 0; index < ledger->size; ++index) {
        const Transaction *item = &ledger->items[index];
        const char *type = item->type == TRANSACTION_INCOME ? "income" : "expense";
        if (fprintf(file, "%d,%s,%s,%" PRId64 ",%s,%s\n",
                    item->id, item->date, type, item->cents,
                    item->category, item->note) < 0) {
            success = false;
            break;
        }
    }
    if (fclose(file) != 0) success = false;
    return success;
}

