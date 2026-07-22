#include <iostream>
#include <string>
#include <utility>
#include <vector>

struct Report {
    std::string title;
    std::vector<int> values;
};

int main() {
    Report source{"measurements", {1, 2, 3, 4}};
    Report destination = std::move(source);
    std::cout << destination.title << ": " << destination.values.size() << '\n';
}

