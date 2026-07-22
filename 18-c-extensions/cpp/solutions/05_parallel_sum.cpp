#include <algorithm>
#include <cassert>
#include <cstddef>
#include <numeric>
#include <span>
#include <thread>
#include <vector>

long long parallel_sum(std::span<const int> values, std::size_t worker_count) {
    if (values.empty()) return 0;
    worker_count = std::clamp<std::size_t>(worker_count, 1, values.size());
    std::vector<long long> partials(worker_count, 0);
    std::vector<std::jthread> workers;
    workers.reserve(worker_count);

    for (std::size_t worker = 0; worker < worker_count; ++worker) {
        std::size_t begin = values.size() * worker / worker_count;
        std::size_t end = values.size() * (worker + 1) / worker_count;
        workers.emplace_back([values, begin, end, &partials, worker] {
            partials[worker] = std::accumulate(values.begin() + begin,
                                               values.begin() + end, 0LL);
        });
    }
    workers.clear();
    return std::accumulate(partials.begin(), partials.end(), 0LL);
}

int main() {
    std::vector<int> values(10000, 1);
    assert(parallel_sum(values, 4) == 10000);
    assert(parallel_sum({}, 4) == 0);
}

