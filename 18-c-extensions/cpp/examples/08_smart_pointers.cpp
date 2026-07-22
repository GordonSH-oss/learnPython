#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Node {
    explicit Node(std::string value) : value(std::move(value)) {}
    std::string value;
    std::vector<std::unique_ptr<Node>> children;
};

int main() {
    auto root = std::make_unique<Node>("root");
    root->children.push_back(std::make_unique<Node>("child"));
    std::cout << root->value << " -> " << root->children.front()->value << '\n';
}

