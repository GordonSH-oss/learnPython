#ifndef EXPENSE_TRACKER_STORE_H
#define EXPENSE_TRACKER_STORE_H

#include "ledger.h"

#include <stdbool.h>

bool ledger_store_load(const char *path, Ledger *ledger);
bool ledger_store_save(const char *path, const Ledger *ledger);

#endif

