#include <algorithm>
#include <iostream>
#include <numeric>
#include <ranges>
#include <vector>

int main() {
    std::vector<int> values{9, 2, 7, 4, 1, 6};
    std::ranges::sort(values);
    auto even = values | std::views::filter([](int value) { return value % 2 == 0; });
    long long total = std::accumulate(even.begin(), even.end(), 0LL);
    std::cout << "even total=" << total << '\n';
}

