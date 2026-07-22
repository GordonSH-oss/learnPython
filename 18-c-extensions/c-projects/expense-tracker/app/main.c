#include "ledger.h"
#include "ledger_store.h"

#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_money(int64_t cents) {
    uint64_t magnitude = cents < 0 ? (uint64_t)(-(cents + 1)) + 1 : (uint64_t)cents;
    printf("%s%" PRIu64 ".%02" PRIu64,
           cents < 0 ? "-" : "", magnitude / 100, magnitude % 100);
}

static bool parse_int(const char *text, int *result) {
    char *end;
    errno = 0;
    long value = strtol(text, &end, 10);
    if (errno || end == text || *end || value <= 0 || value > 2147483647L) return false;
    *result = (int)value;
    return true;
}

static bool parse_money(const char *text, int64_t *cents) {
    if (text == NULL || cents == NULL || text[0] == '\0') return false;
    int64_t whole = 0;
    size_t index = 0;
    while (text[index] >= '0' && text[index] <= '9') {
        int digit = text[index] - '0';
        if (whole > (INT64_MAX / 100 - digit) / 10) return false;
        whole = whole * 10 + digit;
        ++index;
    }
    if (index == 0) return false;
    int fraction = 0;
    if (text[index] == '.') {
        ++index;
        if (text[index] < '0' || text[index] > '9') return false;
        fraction = (text[index++] - '0') * 10;
        if (text[index] >= '0' && text[index] <= '9')
            fraction += text[index++] - '0';
    }
    if (text[index] != '\0') return false;
    if (whole > (INT64_MAX - fraction) / 100) return false;
    *cents = whole * 100 + fraction;
    return *cents > 0;
}

static void usage(const char *program) {
    fprintf(stderr,
            "usage:\n"
            "  %s FILE add ID DATE income|expense AMOUNT CATEGORY NOTE\n"
            "  %s FILE list\n"
            "  %s FILE summary [CATEGORY]\n"
            "  %s FILE remove ID\n", program, program, program, program);
}

int main(int argc, char **argv) {
    if (argc < 3) { usage(argv[0]); return 2; }
    Ledger ledger;
    ledger_init(&ledger);
    if (!ledger_store_load(argv[1], &ledger)) {
        fprintf(stderr, "failed to load %s\n", argv[1]);
        ledger_destroy(&ledger);
        return 1;
    }
    int result = 0;
    if (strcmp(argv[2], "add") == 0 && argc == 9) {
        int id;
        int64_t cents;
        TransactionType type;
        if (strcmp(argv[5], "income") == 0) type = TRANSACTION_INCOME;
        else if (strcmp(argv[5], "expense") == 0) type = TRANSACTION_EXPENSE;
        else { fputs("invalid type\n", stderr); result = 1; goto done; }
        Transaction transaction;
        if (!parse_int(argv[3], &id) || !parse_money(argv[6], &cents) ||
            !transaction_create(&transaction, id, argv[4], type, cents,
                                argv[7], argv[8]) ||
            !ledger_add(&ledger, transaction) ||
            !ledger_store_save(argv[1], &ledger)) {
            fputs("failed to add transaction\n", stderr);
            result = 1;
        }
    } else if (strcmp(argv[2], "list") == 0 && argc == 3) {
        for (size_t index = 0; index < ledger.size; ++index) {
            const Transaction *item = &ledger.items[index];
            printf("%d %s %-7s ", item->id, item->date,
                   item->type == TRANSACTION_INCOME ? "income" : "expense");
            print_money(item->cents);
            printf(" %-12s %s\n", item->category, item->note);
        }
    } else if (strcmp(argv[2], "summary") == 0 && (argc == 3 || argc == 4)) {
        int64_t balance;
        if (!ledger_balance(&ledger, &balance)) {
            fputs("balance overflow\n", stderr);
            result = 1;
            goto done;
        }
        printf("balance=");
        print_money(balance);
        putchar('\n');
        if (argc == 4) {
            int64_t category_total;
            if (!ledger_category_expense(&ledger, argv[3], &category_total)) {
                fputs("category total overflow\n", stderr);
                result = 1;
                goto done;
            }
            printf("expense[%s]=", argv[3]);
            print_money(category_total);
            putchar('\n');
        }
    } else if (strcmp(argv[2], "remove") == 0 && argc == 4) {
        int id;
        if (!parse_int(argv[3], &id) || !ledger_remove(&ledger, id) ||
            !ledger_store_save(argv[1], &ledger)) {
            fputs("failed to remove transaction\n", stderr);
            result = 1;
        }
    } else {
        usage(argv[0]);
        result = 2;
    }
done:
    ledger_destroy(&ledger);
    return result;
}
