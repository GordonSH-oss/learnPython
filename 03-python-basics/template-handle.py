"""
Python f-string、t-string 和 Template 用法教程

运行方式：
    python 03-python-basics/template-handle.py

注意：
    本教程包含 Python 3.14+ 的 t-string 语法：t"...{value}..."。
    如果使用 Python 3.13 或更低版本，解释器会直接报 SyntaxError。

学习目标：
    1. 掌握 f-string 的基本插值、表达式和格式化能力。
    2. 掌握 Python 3.14+ t-string 返回 Template 对象的机制。
    3. 掌握 string.Template 的 substitute() 和 safe_substitute()。
    4. 理解什么时候用 f-string、t-string 和 string.Template。
"""

from __future__ import annotations

from datetime import datetime
from string import Template as DollarTemplate
from string.templatelib import Interpolation, Template as TStringTemplate, convert


LINE = "=" * 72


def title(text: str) -> None:
    print(f"\n{LINE}\n{text}\n{LINE}")


def lesson_1_f_string_basic() -> None:
    title("1. f-string：最常用的字符串插值方式")

    name = "Alice"
    age = 18

    print(f"用户名: {name}")
    print(f"年龄: {age}")
    print(f"明年年龄: {age + 1}")

    print(
        """
说明：
  - f-string 以 f 或 F 开头。
  - 花括号 {} 里可以放变量，也可以放简单表达式。
  - f-string 在代码执行时立即求值。
"""
    )


def lesson_2_f_string_format() -> None:
    title("2. f-string：格式化数字、日期和对齐")

    price = 19.9
    ratio = 0.2567
    count = 42
    now = datetime(2026, 7, 9, 14, 30)

    print(f"价格保留两位小数: {price:.2f}")
    print(f"百分比: {ratio:.1%}")
    print(f"数字左侧补零: {count:04d}")
    print(f"日期格式化: {now:%Y-%m-%d %H:%M}")
    print(f"左对齐: |{'Python':<10}|")
    print(f"右对齐: |{'Python':>10}|")
    print(f"居中:   |{'Python':^10}|")

    print(
        """
常见格式：
  - :.2f   浮点数保留 2 位小数
  - :.1%   按百分比显示，并保留 1 位小数
  - :04d   整数宽度为 4，不够时左侧补 0
  - :%Y-%m-%d  按日期格式输出
  - :<10、:>10、:^10  分别表示左对齐、右对齐、居中
"""
    )


def lesson_3_f_string_debug() -> None:
    title("3. f-string：调试写法")

    user_id = 1001
    status = "active"

    print(f"{user_id=}")
    print(f"{status=}")
    print(f"{user_id + 1=}")

    print(
        """
说明：
  - Python 3.8+ 支持 {变量名=} 这种调试写法。
  - 它会同时打印表达式文本和表达式结果。
  - 适合临时调试，不建议大量留在正式日志里。
"""
    )


def render_t_string(template: TStringTemplate) -> str:
    """把 t-string 的 Template 对象渲染成普通字符串。"""
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, Interpolation):
            value = convert(item.value, item.conversion)
            parts.append(format(value, item.format_spec))
    return "".join(parts)


def lesson_4_t_string_basic() -> None:
    title("4. t-string：Python 3.14+，返回 Template 对象")

    name = "Alice"
    age = 18

    template = t"用户名: {name}，明年年龄: {age + 1}"

    print("对象类型:", type(template))
    print("Template 对象:", template)
    print("静态字符串 parts:", template.strings)
    print("插值对象 parts:", template.interpolations)
    print("插值结果 values:", template.values)
    print("手动渲染结果:", render_t_string(template))

    print(
        """
说明：
  - f"..." 会立即返回 str。
  - t"..." 不直接返回 str，而是返回 string.templatelib.Template。
  - Template 里保留了静态字符串和每个 {...} 插值对象。
  - 这适合做自定义渲染、日志脱敏、SQL/HTML 安全处理等高级场景。
"""
    )


