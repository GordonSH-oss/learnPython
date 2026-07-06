# Source Lens V2

Source Lens 是一个用于学习 Django 源码的本地练习项目。它把课程、源码阅读路径、mini project、用户进度和学习笔记放在同一个 Django 应用里，方便你边做边回到 `../../django` 源码验证。

## 运行

```bash
cd 08-frameworks/django-projects/source_lens
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_lessons
.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

打开 `http://127.0.0.1:8000/`。

如果需要记录个人进度，先在页面右上角注册一个本地学习账号。课程内容可以匿名浏览，但完成步骤、完成任务、更新练习状态和添加笔记需要登录。

## 推荐学习顺序

1. `配置系统与启动过程`
   - 对照 `manage.py`、`django/__init__.py`、`django/conf/__init__.py`。
   - 重点理解 `DJANGO_SETTINGS_MODULE`、`django.setup()`、`LazySettings`。

2. `请求与响应链路`
   - 打开 `/request-echo/?chapter=http&chapter=orm`。
   - 对照 `django/http/request.py`、`django/http/response.py`、`django/core/handlers/base.py`。

3. `URL 解析与 View 调度`
   - 查看课程页和 `URL Resolver Lab`。
   - 对照 `django/urls/conf.py`、`django/urls/resolvers.py`、`django/views/generic/base.py`。

4. `ORM 与 QuerySet`
   - 完成 `ORM Query Lab`。
   - 对照 `django/db/models/base.py`、`django/db/models/query.py`、`django/db/models/sql/compiler.py`。

## 内置 mini project

- `Request Lab`：练习 `HttpRequest`、query string、headers、cookies、middleware 和 response header。
- `URL Resolver Lab`：练习 `path()`、converter、`reverse()`、class-based view dispatch。
- `ORM Query Lab`：练习 `model._meta`、QuerySet lazy evaluation、SQL 输出和 SQLCompiler。

## Shell 练习

```bash
.venv/bin/python manage.py shell
```

```python
from django.urls import reverse
from learning.models import Exercise, Topic

reverse("learning:project-detail", kwargs={"slug": "url-resolver-lab"})

qs = Exercise.objects.filter(topic__slug="orm-querysets")
qs._result_cache
list(qs)
qs._result_cache
str(qs.query)

Topic.objects.get(slug="orm-querysets")._meta.fields
```

## 验证

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py test learning
.venv/bin/python manage.py seed_lessons
.venv/bin/python manage.py seed_lessons
```

`seed_lessons` 是幂等命令，重复运行不会重复创建课程或任务。

## 关键文件

- `learning/curriculum.py`：中文课程和 mini project 种子数据。
- `learning/models.py`：课程、步骤、项目、用户进度和学习日志模型。
- `learning/views.py`：课程页面、auth 页面、进度提交、lab payload。
- `learning/templates/learning/`：应用内中文课程页面。
- `learning/tests.py`：V2 验收测试。
