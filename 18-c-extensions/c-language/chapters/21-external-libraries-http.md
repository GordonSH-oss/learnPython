# 21 第三方库与 libcurl HTTP 客户端

## 学习目标

完成本章后，你应能：

- 区分头文件、库文件和运行时网络资源。
- 使用 `curl-config` 获取第三方库的编译与链接参数。
- 理解 libcurl easy interface 的初始化、配置、执行和清理生命周期。
- 使用函数指针回调分批接收 HTTP 响应体。
- 正确处理 `CURLcode`、HTTP 状态码、超时、重定向和 TLS 验证。
- 把依赖第三方库的源文件接入现有 Makefile。

本章基于 `examples/21_http_client.c`。它来自一个使用 libcurl 请求网页的最小实验，并补齐了参数输入、初始化检查、选项错误、HTTP 状态和自动构建支持。

## 为什么使用 libcurl

第 19 章展示了原始 Socket API。Socket 能建立 TCP 连接，但一个可用的 HTTPS 客户端还需要处理：

- DNS 解析。
- TCP 连接与超时。
- TLS 握手和证书验证。
- HTTP 请求头、响应头和状态码。
- 重定向、代理、压缩和不同 HTTP 版本。
- 响应数据的分批读取。

这些规则不适合在普通应用中重复实现。libcurl 是成熟的网络传输库，可以处理 HTTP、HTTPS 和其他协议。本章关注如何正确集成库，而不是自行实现 HTTP 协议栈。

```text
应用代码
   ↓ libcurl easy interface
DNS / TCP / TLS / HTTP
   ↓
远程服务器
```

## 第三方库由什么组成

在 C 中使用 libcurl，需要同时满足两个阶段的依赖：

| 阶段 | 需要的内容 | 本例配置 |
| --- | --- | --- |
| 编译 | 函数、类型和常量声明 | `#include <curl/curl.h>` |
| 链接 | 函数的机器码实现 | `-lcurl` 及平台所需依赖 |

只包含头文件并不足以生成程序：

```c
#include <curl/curl.h>
```

这只让编译器知道 `CURL`、`CURLcode`、`curl_easy_init` 等名称和签名。最终链接时仍必须提供 libcurl。

如果能编译却出现 `undefined reference to curl_easy_init` 或 `symbol(s) not found`，通常是链接命令缺少 libcurl，而不是缺少头文件。

## 检查开发环境

本章需要 libcurl 的开发头文件和库。先检查：

```bash
curl-config --version
curl-config --cflags
curl-config --libs
```

`curl-config` 由 libcurl 开发包提供，会输出当前安装版本真正需要的参数。例如，简单环境可能只输出：

```text
-lcurl
```

其他平台可能还需要头文件目录、库目录或 libcurl 的传递依赖。因此，比起手写固定路径，更适合让构建系统调用 `curl-config`。

macOS 通常随系统工具链提供 libcurl。Linux 如果缺少开发文件，需要安装发行版对应的开发包，例如 Debian/Ubuntu 的 `libcurl4-openssl-dev`。包名和 TLS 后端可能因系统而异。

## 编译示例

在教程根目录运行：

```bash
make build/examples/21_http_client
```

等价的核心命令是：

```bash
clang -std=c17 -Wall -Wextra -Wpedantic \
  $(curl-config --cflags) \
  examples/21_http_client.c \
  $(curl-config --libs) \
  -o build/examples/21_http_client
```

运行时传入 URL：

```bash
build/examples/21_http_client https://example.com
```

不传参数时，程序只输出用法并成功退出，因此全量示例测试不依赖外部网络。

## libcurl easy interface 生命周期

示例遵循固定生命周期：

```text
curl_global_init
        ↓
curl_easy_init
        ↓
curl_easy_setopt 配置请求
        ↓
curl_easy_perform 执行请求
        ↓
curl_easy_getinfo 读取结果元数据
        ↓
curl_easy_cleanup
        ↓
curl_global_cleanup
```

### 全局初始化

```c
CURLcode result = curl_global_init(CURL_GLOBAL_DEFAULT);
if (result != CURLE_OK) {
    fprintf(stderr, "curl global initialization failed: %s\n",
            curl_easy_strerror(result));
    return 1;
}
```

全局初始化应在使用其他 libcurl API 前完成。返回值也需要检查，不能假定初始化永远成功。

在多线程程序中，应在创建工作线程前完成全局初始化，并在所有 libcurl 操作结束后再清理。不要让多个线程随意交错调用全局初始化和清理。

### 创建 easy handle

```c
CURL *handle = curl_easy_init();
if (handle == NULL) {
    fputs("curl easy handle creation failed\n", stderr);
    curl_global_cleanup();
    return 1;
}
```

`CURL *` 是一个不透明句柄。调用者通过公开 API 操作它，不应猜测或访问其内部结构。

