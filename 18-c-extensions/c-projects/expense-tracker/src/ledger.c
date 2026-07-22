#include "ledger.h"

#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static bool valid_date(const char *date) {
    if (date == NULL || strlen(date) != 10 || date[4] != '-' || date[7] != '-')
        return false;
    for (size_t index = 0; index < 10; ++index) {
        if (index != 4 && index != 7 && !isdigit((unsigned char)date[index]))
            return false;
    }
    int month = (date[5] - '0') * 10 + date[6] - '0';
    int day = (date[8] - '0') * 10 + date[9] - '0';
    return month >= 1 && month <= 12 && day >= 1 && day <= 31;
}

static bool copy_text(char destination[LEDGER_TEXT_CAPACITY], const char *source) {
    if (source == NULL || source[0] == '\0' || strchr(source, ',') != NULL) return false;
    int written = snprintf(destination, LEDGER_TEXT_CAPACITY, "%s", source);
    return written >= 0 && written < LEDGER_TEXT_CAPACITY;
}

bool transaction_create(Transaction *transaction, int id, const char *date,
                        TransactionType type, int64_t cents,
                        const char *category, const char *note) {
    if (transaction == NULL || id <= 0 || !valid_date(date) || cents <= 0 ||
        (type != TRANSACTION_INCOME && type != TRANSACTION_EXPENSE) ||
        !copy_text(transaction->category, category) ||
        !copy_text(transaction->note, note)) return false;
    transaction->id = id;
    transaction->type = type;
    transaction->cents = cents;
    memcpy(transaction->date, date, 11);
    return true;
}

void ledger_init(Ledger *ledger) {
    if (ledger == NULL) return;
    ledger->items = NULL;
    ledger->size = 0;
    ledger->capacity = 0;
}

void ledger_destroy(Ledger *ledger) {
    if (ledger == NULL) return;
    free(ledger->items);
    ledger_init(ledger);
}

static Transaction *find_transaction(Ledger *ledger, int id) {
    for (size_t index = 0; index < ledger->size; ++index)
        if (ledger->items[index].id == id) return &ledger->items[index];
    return NULL;
}

static bool ensure_capacity(Ledger *ledger) {
    if (ledger->size < ledger->capacity) return true;
    size_t capacity = ledger->capacity == 0 ? 8 : ledger->capacity * 2;
    if (capacity < ledger->capacity || capacity > SIZE_MAX / sizeof *ledger->items)
        return false;
    Transaction *items = realloc(ledger->items, capacity * sizeof *items);
    if (items == NULL) return false;
    ledger->items = items;
    ledger->capacity = capacity;
    return true;
}

bool ledger_add(Ledger *ledger, Transaction transaction) {
    if (ledger == NULL || find_transaction(ledger, transaction.id) != NULL ||
        !ensure_capacity(ledger)) return false;
    ledger->items[ledger->size++] = transaction;
    return true;
}

bool ledger_remove(Ledger *ledger, int id) {
    if (ledger == NULL) return false;
    for (size_t index = 0; index < ledger->size; ++index) {
        if (ledger->items[index].id == id) {
            memmove(&ledger->items[index], &ledger->items[index + 1],
                    (ledger->size - index - 1) * sizeof *ledger->items);
            --ledger->size;
            return true;
        }
    }
    return false;
}

static bool add_checked(int64_t left, int64_t right, int64_t *result) {
    if ((right > 0 && left > INT64_MAX - right) ||
        (right < 0 && left < INT64_MIN - right)) return false;
    *result = left + right;
    return true;
}

bool ledger_balance(const Ledger *ledger, int64_t *balance) {
    if (ledger == NULL || balance == NULL) return false;
    int64_t value = 0;
    for (size_t index = 0; index < ledger->size; ++index) {
        const Transaction *item = &ledger->items[index];
        int64_t amount = item->type == TRANSACTION_INCOME ? item->cents : -item->cents;
        if (!add_checked(value, amount, &value)) return false;
    }
    *balance = value;
    return true;
}

bool ledger_category_expense(const Ledger *ledger, const char *category,
                             int64_t *total) {
    if (ledger == NULL || category == NULL || total == NULL) return false;
    int64_t value = 0;
    for (size_t index = 0; index < ledger->size; ++index) {
        const Transaction *item = &ledger->items[index];
        if (item->type == TRANSACTION_EXPENSE &&
            strcmp(item->category, category) == 0 &&
            !add_checked(value, item->cents, &value)) return false;
    }
    *total = value;
    return true;
}
