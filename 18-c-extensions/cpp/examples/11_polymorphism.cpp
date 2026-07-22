#include <iostream>
#include <memory>
#include <numbers>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;
    [[nodiscard]] virtual double area() const = 0;
};

class Circle final : public Shape {
public:
    explicit Circle(double radius) : radius_(radius) {}
    [[nodiscard]] double area() const override {
        return std::numbers::pi * radius_ * radius_;
    }
private:
    double radius_;
};

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(2.0));
    std::cout << shapes.front()->area() << '\n';
}

