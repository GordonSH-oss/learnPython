/**
 * 13_preprocessor_bits.c - 预处理器与位操作
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic -DDEBUG 13_preprocessor_bits.c -o 13_preprocessor_bits
 */
#include <stdio.h>
#include <stdint.h>

/* ====== 1. 带参数的宏 (do-while 技巧保证安全) ====== */
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SWAP(a, b) do { __typeof__(a) _t = (a); (a) = (b); (b) = _t; } while(0)

/* ====== 2. 可变参数宏 ====== */
#define DEBUG_LOG(fmt, ...) \
    fprintf(stderr, "[DEBUG %s:%d] " fmt "\n", __FILE__, __LINE__ __VA_OPT__(,) __VA_ARGS__)

/* ====== 3. 条件编译 ====== */
#ifdef DEBUG
  #define LOG(fmt, ...) DEBUG_LOG(fmt __VA_OPT__(,) __VA_ARGS__)
#else
  #define LOG(fmt, ...) ((void)0)
#endif

/* ====== 4. X-Macro 模式: 枚举 + 字符串表 ====== */
#define COLOR_LIST(X) \
    X(RED)           \
    X(GREEN)         \
    X(BLUE)          \
    X(YELLOW)

#define ENUM_ITEM(name) COLOR_##name,
#define STR_ITEM(name)  [COLOR_##name] = #name,

enum Color { COLOR_LIST(ENUM_ITEM) COLOR_COUNT };
static const char *color_names[] = { COLOR_LIST(STR_ITEM) };

/* ====== 5. 位操作: 设置/清除/翻转/检查 ====== */
#define BIT_SET(val, bit)    ((val) |=  (1U << (bit)))
#define BIT_CLEAR(val, bit)  ((val) &= ~(1U << (bit)))
#define BIT_TOGGLE(val, bit) ((val) ^=  (1U << (bit)))
#define BIT_CHECK(val, bit)  (((val) >> (bit)) & 1U)

/* ====== 6. 实用: 权限系统 (位掩码) ====== */
typedef uint8_t Permission;
#define PERM_READ    (1U << 0)  /* 0001 */
#define PERM_WRITE   (1U << 1)  /* 0010 */
#define PERM_EXEC    (1U << 2)  /* 0100 */
#define PERM_ADMIN   (1U << 3)  /* 1000 */

static void print_perms(Permission p) {
    printf("  权限 [%c%c%c%c] (0x%02X)\n",
           (p & PERM_ADMIN) ? 'A' : '-',
           (p & PERM_EXEC)  ? 'X' : '-',
           (p & PERM_WRITE) ? 'W' : '-',
           (p & PERM_READ)  ? 'R' : '-', p);
}

int main(void) {
    /* 1. 带参数宏 */
    printf("=== 带参数宏 ===\n");
    int x = 10, y = 20;
    printf("MAX(%d, %d) = %d\n", x, y, MAX(x, y));
    printf("MIN(%d, %d) = %d\n", x, y, MIN(x, y));
    SWAP(x, y);
    printf("SWAP 后: x=%d, y=%d\n", x, y);

    /* 2 & 3. 可变参数宏 + 条件编译 */
    printf("\n=== 条件编译 (DEBUG=%d) ===\n",
#ifdef DEBUG
           1);
    LOG("这条只在 -DDEBUG 时出现, x=%d", x);
#else
           0);
    LOG("这条不会出现: %s", "test");
#endif

    /* 4. X-Macro */
    printf("\n=== X-Macro 枚举 ===\n");
    for (int i = 0; i < COLOR_COUNT; i++)
        printf("  enum %d -> %s\n", i, color_names[i]);

    /* 5. 位操作 */
    printf("\n=== 位操作 ===\n");
    unsigned int flags = 0;
    BIT_SET(flags, 1);
    printf("  SET bit1:    0b%04u (十进制 %u)\n",
           (flags>>3&1)*1000+(flags>>2&1)*100+(flags>>1&1)*10+(flags&1), flags);
    BIT_TOGGLE(flags, 3);
    printf("  TOGGLE bit3: 0b%04u (十进制 %u)\n",
           (flags>>3&1)*1000+(flags>>2&1)*100+(flags>>1&1)*10+(flags&1), flags);
    BIT_CLEAR(flags, 1);
    printf("  CLEAR bit1:  0b%04u (十进制 %u)\n",
           (flags>>3&1)*1000+(flags>>2&1)*100+(flags>>1&1)*10+(flags&1), flags);
    printf("  CHECK bit3:  %u\n", BIT_CHECK(flags, 3));

    /* 6. 权限系统 */
    printf("\n=== 权限系统 ===\n");
    Permission user = PERM_READ | PERM_WRITE;
    printf("普通用户:"); print_perms(user);
    user |= PERM_EXEC;
    printf("加执行权:"); print_perms(user);
    Permission admin = PERM_READ | PERM_WRITE | PERM_EXEC | PERM_ADMIN;
    printf("管理员:  "); print_perms(admin);

    if (admin & PERM_ADMIN)
        printf("  -> 管理员验证通过!\n");

    return 0;
}
