#include <stdio.h>

typedef enum { LEVEL_BEGINNER, LEVEL_INTERMEDIATE, LEVEL_ADVANCED } Level;

typedef struct {
    const char *name;
    int completed_lessons;
    Level level;
} Learner;

typedef enum { VALUE_INTEGER, VALUE_REAL, VALUE_TEXT } ValueKind;

typedef struct {
    ValueKind kind;
    union {
        int integer;
        double real;
        const char *text;
    } as;
} Value;

static void print_learner(const Learner *learner) {
    if (learner == NULL) return;
    printf("%s completed %d lessons (level %d)\n",
           learner->name, learner->completed_lessons, learner->level);
}

static void print_value(const Value *value) {
    if (value == NULL) return;

    switch (value->kind) {
        case VALUE_INTEGER:
            printf("integer: %d\n", value->as.integer);
            break;
        case VALUE_REAL:
            printf("real: %.2f\n", value->as.real);
            break;
        case VALUE_TEXT:
            printf("text: %s\n", value->as.text);
            break;
        default:
            fputs("invalid value\n", stderr);
            break;
    }
}

int main(void) {
    Learner learner = {
        .name = "Ada",
        .completed_lessons = 7,
        .level = LEVEL_INTERMEDIATE,
    };
    Value values[] = {
        {.kind = VALUE_INTEGER, .as.integer = 42},
        {.kind = VALUE_REAL, .as.real = 3.5},
        {.kind = VALUE_TEXT, .as.text = "hello"},
    };
    size_t value_count = sizeof values / sizeof values[0];

    print_learner(&learner);
    for (size_t index = 0; index < value_count; index++) {
        print_value(&values[index]);
    }

    printf("Learner: size=%zu align=%zu\n",
           sizeof(Learner), _Alignof(Learner));
    printf("Value: size=%zu align=%zu\n",
           sizeof(Value), _Alignof(Value));
    return 0;
}