如果创建失败，已经完成的全局初始化仍需要对应清理。这体现了 C 中常见的资源管理原则：每一次成功获取都必须在所有后续退出路径中对应释放。

## 使用选项配置请求

libcurl 通过 `curl_easy_setopt` 设置 URL、回调、超时等选项：

```c
curl_easy_setopt(handle, CURLOPT_URL, url);
curl_easy_setopt(handle, CURLOPT_FOLLOWLOCATION, 1L);
curl_easy_setopt(handle, CURLOPT_TIMEOUT, 8L);
```

示例把设置过程集中在 `configure_request`，每次设置后检查 `CURLcode`。一旦某个选项失败，后续配置不再继续。

`curl_easy_setopt` 接收可变参数，编译器无法像普通函数那样完整检查最后一个参数。必须严格使用文档要求的类型：

- 字符串选项传 `char *` 或 `const char *`。
- 开关和整数选项通常要求 `long`，因此写 `1L`、`8L`。
- 回调选项传签名匹配的函数指针。
- 上下文选项传 `void *`。

把 `1L` 写成 `1` 在许多平台看似工作，但对可变参数函数来说，类型不匹配可能导致未定义行为。

### URL

示例从命令行获取 URL：

```c
result = curl_easy_setopt(handle, CURLOPT_URL, url);
```

这样同一个程序可以请求不同资源，不必每次修改源码重新编译。

### 重定向

```c
curl_easy_setopt(handle, CURLOPT_FOLLOWLOCATION, 1L);
```

启用后，libcurl 会按照自身限制处理服务器返回的重定向。生产代码还应根据安全要求设置最大重定向次数，并考虑是否允许跨协议重定向。

### 超时

```c
curl_easy_setopt(handle, CURLOPT_TIMEOUT, 8L);
```

总超时防止请求无限等待。更细致的客户端通常会分别设置连接超时和整体传输超时，并根据业务决定是否重试。

### User-Agent

```c
curl_easy_setopt(handle, CURLOPT_USERAGENT, "learn-c-libcurl/1.0");
```

明确的 User-Agent 让服务器和日志能够识别客户端。公共网络服务可能拒绝缺少 User-Agent 或行为异常的请求。

## 回调如何接收响应体

HTTP 响应不一定一次到达。libcurl 在收到一批数据后调用写回调：

```c
static size_t write_response(char *data,
                             size_t size,
                             size_t count,
                             void *context) {
    FILE *output = context;
    size_t written = fwrite(data, size, count, output);
    return written * size;
}
```

回调参数的含义是：

- `data`：本次收到的数据起始地址。
- `size`：每个数据单元的字节数。
- `count`：数据单元数量。
- `context`：调用者通过 `CURLOPT_WRITEDATA` 提供的上下文。

本次数据总字节数是 `size * count`。回调必须返回实际处理的字节数；如果返回值少于收到的字节数，libcurl 会把它视为写入失败并终止传输。

示例把 `stdout` 作为上下文：

```c
curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, write_response);
curl_easy_setopt(handle, CURLOPT_WRITEDATA, stdout);
```

因此回调中的 `void *context` 实际保存 `FILE *`。这是 C 回调接口的常见模式：函数指针描述行为，`void *` 携带调用者状态。

```text
CURLOPT_WRITEFUNCTION -> write_response
CURLOPT_WRITEDATA     -> stdout
                              ↓
libcurl 收到数据 -> write_response(data, ..., stdout)
```

如果要把响应保存到文件，可以把 `fopen` 返回的 `FILE *` 作为上下文。如果要保存在内存中，则可以传入一个包含缓冲区指针、长度和容量的结构体，并在回调中安全扩容。

## 执行请求与两层错误

```c
result = curl_easy_perform(handle);
```

`curl_easy_perform` 是同步调用：当前线程会一直执行到请求完成或失败。`CURLcode` 描述传输层结果，例如 DNS、连接、TLS、超时或写回调失败。

```c
if (result != CURLE_OK) {
    fprintf(stderr, "request failed: %s\n",
            curl_easy_strerror(result));
}
```

HTTP 客户端必须区分两层结果：

1. 传输是否成功，即 `CURLcode` 是否为 `CURLE_OK`。
2. HTTP 服务端返回什么状态，例如 `200`、`404` 或 `500`。

传输成功不等于业务成功。服务器返回 `404` 时，HTTP 交换本身仍可能成功完成。

示例在传输成功后读取状态码：

```c
long status = 0;
result = curl_easy_getinfo(handle, CURLINFO_RESPONSE_CODE, &status);
```

最终只有 libcurl 操作成功并且状态码小于 `400` 时返回进程状态 `0`。

## TLS 证书验证

HTTPS 安全依赖证书验证。libcurl 默认验证服务器证书和主机名，应保留默认行为。

不要用下面的选项绕过证书问题：

