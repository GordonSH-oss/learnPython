CURRICULUM = [
    {
        "slug": "settings-and-setup",
        "title": "配置系统与启动过程",
        "source_file": "django/__init__.py, django/conf/__init__.py",
        "source_symbol": "django.setup(), LazySettings",
        "summary": "从 manage.py 到 django.setup()，理解 settings 何时加载、app registry 何时填充。",
        "reading_order": 1,
        "lessons": [
            {
                "slug": "bootstrap-flow",
                "title": "从 manage.py 走到 django.setup()",
                "summary": "跟踪命令行启动路径，确认 Django 在真正处理请求前做了什么。",
                "explanation": "Django 的启动不是一次性导入所有东西。manage.py 先设置 DJANGO_SETTINGS_MODULE，再进入命令系统；需要 app registry 时才调用 django.setup()。",
                "source_file": "manage.py, django/__init__.py, django/core/management/__init__.py",
                "source_symbol": "execute_from_command_line(), django.setup()",
                "reading_order": 1,
                "steps": [
                    {
                        "slug": "read-manage-py",
                        "title": "读 manage.py 的两个关键动作",
                        "body": "manage.py 只做两件事：设置环境变量，然后调用 execute_from_command_line()。",
                        "action": "打开本项目 manage.py，找出 DJANGO_SETTINGS_MODULE 和 execute_from_command_line()。",
                        "checkpoint": "你能说清楚为什么 settings 模块路径必须先设置。",
                        "source_file": "source_lens/manage.py",
                        "source_symbol": "main()",
                        "order": 1,
                        "exercises": [
                            {
                                "slug": "trace-manage-py",
                                "title": "画出 manage.py 的调用箭头",
                                "prompt": "写下 manage.py -> execute_from_command_line() -> ManagementUtility.execute() 的调用顺序。",
                                "source_hint": "manage.py, django/core/management/__init__.py",
                                "difficulty": "easy",
                            }
                        ],
                    },
                    {
                        "slug": "trace-django-setup",
                        "title": "拆开 django.setup() 的副作用",
                        "body": "django.setup() 会配置日志、设置 script prefix，并把 INSTALLED_APPS 填充进 app registry。",
                        "action": "打开 django/__init__.py，逐行记录 setup() 的三个动作。",
                        "checkpoint": "你能解释 apps.populate() 为什么必须在模型使用前完成。",
                        "source_file": "django/__init__.py",
                        "source_symbol": "setup()",
                        "order": 2,
                        "exercises": [
                            {
                                "slug": "trace-setup",
                                "title": "Trace django.setup()",
                                "prompt": "打开 django/__init__.py，写下 django.setup() 每个副作用对应的源码行。",
                                "source_hint": "django/__init__.py:setup",
                                "difficulty": "easy",
                            }
                        ],
                    },
                ],
            },
            {
                "slug": "lazy-settings",
                "title": "LazySettings 为什么是懒加载",
                "summary": "理解 settings 对象为什么不是普通 dict，以及第一次访问配置时发生了什么。",
                "explanation": "Django 允许很多模块导入 settings，但不能要求导入瞬间就完成配置。因此 settings 是 LazyObject，第一次访问属性才加载真实 Settings。",
                "source_file": "django/conf/__init__.py",
                "source_symbol": "LazySettings.__getattr__",
                "reading_order": 2,
                "steps": [
                    {
                        "slug": "observe-settings-cache",
                        "title": "观察 settings 属性缓存",
                        "body": "LazySettings 第一次访问属性时会触发 _setup()，之后把值缓存在 __dict__。",
                        "action": "在 shell 中访问 settings.DEBUG 前后对比 settings.__dict__。",
                        "checkpoint": "你能解释为什么第二次访问 settings.DEBUG 不再进入 Settings 模块导入流程。",
                        "source_file": "django/conf/__init__.py",
                        "source_symbol": "LazySettings.__getattr__",
                        "order": 1,
                        "exercises": [
                            {
                                "slug": "lazy-settings-cache",
                                "title": "Observe LazySettings caching",
                                "prompt": "访问 settings.DEBUG 两次，并记录 settings.__dict__ 的变化。",
                                "source_hint": "django/conf/__init__.py:LazySettings.__getattr__",
                                "difficulty": "medium",
                            }
                        ],
                    }
                ],
            },
        ],
    },
    {
        "slug": "request-response",
        "title": "请求与响应链路",
        "source_file": "django/http/request.py, django/http/response.py, django/core/handlers/base.py",
        "source_symbol": "HttpRequest, HttpResponse, BaseHandler",
        "summary": "用可见页面追踪 request、middleware、view 和 response header 的流动。",
        "reading_order": 2,
        "lessons": [
            {
                "slug": "request-object",
                "title": "HttpRequest 从哪里来",
                "summary": "从 WSGIRequest 到 view 参数，理解 request 的数据结构。",
                "explanation": "浏览器请求先被 WSGIHandler 包装成 WSGIRequest。它继承 HttpRequest，并把 environ 转成 path、GET、headers、COOKIES 等属性。",
                "source_file": "django/core/handlers/wsgi.py, django/http/request.py",
                "source_symbol": "WSGIRequest, HttpRequest",
                "reading_order": 1,
                "steps": [
                    {
                        "slug": "inspect-request-echo",
                        "title": "用 Request Echo 对照 HttpRequest",
                        "body": "Request Echo 页面直接返回 request 的 method、path、query、headers 和 middleware 标记。",
                        "action": "打开 /request-echo/?chapter=http&chapter=orm，对照 django/http/request.py。",
                        "checkpoint": "你能说明 GET 为什么是 QueryDict，以及 getlist() 和 get() 的差异。",
                        "source_file": "learning/views.py, django/http/request.py",
                        "source_symbol": "request_echo(), QueryDict",
                        "order": 1,
                        "exercises": [
                            {
                                "slug": "inspect-request-echo",
                                "title": "Inspect Request Echo",
                                "prompt": "打开 /request-echo/?chapter=http&chapter=orm，解释 JSON 中 query 的结构。",
                                "source_hint": "learning/views.py:request_echo, django/http/request.py:QueryDict",
                                "difficulty": "easy",
                            }
                        ],
                    },
                    {
                        "slug": "follow-middleware",
                        "title": "跟踪 middleware 如何修改 request/response",
                        "body": "SourceLensHeaderMiddleware 在调用下游 view 前给 request 加标记，view 返回后给 response 加 header。",
                        "action": "打开 learning/middleware.py，再到 django/core/handlers/base.py 看 load_middleware()。",
                        "checkpoint": "你能画出 request 进入 middleware 和 response 返回 middleware 的顺序。",
                        "source_file": "learning/middleware.py, django/core/handlers/base.py",
                        "source_symbol": "SourceLensHeaderMiddleware, BaseHandler.load_middleware",
                        "order": 2,
                        "exercises": [
                            {
                                "slug": "middleware-header",
                                "title": "Follow middleware header flow",
                                "prompt": "找出 X-Source-Lens 是在哪里加上的，并解释为什么 curl -I 能看到它。",
                                "source_hint": "learning/middleware.py, django/core/handlers/base.py",
                                "difficulty": "medium",
                            }
                        ],
                    },
                ],
            }
        ],
    },
    {
        "slug": "urls-and-views",
        "title": "URL 解析与 View 调度",
        "source_file": "django/urls/conf.py, django/urls/resolvers.py, django/views/generic/base.py",
        "source_symbol": "path(), URLResolver, View.as_view()",
        "summary": "理解 URLPattern 如何匹配路径，以及 class-based view 如何变成可调用函数。",
        "reading_order": 3,
        "lessons": [
            {
                "slug": "url-patterns",
                "title": "path() 创建了什么对象",
                "summary": "把 urlpatterns 和 URLResolver.resolve() 串起来。",
                "explanation": "path() 不是注册全局路由，而是创建 URLPattern/URLResolver 对象。请求到来时 resolver 递归匹配这些对象。",
                "source_file": "django/urls/conf.py, django/urls/resolvers.py",
                "source_symbol": "path(), URLResolver.resolve()",
                "reading_order": 1,
                "steps": [
                    {
                        "slug": "reverse-detail-url",
                        "title": "用 reverse() 反查 URL",
                        "body": "get_absolute_url() 和 redirect() 最终都依赖 URL name 反查真实路径。",
                        "action": "在 shell 中调用 reverse('learning:project-detail', kwargs={'slug': 'url-resolver-lab'})。",
                        "checkpoint": "你能说明 app_name 和 namespace 为什么会影响 reverse()。",
                        "source_file": "django/urls/base.py, learning/models.py",
                        "source_symbol": "reverse(), MiniProject.get_absolute_url()",
                        "order": 1,
                        "exercises": [
                            {
                                "slug": "reverse-detail-url",
                                "title": "Reverse an exercise URL",
                                "prompt": "用 reverse() 生成 URL Resolver Lab 的详情页路径。",
                                "source_hint": "django/urls/base.py:reverse",
                                "difficulty": "easy",
                            }
                        ],
                    },
                    {
                        "slug": "detail-view-dispatch",
                        "title": "读 class-based view 调度",
                        "body": "TopicDetailView.as_view() 返回一个普通函数，这个函数实例化 view，再调用 dispatch()。",
                        "action": "从 learning.views.TopicDetailView 追到 django.views.generic.base.View.as_view()。",
                        "checkpoint": "你能解释为什么 URLconf 中写的是 TopicDetailView.as_view() 而不是 TopicDetailView()。",
                        "source_file": "django/views/generic/base.py",
                        "source_symbol": "View.as_view(), View.dispatch()",
                        "order": 2,
                        "exercises": [
                            {
                                "slug": "detail-view-dispatch",
                                "title": "Read class-based view dispatch",
                                "prompt": "跟踪 TopicDetailView.as_view() 返回的函数如何调用 dispatch()。",
                                "source_hint": "django/views/generic/base.py:View.as_view",
                                "difficulty": "medium",
                            }
                        ],
                    },
                ],
            }
        ],
    },
    {
        "slug": "orm-querysets",
        "title": "ORM 与 QuerySet",
        "source_file": "django/db/models/base.py, django/db/models/query.py, django/db/models/sql/compiler.py",
        "source_symbol": "ModelBase, QuerySet, SQLCompiler",
        "summary": "用模型、shell 和 SQL 输出理解 Django ORM 如何从 Python 对象走到 SQL。",
        "reading_order": 4,
        "lessons": [
            {
                "slug": "model-and-queryset",
                "title": "Model 元信息与 QuerySet 懒执行",
                "summary": "解释 _meta、Manager、QuerySet、SQLCompiler 之间的关系。",
                "explanation": "ModelBase 在类创建时收集字段并构造 _meta。Manager 负责生成 QuerySet。QuerySet 大多数操作只复制 query 对象，直到迭代或取值才执行 SQL。",
                "source_file": "django/db/models/base.py, django/db/models/query.py",
                "source_symbol": "ModelBase, QuerySet._fetch_all",
                "reading_order": 1,
                "steps": [
                    {
                        "slug": "inspect-model-meta",
                        "title": "检查 model._meta",
                        "body": "_meta 保存字段、表名、ordering、manager 等模型元信息。",
                        "action": "在 shell 中运行 Topic._meta.fields、Topic._meta.db_table、Topic._meta.default_manager。",
                        "checkpoint": "你能把 _meta 中的字段和 models.py 中的字段定义对应起来。",
                        "source_file": "django/db/models/base.py, django/db/models/options.py",
                        "source_symbol": "ModelBase, Options",
                        "order": 1,
                        "exercises": [
                            {
                                "slug": "model-meta",
                                "title": "Inspect model _meta",
                                "prompt": "检查 Topic._meta.fields，并说明这些字段何时注册到模型类。",
                                "source_hint": "django/db/models/base.py:ModelBase",
                                "difficulty": "hard",
                            }
                        ],
                    },
                    {
                        "slug": "prove-queryset-laziness",
                        "title": "证明 QuerySet 是懒执行",
                        "body": "filter() 返回新 QuerySet，但不会立刻查询数据库。list()、len()、bool() 会触发 _fetch_all()。",
                        "action": "在 shell 中创建 qs = Exercise.objects.filter(...), 再观察 list(qs) 前后的 qs._result_cache。",
                        "checkpoint": "你能指出 filter()、_chain()、_fetch_all() 分别负责什么。",
                        "source_file": "django/db/models/query.py",
                        "source_symbol": "QuerySet.filter(), QuerySet._fetch_all",
                        "order": 2,
                        "exercises": [
                            {
                                "slug": "queryset-laziness",
                                "title": "Prove QuerySet laziness",
                                "prompt": "创建 QuerySet，分别用 list()、len()、bool() 触发执行并记录结果。",
                                "source_hint": "django/db/models/query.py:QuerySet._fetch_all",
                                "difficulty": "medium",
                            }
                        ],
                    },
                ],
            }
        ],
    },
]


