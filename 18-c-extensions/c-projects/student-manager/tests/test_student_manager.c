#include "student_registry.h"

#include <assert.h>
#include <string.h>

int main(void) {
    /* 实体校验应在插入前拒绝无效学号和成绩。 */
    Student invalid;
    assert(!student_create(&invalid, 0, "Ada", 90));
    assert(!student_create(&invalid, 1, "Ada", 101));

    StudentRegistry registry;
    student_registry_init(&registry);

    /* 按真实调用者的使用顺序测试公共接口。 */
    Student ada;
    Student grace;
    assert(student_create(&ada, 1, "Ada", 88.5));
    assert(student_create(&grace, 2, "Grace", 96.0));
    assert(student_registry_add(&registry, ada));
    assert(student_registry_add(&registry, grace));
    assert(!student_registry_add(&registry, ada));
    assert(strcmp(student_registry_find(&registry, 2)->name, "Grace") == 0);

    /* 除基本增删查外，还要验证统计和排序等派生行为。 */
    ScoreStatistics statistics;
    assert(student_registry_statistics(&registry, &statistics));
    assert(statistics.average == 92.25);
    student_registry_sort_by_score(&registry, true);
    assert(registry.items[0].id == 2);
    assert(student_registry_remove(&registry, 1));
    assert(registry.size == 1);

    /* 测试代码拥有注册表，也必须释放其动态数组。 */
    student_registry_destroy(&registry);
}
