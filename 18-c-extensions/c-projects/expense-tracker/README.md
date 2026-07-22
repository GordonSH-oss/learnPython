# 个人记账系统

## 学习目标

- 使用 `int64_t` 的“分”表示金额，避免二进制浮点累计误差
- 建模收入和支出
- 实现余额与分类支出汇总
- 用 CSV 保存记录并处理解析失败

## 运行

```bash
make test
./build/expense-tracker ledger.csv add 1 2026-07-01 income 10000 salary monthly
./build/expense-tracker ledger.csv add 2 2026-07-02 expense 35.50 food lunch
./build/expense-tracker ledger.csv list
./build/expense-tracker ledger.csv summary
./build/expense-tracker ledger.csv summary food
```

CSV 示例：

```text
1,2026-07-01,income,1000000,salary,monthly
```

金额在文件中保存为整数分。教学版不支持 category/note 中的逗号；生产 CSV 应使用完整转义规则或成熟解析库。

## 扩展练习

1. 支持 `+100.00`、货币代码和不同小数位规则。
2. 增加按月份汇总。
3. 增加预算和“超出预算”检测。
4. 支持标准 CSV 引号和逗号转义。
5. 为余额累计溢出构造自动测试。