```c
// 不安全：不要作为修复证书错误的常规方法
curl_easy_setopt(handle, CURLOPT_SSL_VERIFYPEER, 0L);
curl_easy_setopt(handle, CURLOPT_SSL_VERIFYHOST, 0L);
```

关闭验证会让客户端无法确认连接的服务器身份，容易受到中间人攻击。遇到证书错误时，应检查系统时间、CA 证书包、代理环境和服务器证书链。

不同平台的 libcurl 可能使用不同 TLS 后端和 CA 路径。不要假定“macOS 一定无需配置”能够推广到所有构建和部署环境。

## 清理资源

无论请求成功还是失败，只要句柄创建成功，就应清理：

```c
curl_easy_cleanup(handle);
curl_global_cleanup();
```

清理顺序与获取顺序相反：先释放 easy handle，再清理全局状态。

当前示例在所有配置和传输操作完成后汇合到统一清理路径，避免每个错误分支重复资源释放代码。

## Makefile 如何接入 libcurl

普通单文件示例只需要编译器和 C 标准库，但 libcurl 示例需要额外参数。根 Makefile 单独定义：

```make
CURL_CFLAGS := $(shell curl-config --cflags)
CURL_LIBS := $(shell curl-config --libs)

$(BUILD)/examples/21_http_client: examples/21_http_client.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(CURL_CFLAGS) $< $(CURL_LIBS) -o $@
```

源文件必须从通用示例列表中排除，避免先套用不带 `-lcurl` 的模式规则。

链接命令中，源文件或目标文件放在库参数前面具有更好的可移植性。部分静态链接器按从左到右的顺序解析符号，如果库出现在引用它的目标文件之前，可能不会提取所需实现。

大型项目也常使用 `pkg-config`：

```bash
pkg-config --cflags --libs libcurl
```

选择 `curl-config` 还是 `pkg-config` 取决于项目和目标平台；关键是让构建系统从已安装库获得参数，而不是把本机绝对路径写死。

## 与原始 Socket 的边界

第 19 章的 Socket 示例适合理解操作系统网络接口和 TCP/UDP 数据流；本章的 libcurl 示例适合编写真正的 HTTP 客户端。

| 需求 | 更合适的层次 |
| --- | --- |
| 学习 `socket/connect/read/write` | 原始 Socket API |
| 自定义二进制 TCP 协议 | 原始 Socket API |
| 发起 HTTP/HTTPS 请求 | libcurl |
| 处理 TLS、代理、重定向和压缩 | libcurl |

使用成熟库不是逃避底层知识，而是在理解边界后把复杂协议交给经过验证的实现。

## 常见错误

### 只包含头文件，没有链接库

编译器认识函数声明，但链接器找不到实现。使用 `curl-config --libs` 提供链接参数。

### 回调返回固定值

写回调必须返回实际处理的字节数。固定返回 `0` 会让 libcurl 认为写入失败。

### 忽略 `curl_easy_setopt` 返回值

选项名称、类型或当前构建不支持某项功能时，配置可能失败。不要直接进入传输阶段。

### 把 HTTP 404 当作传输失败

`CURLE_OK` 只说明传输成功。还要读取 HTTP 状态或使用适合业务的 libcurl 选项。

### 为解决证书错误关闭 TLS 验证

这会移除 HTTPS 的身份验证能力。应修复证书或 CA 配置。

### 在自动测试中依赖公网

公网状态、DNS、代理和证书环境都不稳定。自动测试应使用本地测试服务器或依赖注入；本例无参数运行时不发起请求。

## 检查点

1. `#include <curl/curl.h>` 是否会自动链接 libcurl？不会。
2. 为什么 `CURLOPT_TIMEOUT` 使用 `8L`？可变参数接口要求对应选项使用 `long`。
3. 为什么写回调可能被调用多次？响应数据可能分批到达。
4. `CURLE_OK` 是否意味着 HTTP 状态为 `200`？不意味着。
5. 为什么不能随意关闭 TLS 证书验证？客户端将无法确认服务器身份。

## 动手练习

1. 请求 `https://example.com`，分别观察响应体、HTTP 状态和进程退出码。
2. 请求一个不存在的页面，验证传输成功与 HTTP `404` 可以同时发生。
3. 使用 `CURLOPT_CONNECTTIMEOUT` 增加独立的连接超时。
4. 增加响应头回调，分别输出状态行、响应头和响应体。
5. 把 `stdout` 替换成由命令行指定的输出文件，并保证所有错误路径都关闭文件。
6. 定义动态缓冲区结构体，在写回调中使用 `realloc` 收集完整响应；处理容量溢出和分配失败。
7. 使用本地 HTTP 服务器代替公网，为成功响应、404 和超时编写可重复测试。
8. 分别删除头文件包含和链接参数，比较编译错误与链接错误。
