#include <cassert>
#include <iostream>
#include <stdexcept>

class Temperature {
public:
    explicit Temperature(double celsius) : celsius_(celsius) {
        if (celsius < -273.15) throw std::invalid_argument("below absolute zero");
    }
    [[nodiscard]] double celsius() const { return celsius_; }
    [[nodiscard]] double fahrenheit() const { return celsius_ * 9.0 / 5.0 + 32.0; }
private:
    double celsius_;
};

int main() {
    Temperature freezing{0.0};
    assert(freezing.celsius() == 0.0);
    assert(freezing.fahrenheit() == 32.0);
    try {
        Temperature invalid{-300.0};
        (void)invalid;
        return 1;
    } catch (const std::invalid_argument&) {
    }
    std::cout << freezing.fahrenheit() << '\n';
}

