#ifndef EXPENSE_TRACKER_LEDGER_H
#define EXPENSE_TRACKER_LEDGER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define LEDGER_TEXT_CAPACITY 64

typedef enum {
    TRANSACTION_INCOME,
    TRANSACTION_EXPENSE
} TransactionType;

typedef struct {
    int id;
    char date[11];
    TransactionType type;
    int64_t cents;
    char category[LEDGER_TEXT_CAPACITY];
    char note[LEDGER_TEXT_CAPACITY];
} Transaction;

typedef struct {
    Transaction *items;
    size_t size;
    size_t capacity;
} Ledger;

bool transaction_create(Transaction *transaction, int id, const char *date,
                        TransactionType type, int64_t cents,
                        const char *category, const char *note);
void ledger_init(Ledger *ledger);
void ledger_destroy(Ledger *ledger);
bool ledger_add(Ledger *ledger, Transaction transaction);
bool ledger_remove(Ledger *ledger, int id);
bool ledger_balance(const Ledger *ledger, int64_t *balance);
bool ledger_category_expense(const Ledger *ledger, const char *category,
                             int64_t *total);

#endif
