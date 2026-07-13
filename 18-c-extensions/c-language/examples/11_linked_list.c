#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

static bool push(Node **head, int value) {
    Node *node = malloc(sizeof *node);
    if (node == NULL) return false;
    node->value = value;
    node->next = *head;
    *head = node;
    return true;
}

static void destroy(Node **head) {
    while (*head != NULL) {
        Node *next = (*head)->next;
        free(*head);
        *head = next;
    }
}

int main(void) {
    Node *head = NULL;
    for (int value = 3; value >= 1; value--) {
        if (!push(&head, value)) {
            destroy(&head);
            return 1;
        }
    }
    for (const Node *node = head; node != NULL; node = node->next) printf("%d ", node->value);
    putchar('\n');
    destroy(&head);
    return 0;
}
