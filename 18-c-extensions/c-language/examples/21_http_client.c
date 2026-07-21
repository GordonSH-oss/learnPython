#include <curl/curl.h>

#include <stdio.h>

static size_t write_response(char *data, size_t size, size_t count, void *context) {
    FILE *output = context;
    size_t written = fwrite(data, size, count, output);
    return written * size;
}

static CURLcode configure_request(CURL *handle, const char *url) {
    CURLcode result = curl_easy_setopt(handle, CURLOPT_URL, url);
    if (result == CURLE_OK) {
        result = curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_response);
    }
    if (result == CURLE_OK) {
        result = curl_easy_setopt(handle, CURLOPT_WRITEDATA, stdout);
    }
    if (result == CURLE_OK) {
        result = curl_easy_setopt(handle, CURLOPT_FOLLOWLOCATION, 1L);
    }
    if (result == CURLE_OK) {
        result = curl_easy_setopt(handle, CURLOPT_TIMEOUT, 8L);
    }
    if (result == CURLE_OK) {
        result = curl_easy_setopt(handle, CURLOPT_USERAGENT, "learn-c-libcurl/1.0");
    }
    return result;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <url>\n", argv[0]);
        return argc == 1 ? 0 : 1;
    }

    CURLcode result = curl_global_init(CURL_GLOBAL_DEFAULT);
    if (result != CURLE_OK) {
        fprintf(stderr, "curl global initialization failed: %s\n",
                curl_easy_strerror(result));
        return 1;
    }

    CURL *handle = curl_easy_init();
    if (handle == NULL) {
        fputs("curl easy handle creation failed\n", stderr);
        curl_global_cleanup();
        return 1;
    }

    result = configure_request(handle, argv[1]);
    if (result == CURLE_OK) result = curl_easy_perform(handle);

    long status = 0;
    if (result == CURLE_OK) {
        result = curl_easy_getinfo(handle, CURLINFO_RESPONSE_CODE, &status);
    }

    if (result != CURLE_OK) {
        fprintf(stderr, "request failed: %s\n", curl_easy_strerror(result));
    } else {
        fprintf(stderr, "\nHTTP status: %ld\n", status);
    }

    curl_easy_cleanup(handle);
    curl_global_cleanup();
    return result == CURLE_OK && status < 400 ? 0 : 1;
}
