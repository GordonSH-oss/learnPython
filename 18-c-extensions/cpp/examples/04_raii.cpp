#include <cstdio>
#include <iostream>
#include <stdexcept>

class TemporaryFile {
public:
    TemporaryFile() : file_(std::tmpfile()) {
        if (file_ == nullptr) throw std::runtime_error("tmpfile failed");
    }

    ~TemporaryFile() {
        if (file_ != nullptr) std::fclose(file_);
    }

    TemporaryFile(const TemporaryFile&) = delete;
    TemporaryFile& operator=(const TemporaryFile&) = delete;

    void write(const char* text) {
        if (std::fputs(text, file_) == EOF) throw std::runtime_error("write failed");
    }

private:
    std::FILE* file_;
};

int main() {
    TemporaryFile file;
    file.write("RAII\n");
    std::cout << "temporary file is managed by an object\n";
}

