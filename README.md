# DiachronicVec

DiachronicVec 是一个用于构建、对齐并分析西方哲学历时语料词向量的项目。通过该项目可以从不同历史时期的文本中学习 Word2Vec 模型、将它们对齐到统一空间，并开展语义漂移等分析与可视化。

## 目录结构

```
DiachronicVec/
├── processed_corpus/                # 预处理后的西哲史分词语料（JSON）
├── models/
│   ├── word2vec/                   # 未对齐的 Word2Vec 模型
│   └── word_vectors_aligned/       # 对齐后的 KeyedVectors
├── scripts/
│   ├── train_models.py             # 训练各时期 Word2Vec 模型
│   ├── align_models.py             # 正交 Procrustes 对齐脚本
│   └── analyze_semantics.py        # 历时分析与可视化
├── results/                        # 分析生成的图表与输出
└── README.md
```

## 环境与依赖

建议使用 Python 3.10+ 并创建虚拟环境：

```bash
pip install gensim numpy matplotlib pandas
```



## 使用说明

### 1. 训练方言/时期词向量

`scripts/train_models.py` 会读取 `processed_corpus/` 目录下的 JSON 句子列表，分别训练 `ancient`、`medieval`、`modern`、`contemporary` 四个 Word2Vec 模型，并保存到 `models/word2vec/`。

```bash
cd scripts
python train_models.py
```

### 2. 对齐词向量空间

`scripts/align_models.py` 使用正交 Procrustes 方法，以 `modern` 模型为枢纽，将其他三个时期的 KeyedVectors 对齐到统一空间，输出到 `models/word_vectors_aligned/`。

```bash
python align_models.py
```

### 3. 语义分析与可视化

`scripts/analyze_semantics.py` 提供以下功能：

- `plot_macro_drift`：绘制多个概念相对基准时期的语义漂移折线图。
- `get_neighbor_evolution_table`：生成各时期 Top-N 近邻变化表。
- `plot_jaccard_similarity`：展示临近时期 Top-N 近邻集合的 Jaccard 相似度。
- `find_top_drifters`：列出语义变化幅度最大的词汇。

执行脚本会自动调用上述分析并输出结果：

```bash
python analyze_semantics.py
```

运行后，`results/` 目录将包含：

- `macro_drift.png`：目标词与稳定词的整体漂移趋势。
- `<word>_jaccard.png`：每个目标词在相邻时期的邻居重叠度柱状图。
- 终端输出：每个词的近邻演化表（`pandas.DataFrame`）及最显著的语义漂移词列表。






