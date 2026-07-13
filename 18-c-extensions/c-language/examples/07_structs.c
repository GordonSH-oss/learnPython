#include <stdio.h>

typedef enum { LEVEL_BEGINNER, LEVEL_INTERMEDIATE, LEVEL_ADVANCED } Level;

typedef struct {
    const char *name;
    int completed_lessons;
    Level level;
} Learner;

static void print_learner(const Learner *learner) {
    if (learner == NULL) return;
    printf("%s completed %d lessons (level %d)\n",
           learner->name, learner->completed_lessons, learner->level);
}

int main(void) {
    Learner learner = {.name = "Ada", .completed_lessons = 7, .level = LEVEL_INTERMEDIATE};
    print_learner(&learner);
    return 0;
}
