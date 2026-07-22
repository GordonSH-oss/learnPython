#include <cassert>
#include <cstdio>
#include <stdexcept>
#include <utility>

class UniqueFile {
public:
    explicit UniqueFile(std::FILE* file) : file_(file) {
        if (file_ == nullptr) throw std::invalid_argument("null file");
    }
    ~UniqueFile() {
        if (file_ != nullptr) std::fclose(file_);
    }
    UniqueFile(const UniqueFile&) = delete;
    UniqueFile& operator=(const UniqueFile&) = delete;
    UniqueFile(UniqueFile&& other) noexcept
        : file_(std::exchange(other.file_, nullptr)) {}
    UniqueFile& operator=(UniqueFile&& other) noexcept {
        if (this != &other) {
            if (file_ != nullptr) std::fclose(file_);
            file_ = std::exchange(other.file_, nullptr);
        }
        return *this;
    }
    [[nodiscard]] bool valid() const { return file_ != nullptr; }
private:
    std::FILE* file_;
};

int main() {
    UniqueFile first{std::tmpfile()};
    UniqueFile second{std::move(first)};
    assert(!first.valid());
    assert(second.valid());
}

