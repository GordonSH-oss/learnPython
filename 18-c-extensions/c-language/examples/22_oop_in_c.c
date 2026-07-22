/**
 * 22_oop_in_c.c - 使用结构体、嵌入和函数指针表模拟面向对象
 * 编译: clang -std=c17 -Wall -Wextra -Wpedantic 22_oop_in_c.c -o 22_oop_in_c
 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Animal Animal;

typedef struct {
    void (*speak)(const Animal *self);
    void (*destroy)(Animal *self);
} AnimalVTable;

struct Animal {
    const AnimalVTable *vtable;
    const char *name;
};

typedef struct {
    Animal base;
    int remaining_tricks;
} Dog;

typedef struct {
    Animal base;
    int remaining_naps;
} Cat;

static void animal_speak(const Animal *self) {
    if (self != NULL && self->vtable != NULL && self->vtable->speak != NULL) {
        self->vtable->speak(self);
    }
}

static void animal_destroy(Animal *self) {
    if (self != NULL && self->vtable != NULL && self->vtable->destroy != NULL) {
        self->vtable->destroy(self);
    }
}

static void dog_speak(const Animal *animal) {
    const Dog *self = (const Dog *)animal;
    printf("%s: woof! I can perform %d more tricks.\n",
           self->base.name, self->remaining_tricks);
}

static void dog_destroy(Animal *animal) {
    Dog *self = (Dog *)animal;
    printf("destroy dog: %s\n", self->base.name);
    free(self);
}

static const AnimalVTable DOG_VTABLE = {
    .speak = dog_speak,
    .destroy = dog_destroy,
};

static Dog *dog_create(const char *name, int remaining_tricks) {
    Dog *self = malloc(sizeof *self);
    if (self == NULL) {
        return NULL;
    }

    self->base.vtable = &DOG_VTABLE;
    self->base.name = name;
    self->remaining_tricks = remaining_tricks;
    return self;
}

static Animal *dog_as_animal(Dog *self) {
    return self == NULL ? NULL : &self->base;
}

static void cat_speak(const Animal *animal) {
    const Cat *self = (const Cat *)animal;
    printf("%s: meow. I have %d naps left.\n",
           self->base.name, self->remaining_naps);
}

static void cat_destroy(Animal *animal) {
    Cat *self = (Cat *)animal;
    printf("destroy cat: %s\n", self->base.name);
    free(self);
}

static const AnimalVTable CAT_VTABLE = {
    .speak = cat_speak,
    .destroy = cat_destroy,
};

static Cat *cat_create(const char *name, int remaining_naps) {
    Cat *self = malloc(sizeof *self);
    if (self == NULL) {
        return NULL;
    }

    self->base.vtable = &CAT_VTABLE;
    self->base.name = name;
    self->remaining_naps = remaining_naps;
    return self;
}

static Animal *cat_as_animal(Cat *self) {
    return self == NULL ? NULL : &self->base;
}

int main(void) {
    Dog *dog = dog_create("Bolt", 3);
    Cat *cat = cat_create("Mochi", 7);
    if (dog == NULL || cat == NULL) {
        animal_destroy(dog_as_animal(dog));
        animal_destroy(cat_as_animal(cat));
        fprintf(stderr, "failed to create animals\n");
        return EXIT_FAILURE;
    }

    Animal *animals[] = {
        dog_as_animal(dog),
        cat_as_animal(cat),
    };
    const size_t count = sizeof animals / sizeof animals[0];

    puts("same interface, different behavior:");
    for (size_t i = 0; i < count; ++i) {
        animal_speak(animals[i]);
    }

    puts("\npolymorphic destruction:");
    for (size_t i = 0; i < count; ++i) {
        animal_destroy(animals[i]);
    }

    return EXIT_SUCCESS;
}
