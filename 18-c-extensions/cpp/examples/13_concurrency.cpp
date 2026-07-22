#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

class Counter {
public:
    void increment() {
        std::lock_guard lock{mutex_};
        ++value_;
    }
    [[nodiscard]] int value() const {
        std::lock_guard lock{mutex_};
        return value_;
    }
private:
    mutable std::mutex mutex_;
    int value_ = 0;
};

int main() {
    Counter counter;
    std::vector<std::jthread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&counter] {
            for (int n = 0; n < 1000; ++n) counter.increment();
        });
    }
    threads.clear(); // destroys jthreads, joining them
    std::cout << "counter=" << counter.value() << '\n';
}

