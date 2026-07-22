#include "ledger.h"

#include <assert.h>

int main(void) {
    Transaction invalid;
    assert(!transaction_create(&invalid, 1, "2026-13-01", TRANSACTION_EXPENSE,
                               100, "food", "bad date"));
    Ledger ledger;
    ledger_init(&ledger);
    Transaction salary, lunch;
    assert(transaction_create(&salary, 1, "2026-07-01", TRANSACTION_INCOME,
                              500000, "salary", "monthly"));
    assert(transaction_create(&lunch, 2, "2026-07-02", TRANSACTION_EXPENSE,
                              3500, "food", "lunch"));
    assert(ledger_add(&ledger, salary));
    assert(ledger_add(&ledger, lunch));
    assert(!ledger_add(&ledger, salary));
    int64_t total;
    assert(ledger_balance(&ledger, &total) && total == 496500);
    assert(ledger_category_expense(&ledger, "food", &total) && total == 3500);
    assert(ledger_remove(&ledger, 2));
    assert(ledger_balance(&ledger, &total) && total == 500000);
    ledger_destroy(&ledger);
}
