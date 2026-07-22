#include <cstddef>
#include <iostream>
#include <limits>

extern "C" int cpp_sum(const int* values, std::size_t length,
                         long long* result) noexcept {
    if (result == nullptr || (values == nullptr && length != 0)) return -1;
    long long total = 0;
    for (std::size_t index = 0; index < length; ++index) {
        int value = values[index];
        if ((value > 0 && total > std::numeric_limits<long long>::max() - value) ||
            (value < 0 && total < std::numeric_limits<long long>::min() - value)) {
            return -2;
        }
        total += value;
    }
    *result = total;
    return 0;
}

int main() {
    int values[]{1, 2, 3, 4};
    long long result = 0;
    int status = cpp_sum(values, 4, &result);
    std::cout << "status=" << status << " sum=" << result << '\n';
}

