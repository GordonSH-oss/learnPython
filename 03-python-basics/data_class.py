from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    # 使用 lambda 返回共享字典的引用
    scores: dict = field(default_factory=lambda: shared_scores)

student1 = Student(name="John", scores={"math": 90, "english": 80, "science": 70})
student1.scores["math"] = 100
print(student1)
student2 = Student("Tom")
# student2 = Student(name="Tom", scores={"math": 80, "english": 80, "science": 70})
print(student2)