def lesson_5_t_string_interpolation_detail() -> None:
    title("5. t-string：可以读取表达式、转换标记和格式规格")

    name = "Alice"
    score = 95.678

    template = t"用户 {name!r} 的分数是 {score:.1f}"

    for interpolation in template.interpolations:
        print("value:", interpolation.value)
        print("expression:", interpolation.expression)
        print("conversion:", interpolation.conversion)
        print("format_spec:", interpolation.format_spec)
        print("-" * 32)

    print("手动渲染结果:", render_t_string(template))

    print(
        """
说明：
  - interpolation.value 是表达式求值后的结果。
  - interpolation.expression 是花括号里的表达式文本。
  - interpolation.conversion 对应 !s、!r、!a。
  - interpolation.format_spec 对应 :.2f、:^10 这类格式说明。

注意：
  - t-string 会先求值表达式，所以它不是“延迟执行表达式”的模板。
  - 它的价值是让你在字符串真正拼接前，拿到结构化的插值信息。
"""
    )


def lesson_6_template_basic() -> None:
    title("6. string.Template：用 $name 占位，再传数据替换")

    template = DollarTemplate("你好，$name！你的订单号是 $order_id。")
    result = template.substitute(name="Alice", order_id="A-10086")

    print(result)

    print(
        """
说明：
  - Template 来自标准库 string。
  - 占位符写成 $name。
  - substitute() 要求所有占位符都有对应值，否则会报 KeyError。
"""
    )


def lesson_7_template_braces_and_escape() -> None:
    title("7. string.Template：${name} 避免边界歧义，$$ 表示普通 $")

    template = DollarTemplate("文件名: ${prefix}_report.txt，价格: $$${price}")
    result = template.substitute(prefix="sales", price="19.90")

    print(result)

    print(
        """
规则：
  - $prefix_report 会被理解成一个叫 prefix_report 的变量。
  - ${prefix}_report 可以明确告诉 Python：变量名只有 prefix。
  - $$ 用来输出普通的美元符号 $。
"""
    )


def lesson_8_safe_substitute() -> None:
    title("8. safe_substitute：缺少变量时不报错")

    template = DollarTemplate("你好，$name。你的优惠码是 $coupon。")

    try:
        print(template.substitute(name="Alice"))
    except KeyError as error:
        print("substitute() 缺少变量会报错:", error)

    print("safe_substitute() 缺少变量会保留占位符:")
    print(template.safe_substitute(name="Alice"))

    print(
        """
选择：
  - substitute()：模板必须完整渲染，缺字段就报错，适合严格场景。
  - safe_substitute()：允许部分字段暂时缺失，适合预览、草稿、分阶段填充。
"""
    )


def lesson_9_user_template() -> None:
    title("9. 工程场景：用户可配置模板时，string.Template 更合适")

    user_defined_template = DollarTemplate(
        """
亲爱的 $name：

你的会员等级是 $level。
当前积分是 $points。

感谢使用我们的服务。
""".strip()
    )

    data = {
        "name": "Alice",
        "level": "Gold",
        "points": 980,
    }

    print(user_defined_template.substitute(data))

    print(
        """
为什么这里不用 f-string？
  - f-string 是代码的一部分，花括号里会执行 Python 表达式。
  - 如果模板内容来自用户、配置文件、数据库，不应该把它当代码执行。
  - Template 只做简单占位符替换，更适合“用户可编辑模板”。
"""
    )


def lesson_10_choose_between_them() -> None:
    title("10. 怎么选择：f-string、t-string 还是 string.Template")

    print(
        """
优先用 f-string：
  - 模板写死在代码里。
  - 需要表达式、格式化、日期格式、数字格式。
  - 例如日志、错误消息、简单返回文案。

优先用 t-string：
  - 使用 Python 3.14+。
  - 模板写在代码里，但你不想立刻拼成字符串。
  - 需要拿到静态文本、表达式文本、格式规格和值，做自定义处理。
  - 例如安全渲染、日志脱敏、结构化模板分析。

优先用 string.Template：
  - 模板来自配置文件、数据库、用户输入。
  - 只需要简单变量替换。
  - 需要让非开发人员编辑模板。
  - 希望缺字段时能用 safe_substitute() 保留占位符。

一句话：
  - f-string 适合“开发者在代码里直接拼出字符串”。
  - t-string 适合“开发者在代码里写模板，但交给自定义处理器渲染”。
  - string.Template 适合“把外部 $name 模板填上数据”。
"""
    )


def main() -> None:
    lesson_1_f_string_basic()
    lesson_2_f_string_format()
    lesson_3_f_string_debug()
    lesson_4_t_string_basic()
    lesson_5_t_string_interpolation_detail()
    lesson_6_template_basic()
    lesson_7_template_braces_and_escape()
    lesson_8_safe_substitute()
    lesson_9_user_template()
    lesson_10_choose_between_them()


if __name__ == "__main__":
    main()
