#include <cassert>
#include <sstream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>

std::pair<std::string, std::size_t> most_frequent(std::string_view text) {
    std::istringstream input{std::string{text}};
    std::unordered_map<std::string, std::size_t> frequencies;
    std::string word;
    while (input >> word) ++frequencies[word];

    std::pair<std::string, std::size_t> result;
    for (const auto& [candidate, count] : frequencies) {
        if (count > result.second) result = {candidate, count};
    }
    return result;
}

int main() {
    auto [word, count] = most_frequent("c++ values c++ raii values c++");
    assert(word == "c++" && count == 3);
}

