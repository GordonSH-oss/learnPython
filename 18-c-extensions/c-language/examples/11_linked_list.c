#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

static bool push(Node **head, int value) {
    if (head == NULL) return false;
    Node *node = malloc(sizeof *node);
    if (node == NULL) return false;
    node->value = value;
    node->next = *head;
    *head = node;
    return true;
}

static void destroy(Node **head) {
    if (head == NULL) return;
    while (*head != NULL) {
        Node *next = (*head)->next;
        free(*head);
        *head = next;
    }
}

static bool remove_first(Node **head, int target) {
    if (head == NULL) return false;

    Node **link = head;
    while (*link != NULL) {
        if ((*link)->value == target) {
            Node *removed = *link;
            *link = removed->next;
            free(removed);
            return true;
        }
        link = &(*link)->next;
    }
    return false;
}

typedef bool (*Predicate)(int value, void *context);

static size_t count_if(const Node *head, Predicate predicate, void *context) {
    size_t count = 0;
    for (const Node *node = head; node != NULL; node = node->next) {
        if (predicate(node->value, context)) ++count;
    }
    return count;
}

static bool is_greater_than(int value, void *context) {
    const int *threshold = context;
    return value > *threshold;
}

int main(void) {
    Node *head = NULL;
    for (int value = 3; value >= 1; value--) {
        if (!push(&head, value)) {
            destroy(&head);
            return 1;
        }
    }
    for (const Node *node = head; node != NULL; node = node->next) {
        printf("%d ", node->value);
    }
    putchar('\n');

    if (!remove_first(&head, 2)) {
        fputs("value not found\n", stderr);
        destroy(&head);
        return 1;
    }

    int threshold = 1;
    printf("values greater than %d: %zu\n",
           threshold, count_if(head, is_greater_than, &threshold));
    destroy(&head);
    return 0;
}
