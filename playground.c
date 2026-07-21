#include <stdio.h>
#include <curl/curl.h>

// 接收响应数据回调
size_t write_cb(char *buf, size_t size, size_t count, void *arg)
{
    size_t len = size * count;
    fwrite(buf, size, count, stdout);
    return len;
}

int main(void)
{
    // 初始化curl
    curl_global_init(CURL_GLOBAL_ALL);
    CURL *handle = curl_easy_init();
    if (!handle)
    {
        fprintf(stderr, "curl 创建失败\n");
        curl_global_cleanup();
        return 1;
    }

    const char *url = "https://docs.rongcloud.cn";
    curl_easy_setopt(handle, CURLOPT_URL, url);
    curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_cb);
    curl_easy_setopt(handle, CURLOPT_FOLLOWLOCATION, 1L); // 自动跳转重定向
    curl_easy_setopt(handle, CURLOPT_TIMEOUT, 8L);        // 8秒超时

    // Mac自带根证书，不用关闭SSL校验，注释掉下面两行更安全
    // curl_easy_setopt(handle, CURLOPT_SSL_VERIFYPEER, 0L);
    // curl_easy_setopt(handle, CURLOPT_SSL_VERIFYHOST, 0L);

    // 发起请求
    CURLcode ret = curl_easy_perform(handle);
    if (ret != CURLE_OK)
    {
        fprintf(stderr, "请求出错：%s\n", curl_easy_strerror(ret));
    }

    // 释放资源
    curl_easy_cleanup(handle);
    curl_global_cleanup();
    return 0;
}