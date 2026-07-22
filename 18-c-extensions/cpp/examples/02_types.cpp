#include <iostream>
#include <string>
#include <vector>

void append_marker(std::string& text) {
    text += "!";
}

int main() {
    std::string message = "references";
    append_marker(message);

    const std::vector<int> values{2, 4, 6};
    int total = 0;
    for (const auto value : values) total += value;

    std::cout << message << ": " << total << '\n';
}

