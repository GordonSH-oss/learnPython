#include <filesystem>
#include <iostream>
#include <system_error>

int main() {
    std::error_code error;
    std::uintmax_t files = 0;
    for (const auto& entry : std::filesystem::directory_iterator{".", error}) {
        if (error) break;
        if (entry.is_regular_file(error) && !error) ++files;
    }
    if (error) {
        std::cerr << error.message() << '\n';
        return 1;
    }
    std::cout << "regular files=" << files << '\n';
}

