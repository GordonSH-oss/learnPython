#include <vector>

// TODO: 使用 std::jthread 将 vector 分块求和，避免共享可变累计值。

int main() {
    std::vector<int> values(10000, 1);
    (void)values;
    return 0;
}

