# 文本分析器

## 学习目标

- 逐字符流式读取文件，不把全文加载进内存
- 使用开放寻址哈希表统计词频
- 在负载因子达到 70% 前扩容并重新散列
- 生成行数、词数、字节数、唯一词数和 Top N

## 运行

```bash
make test
./build/text-analyzer README.md
./build/text-analyzer README.md 20
```

单词规则为连续的字母或数字，统一转换为小写。教学版拒绝超过 127 字节的单词，避免静默截断。

## 数据流

```text
FILE*
  -> fgetc
  -> tokenizer
  -> lowercase word
  -> hash table count
  -> frequency array
  -> qsort Top N
```

## 阅读顺序

1. `include/analyzer.h`：公开结果和生命周期。
2. `hash_word`：FNV-1a 风格哈希。
3. `record_word`：冲突探测和扩容。
4. `text_analyzer_process`：流式 tokenizer。
5. `text_analyzer_top`：摘要排序。

## 扩展练习

1. 改为动态单词缓冲区，支持任意长度并检查扩容溢出。
2. 支持停用词文件。
3. 用最小堆实现 Top N，避免排序全部唯一词。
4. 增加 UTF-8 tokenizer，并说明“字节、码点、用户字符”的区别。
5. 比较链地址法和开放寻址的内存局部性。

