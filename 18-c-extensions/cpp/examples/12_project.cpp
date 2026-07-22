#include <cassert>
#include <iostream>
#include <string>
#include <utility>

class Task {
public:
    explicit Task(std::string title) : title_(std::move(title)) {}
    void complete() { completed_ = true; }
    [[nodiscard]] bool completed() const { return completed_; }
private:
    std::string title_;
    bool completed_ = false;
};

int main() {
    Task task{"test project"};
    assert(!task.completed());
    task.complete();
    assert(task.completed());
    std::cout << "project test passed\n";
}

