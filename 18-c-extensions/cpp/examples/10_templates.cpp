#include <concepts>
#include <iostream>
#include <string>

template <std::totally_ordered T>
const T& maximum(const T& left, const T& right) {
    return left < right ? right : left;
}

int main() {
    std::cout << maximum(4, 9) << '\n';
    std::cout << maximum(std::string{"Ada"}, std::string{"Grace"}) << '\n';
}

