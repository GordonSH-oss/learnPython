#include "calculator.h"

double calculator_add(double left, double right) {
    return left + right;
}

bool calculator_divide(double numerator, double denominator, double *result) {
    if (denominator == 0.0 || result == 0) return false;
    *result = numerator / denominator;
    return true;
}
