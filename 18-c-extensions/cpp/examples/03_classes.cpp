#include <iostream>
#include <stdexcept>

class BankAccount {
public:
    explicit BankAccount(long initial_balance) : balance_(initial_balance) {
        if (initial_balance < 0) throw std::invalid_argument("negative balance");
    }

    void deposit(long amount) {
        if (amount <= 0) throw std::invalid_argument("deposit must be positive");
        balance_ += amount;
    }

    bool withdraw(long amount) {
        if (amount <= 0 || amount > balance_) return false;
        balance_ -= amount;
        return true;
    }

    [[nodiscard]] long balance() const { return balance_; }

private:
    long balance_;
};

int main() {
    BankAccount account{100};
    account.deposit(50);
    account.withdraw(40);
    std::cout << "balance=" << account.balance() << '\n';
}