MINI_PROJECTS = [
    {
        "slug": "request-lab",
        "topic_slug": "request-response",
        "title": "Request Lab",
        "summary": "通过一个可观察的请求回显页面理解 HttpRequest、headers、cookies 和 response header。",
        "objective": "你将修改 query string、观察 request.GET/getlist()、确认 middleware 对 request 和 response 的影响。",
        "source_file": "learning/views.py, learning/middleware.py, django/http/request.py",
        "source_symbol": "request_echo(), HttpRequest, HttpResponse",
        "reading_order": 1,
        "tasks": [
            {
                "slug": "querydict-observation",
                "title": "观察 QueryDict 多值参数",
                "prompt": "访问 /request-echo/?chapter=http&chapter=orm，解释 chapter 为什么是列表。",
                "source_hint": "django/http/request.py:QueryDict",
                "next_action": "在浏览器改 query string，然后刷新项目页记录你的观察。",
                "order": 1,
            },
            {
                "slug": "middleware-response-header",
                "title": "确认 middleware 添加响应头",
                "prompt": "用 curl -I / 查看 X-Source-Lens 是否存在。",
                "source_hint": "learning/middleware.py:SourceLensHeaderMiddleware",
                "next_action": "打开 BaseHandler.load_middleware()，解释 response 为什么会反向经过 middleware。",
                "order": 2,
            },
            {
                "slug": "request-cookies",
                "title": "定位 cookies 解析入口",
                "prompt": "阅读 WSGIRequest.COOKIES，找出 parse_cookie() 的调用位置。",
                "source_hint": "django/core/handlers/wsgi.py:WSGIRequest.COOKIES",
                "next_action": "用浏览器开发者工具加一个 cookie，再观察 request echo。",
                "order": 3,
            },
        ],
    },
    {
        "slug": "url-resolver-lab",
        "topic_slug": "urls-and-views",
        "title": "URL Resolver Lab",
        "summary": "通过命名 URL、converter 和 class-based view 理解 URLResolver 的匹配和反查。",
        "objective": "你将从 urlpatterns 追踪到 URLResolver.resolve()，再用 reverse() 反向生成路径。",
        "source_file": "learning/urls.py, django/urls/conf.py, django/urls/resolvers.py",
        "source_symbol": "path(), URLResolver.resolve(), reverse()",
        "reading_order": 2,
        "tasks": [
            {
                "slug": "read-urlpatterns",
                "title": "列出 learning.urls 中的 URLPattern",
                "prompt": "打开 learning/urls.py，写出每个 path() 的 route、view 和 name。",
                "source_hint": "learning/urls.py",
                "next_action": "把其中一个 name 输入 reverse()，确认输出路径。",
                "order": 1,
            },
            {
                "slug": "converter-match",
                "title": "理解 slug converter",
                "prompt": "追踪 topics/<slug:slug>/ 为什么能把路径片段传给 TopicDetailView。",
                "source_hint": "django/urls/resolvers.py:RoutePattern.match",
                "next_action": "打开一个不存在的 slug，观察 404 发生在哪个 resolver 阶段。",
                "order": 2,
            },
            {
                "slug": "cbv-as-view",
                "title": "解释 as_view() 返回值",
                "prompt": "说明 TopicDetailView.as_view() 为什么返回可调用对象。",
                "source_hint": "django/views/generic/base.py:View.as_view",
                "next_action": "在 shell 中打印 TopicDetailView.as_view().__dict__。",
                "order": 3,
            },
        ],
    },
    {
        "slug": "orm-query-lab",
        "topic_slug": "orm-querysets",
        "title": "ORM Query Lab",
        "summary": "用 shell 和页面任务理解 ModelBase、_meta、QuerySet 和 SQLCompiler。",
        "objective": "你将观察模型元数据、QuerySet 缓存、SQL 字符串和用户进度模型。",
        "source_file": "learning/models.py, django/db/models/query.py, django/db/models/sql/compiler.py",
        "source_symbol": "ModelBase, QuerySet, SQLCompiler.execute_sql",
        "reading_order": 3,
        "tasks": [
            {
                "slug": "meta-fields",
                "title": "查看 Topic._meta.fields",
                "prompt": "在 shell 中列出 Topic._meta.fields 的 name 和 class。",
                "source_hint": "django/db/models/base.py:ModelBase",
                "next_action": "回到 models.py，对照每个字段的定义。",
                "order": 1,
            },
            {
                "slug": "queryset-cache",
                "title": "观察 QuerySet _result_cache",
                "prompt": "创建 Exercise.objects.all()，在 list(qs) 前后打印 qs._result_cache。",
                "source_hint": "django/db/models/query.py:QuerySet._fetch_all",
                "next_action": "继续调用 len(qs)，判断是否再次查询。",
                "order": 2,
            },
            {
                "slug": "print-sql",
                "title": "打印 QuerySet SQL",
                "prompt": "运行 str(Exercise.objects.filter(topic__slug='orm-querysets').query)。",
                "source_hint": "django/db/models/sql/compiler.py:SQLCompiler.as_sql",
                "next_action": "找出 WHERE 条件如何对应 filter() 参数。",
                "order": 3,
            },
        ],
    },
]
