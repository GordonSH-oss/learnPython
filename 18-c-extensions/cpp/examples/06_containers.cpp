#include <iostream>
#include <span>
#include <string>
#include <vector>

int sum(std::span<const int> values) {
    int total = 0;
    for (int value : values) total += value;
    return total;
}

int main() {
    std::vector<int> values{1, 2, 3, 4};
    std::string label = "vector sum";
    std::cout << label << '=' << sum(values) << '\n';
}

