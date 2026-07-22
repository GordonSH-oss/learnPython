#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>

std::optional<int> lookup(const std::unordered_map<std::string, int>& values,
                          const std::string& key) {
    auto found = values.find(key);
    if (found == values.end()) return std::nullopt;
    return found->second;
}

int main() {
    const std::unordered_map<std::string, int> values{{"answer", 42}};
    if (auto result = lookup(values, "answer")) std::cout << *result << '\n';
}

