#include <algorithm>
#include <cassert>
#include <numeric>
#include <optional>
#include <span>
#include <vector>

struct Statistics {
    int minimum;
    int maximum;
    double mean;
};

std::optional<Statistics> calculate(std::span<const int> values) {
    if (values.empty()) return std::nullopt;
    auto [minimum, maximum] = std::minmax_element(values.begin(), values.end());
    long long total = std::accumulate(values.begin(), values.end(), 0LL);
    return Statistics{*minimum, *maximum,
                      static_cast<double>(total) / static_cast<double>(values.size())};
}

int main() {
    std::vector<int> values{4, 1, 9, 6};
    auto result = calculate(values);
    assert(result.has_value());
    assert(result->minimum == 1 && result->maximum == 9 && result->mean == 5.0);
    assert(!calculate({}).has_value());
}

