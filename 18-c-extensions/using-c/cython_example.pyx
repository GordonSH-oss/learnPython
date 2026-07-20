# cython: language_level=3, boundscheck=False, wraparound=False

"""Typed Cython implementation of the Sieve of Eratosthenes."""


def primes(int limit):
    if limit < 2:
        return []

    cdef int candidate, multiple
    cdef bytearray sieve = bytearray(b"\x01") * (limit + 1)
    cdef list result = []
    sieve[0] = 0
    sieve[1] = 0

    for candidate in range(2, limit + 1):
        if sieve[candidate]:
            result.append(candidate)
            if candidate <= limit // candidate:
                for multiple in range(candidate * candidate,
                                      limit + 1, candidate):
                    sieve[multiple] = 0
    return result
