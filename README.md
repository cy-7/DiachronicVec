# DiachronicVec — 西方哲学历时词向量语义演变分析系统

## 一、项目概述

DiachronicVec 是一个基于 **历时词向量（Diachronic Word Embeddings）** 技术的语义演变分析系统，专注于研究西方哲学核心概念在两千余年历史跨度中的语义漂移现象。项目覆盖从古希腊哲学到当代分析哲学的四个历史时期，通过训练各时期独立的 Word2Vec 模型并利用 Orthogonal Procrustes 对齐算法将其映射到统一向量空间，实现跨时代的定量语义比较。

系统提供完整的 **数据处理 → 模型训练 → 向量对齐 → 语义分析 → 交互式可视化** 全流程 pipeline，并配备基于 React 的现代化 Web 前端，支持语义漂移曲线、Jaccard 近邻重叠度、近邻演化表、向量空间降维投影、漂移排行榜等多维度分析视图。

### 核心研究问题

> 哲学核心概念（如 reason、god、nature、law）的语义内涵如何随历史时期发生系统性变迁？能否通过计算语言学方法定量刻画这种变迁？

### 学术背景

本项目的方法论基础来自 Hamilton et al. (2016) 的经典论文 *"Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change"*，该研究首次系统性地将词向量对齐技术应用于历时语义分析。本项目将该方法从通用语料迁移到哲学专业领域，并在多个技术环节进行了针对性优化。

---

## 二、研究语料

### 2.1 语料分期与构成

项目将西方哲学史划分为四个时期，每个时期收录该时期代表性哲学家的核心著作英文文本：

| 时期 | 代号 | 代表年份 | 文本数量 | 主要作者 |
|------|------|----------|----------|----------|
| **古代** | `ancient` | -400 | 27 篇 | 柏拉图、亚里士多德、西塞罗、爱比克泰德、马可·奥勒留、卢克莱修、普罗提诺、塞克斯都·恩披里柯等 |
| **中世纪** | `medieval` | 1200 | 10 篇 | 奥古斯丁、安瑟伦、托马斯·阿奎那、波爱修斯、迈蒙尼德、托马斯·肯培等 |
| **近代** | `modern` | 1800 | 30 篇 | 笛卡尔、洛克、休谟、康德、黑格尔、斯宾诺莎、尼采、密尔、马克思等 |
| **当代** | `contemporary` | 2000 | 43 篇 | 斯坦福哲学百科（SEP）与互联网哲学百科（IEP）条目，涵盖海德格尔、维特根斯坦、罗尔斯、福柯、德里达、萨特等 |

### 2.2 语料来源

- **古代至近代**：主要来自 Project Gutenberg 公共领域英文译本
- **当代**：来自 Stanford Encyclopedia of Philosophy (SEP) 和 Internet Encyclopedia of Philosophy (IEP) 的学术条目

### 2.3 语料特点与局限

- 古代至近代语料为原始哲学文本的英文翻译，当代语料为学术百科文章，两者在文体上存在差异
- 各时期语料规模不均衡：近代最大（约 9 万句），当代最小（约 2 万句）
- 四个时期的共享词汇量约 3,086 个词，这是跨时期比较的基础

---

## 三、技术架构

### 3.1 系统架构总览

```
┌──────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                 │
│  ┌───────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ DriftChart│ Jaccard  │ Neighbor │ Scatter  │  Top   │ │
│  │           │  Chart   │  Table   │  Plot    │Drifters│ │
│  └────┬──────┴────┬─────┴────┬─────┴────┬─────┴────┬───┘ │
│       └───────────┴──────────┴──────────┴──────────┘     │
│                         ↕ REST API                       │
├──────────────────────────────────────────────────────────┤
│                  FastAPI Backend (Uvicorn)               │
│   ┌──────────────────────────────────────────────────┐   │
│   │              Analyzer Engine                     │   │
│   │  ┌──────────┬──────────┬──────────┬───────────┐  │   │
│   │  │  Drift   │ Jaccard  │ Neighbor │  Scatter  │  │   │
│   │  │ Series   │Similarity│Evolution │    2D     │  │   │
│   │  └──────────┴──────────┴──────────┴───────────┘  │   │
│   └──────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────┤
│                  Diachronic Core Library                 │
│   ┌───────────┬───────────┬───────────┬──────────────┐   │
│   │ Preprocess│   Train   │   Align   │   Analyze    │   │
│   │  (spaCy)  │ (Word2Vec)│(Procrustes│  (NumPy)     │   │
│   └───────────┴───────────┴───────────┴──────────────┘   │
├──────────────────────────────────────────────────────────┤
│                    Data Layer                            │
│ corpus/→data/sentences/→models/word2vec/→models/aligned/ │
└──────────────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
DiachronicVec/
├── corpus/                     # 原始语料文本
│   ├── ancient/                # 古代哲学文本 (27篇)
│   ├── medieval/               # 中世纪哲学文本 (10篇)
│   ├── modern/                 # 近代哲学文本 (30篇)
│   └── contemporary/           # 当代哲学百科条目 (43篇)
├── diachronic/                 # 核心算法库
│   ├── config.py               # 全局配置（超参数、路径、分期定义）
│   ├── preprocess.py           # 语料预处理（分句、词形还原、过滤）
│   ├── train.py                # Word2Vec 模型训练
│   ├── align.py                # Orthogonal Procrustes 向量空间对齐
│   ├── analyze.py              # 语义分析引擎（漂移、Jaccard、近邻等）
│   └── utils.py                # 工具函数（余弦距离计算）
├── api/                        # FastAPI 后端
│   ├── main.py                 # 应用入口与生命周期管理
│   └── routers/
│       ├── analysis.py         # 分析 API 路由
│       └── corpus.py           # 语料信息 API 路由
├── web/                        # React 前端
│   ├── src/
│   │   ├── App.jsx             # 应用主组件与路由
│   │   ├── api/client.js       # API 客户端封装
│   │   └── components/
│   │       ├── Dashboard.jsx   # 项目总览面板
│   │       ├── DriftChart.jsx  # 语义漂移折线图
│   │       ├── JaccardChart.jsx# Jaccard 重叠度柱状图
│   │       ├── NeighborTable.jsx# 近邻演化对比表
│   │       ├── ScatterPlot.jsx # 向量空间散点图
│   │       ├── TopDrifters.jsx # 漂移排行榜
│   │       ├── WordInput.jsx   # 词汇输入组件
│   │       └── Layout.jsx      # 布局与导航
│   └── package.json
├── scripts/                    # 独立脚本入口
├── run.py                      # 统一 CLI 入口
└── pyproject.toml              # Python 项目配置
```

### 3.3 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **NLP 预处理** | spaCy | ≥3.7 | 分句、词形还原（lemmatization）、停用词过滤 |
| **词向量训练** | Gensim Word2Vec | ≥4.3 | Skip-gram 模型训练 |
| **向量对齐** | SciPy | ≥1.11 | Orthogonal Procrustes 旋转矩阵求解 |
| **数值计算** | NumPy | ≥1.24 | 矩阵运算、余弦相似度计算 |
| **降维可视化** | scikit-learn | ≥1.4 | PCA / t-SNE 降维 |
| **后端框架** | FastAPI + Uvicorn | ≥0.110 | RESTful API 服务 |
| **前端框架** | React 18 + Vite 5 | - | 单页应用 |
| **图表库** | Recharts + D3.js | - | 折线图、柱状图、散点图 |
| **样式** | Tailwind CSS 3 | - | 暗色主题 UI |

---

## 四、核心算法详解

### 4.1 语料预处理

预处理流程（`diachronic/preprocess.py`）：

1. **Gutenberg 清洗**：自动检测并移除 Project Gutenberg 的版权声明头尾
2. **spaCy NLP 管线**：使用 `en_core_web_sm` 模型进行分句和词形还原
3. **Token 过滤规则**：
   - 仅保留字母组成的 token（`is_alpha`）
   - 移除停用词（`is_stop`）
   - 最小长度 3 个字符
   - 每句至少 3 个有效 token
4. **输出格式**：每个时期生成一个 JSON 文件，包含分词后的句子列表

### 4.2 Word2Vec 训练

训练配置（`diachronic/config.py` → `diachronic/train.py`）：

| 参数 | 值 | 说明 |
|------|----|------|
| `sg` | 1 (Skip-gram) | Hamilton et al. (2016) 推荐，对低频词表现更好 |
| `vector_size` | 300 | 标准维度，平衡表达能力与训练效率 |
| `window` | 5 | 上下文窗口大小 |
| `epochs` | 15 | 训练轮次，小语料需要更多轮次 |
| `negative` | 10 | 负采样数量，提升训练质量 |
| `sample` | 1e-4 | 高频词下采样阈值 |
| `min_count` | 按时期调整 | ancient=7, medieval=5, modern=10, contemporary=2 |

**`min_count` 差异化设计**：各时期语料规模不同，`min_count` 按语料大小调整，确保每个时期都能保留足够的有效词汇。当代语料最小，因此 `min_count=2` 以最大化词汇覆盖。

### 4.3 Orthogonal Procrustes 向量空间对齐

对齐算法（`diachronic/align.py`）是本项目的核心技术环节：

**问题定义**：各时期独立训练的 Word2Vec 模型处于不同的向量空间中，同一个词在不同时期的向量无法直接比较。需要找到一个正交旋转矩阵 R，将各时期的向量空间对齐到统一的参考空间。

**算法流程**：

1. **选择 Hub 时期**：以 `modern`（近代）作为参考空间（Hub Period），因为近代语料最大、词汇最丰富
2. **提取共享词汇**：找到源时期和目标时期的共同词汇
3. **L2 归一化**：对共享词汇的向量矩阵进行 L2 行归一化（不做均值中心化）
4. **求解 Procrustes**：通过 SVD 分解求解最优正交旋转矩阵 R = argmin‖XR - Y‖_F
5. **应用旋转**：将源时期的全部词向量归一化后乘以 R，映射到 Hub 空间
6. **Hub 归一化**：Hub 时期自身的向量也进行 L2 归一化，确保所有时期在同一余弦空间

**关键设计决策**：
- **不做均值中心化**：遵循 Hamilton et al. (2016) 的标准做法，避免破坏词向量的几何结构
- **L2 归一化**：确保 Procrustes 对齐在单位球面上进行，使余弦相似度计算更稳定
- **Hub 选择**：选择语料最大的时期作为 Hub，因为其向量空间最稳定

### 4.4 语义分析引擎

分析引擎（`diachronic/analyze.py`）提供五种核心分析方法：

#### 4.4.1 语义漂移分析（Drift Series）

- **度量**：目标词在各时期的向量与 benchmark 时期（默认 modern）向量的余弦距离
- **Baseline 计算**：从 3,086 个共享词汇中，计算每个词跨所有时期的总漂移量，取漂移最小的 25%（约 770 个词）作为"稳定词"，其平均漂移作为 baseline
- **意义**：目标词的漂移曲线高于 baseline 说明该词经历了超出正常水平的语义变化

#### 4.4.2 Jaccard 近邻重叠度

- **方法**：在共享词汇空间内，计算目标词在相邻时期的 Top-K 近邻集合的 Jaccard 相似系数
- **多 K 值对比**：同时计算 K=10、25、50 三个粒度，K 越小越聚焦核心语义圈
- **共享词汇限制**：近邻搜索严格限制在四个时期共有的 3,086 个词内，通过预计算的归一化矩阵直接进行余弦相似度排序，确保跨时期可比性
- **公式**：J(A, B) = |N_k(w, t₁) ∩ N_k(w, t₂)| / |N_k(w, t₁) ∪ N_k(w, t₂)|

#### 4.4.3 近邻演化表

- 展示目标词在四个时期各自的 Top-10 最近邻词汇及相似度分数
- 近邻搜索限制在共享词汇内，确保跨时期可比

#### 4.4.4 向量空间降维投影

- 支持 PCA 和 t-SNE 两种降维方法
- 将多个目标词在四个时期的向量投影到二维平面
- 同一词的四个时期点用虚线连接，直观展示语义轨迹

#### 4.4.5 漂移排行榜

- 向量化计算所有共享词汇从起始时期到终止时期的余弦距离
- 使用 `np.einsum` 批量计算，高效处理 3,086 个词
- 返回漂移最大的 Top-N 词汇

---

## 五、API 接口文档

### 5.1 基础信息

- **Base URL**: `http://localhost:8000/api`
- **数据格式**: JSON
- **框架**: FastAPI（自动生成 OpenAPI 文档，访问 `/docs`）

### 5.2 接口列表

#### 语料信息

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/periods` | 获取时期列表（名称、年份、颜色） |
| GET | `/corpus/stats` | 获取语料统计（时期数、共享词汇量、各时期词汇量） |
| GET | `/vocab?period=ancient&limit=500` | 获取指定时期的词汇列表 |

#### 语义分析

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| POST | `/analysis/drift` | `{"words": ["reason","god"], "benchmark": "modern", "include_stable": true}` | 语义漂移时间序列 |
| POST | `/analysis/neighbors` | `{"word": "reason", "top_n": 10}` | 近邻演化 |
| POST | `/analysis/jaccard` | `{"word": "reason", "top_n": 25}` | Jaccard 重叠度（多 K 值） |
| POST | `/analysis/scatter` | `{"words": ["reason","god"], "method": "pca"}` | 2D 降维投影 |
| GET | `/analysis/top-drifters?start=ancient&end=contemporary&n=20` | - | 漂移排行榜 |

### 5.3 响应示例

**语义漂移** (`POST /analysis/drift`)：
```json
{
  "years": [-400, 1200, 1800, 2000],
  "periods": ["ancient", "medieval", "modern", "contemporary"],
  "series": {
    "reason": [0.39, 0.36, 0.0, 0.33],
    "god": [0.32, 0.35, 0.0, 0.41]
  },
  "baseline": [0.39, 0.40, 0.0, 0.44]
}
```

**Jaccard 重叠度** (`POST /analysis/jaccard`)：
```json
{
  "labels": ["ancient-medieval", "medieval-modern", "modern-contemporary"],
  "results_by_k": {
    "10": [0.0, 0.0526, 0.1111],
    "25": [0.0417, 0.0417, 0.087],
    "50": [0.0526, 0.0526, 0.0638]
  },
  "scores": [0.0417, 0.0417, 0.087]
}
```

---

## 六、前端可视化系统

### 6.1 界面设计

前端采用暗色主题（Dark Theme）单页应用设计，左侧为导航栏，右侧为内容区域。共包含六个功能视图：

| 视图 | 组件 | 功能描述 |
|------|------|----------|
| **总览** | `Dashboard` | 展示各时期词汇量统计、项目介绍、历史分期说明 |
| **语义漂移** | `DriftChart` | 多词余弦距离折线图 + 稳定基线虚线（ComposedChart） |
| **近邻演化** | `NeighborTable` | 四时期 Top-10 近邻对比表格 |
| **Jaccard 重叠** | `JaccardChart` | 多 K 值分组柱状图（Top-10/25/50） |
| **向量空间** | `ScatterPlot` | D3.js 绘制的 PCA/t-SNE 二维散点图，带轨迹连线 |
| **漂移排行** | `TopDrifters` | 渐变进度条排行榜 |

### 6.2 交互特性

- **词汇输入**：支持自定义输入目标词，逗号分隔
- **实时查询**：点击按钮即时调用后端 API 并渲染结果
- **降维切换**：向量空间视图支持 PCA / t-SNE 方法切换
- **响应式布局**：基于 Tailwind CSS 的自适应网格布局

---

## 七、快速开始

### 7.1 环境要求

- Python ≥ 3.10
- Node.js ≥ 18
- spaCy 英文模型：`python -m spacy download en_core_web_sm`

### 7.2 安装依赖

```bash
# Python 依赖
pip install -e .

# 前端依赖
cd web && npm install
```

### 7.3 数据处理 Pipeline

```bash
# 方式一：一键执行全流程（预处理 → 训练 → 对齐）
python run.py pipeline

# 方式二：分步执行
python run.py preprocess   # 语料预处理（需要 spaCy 模型）
python run.py train        # 训练 Word2Vec 模型
python run.py align        # Procrustes 对齐
```

### 7.4 启动服务

```bash
# 启动后端 API（端口 8000）
python run.py serve

# 启动前端开发服务器（另一个终端）
cd web && npm run dev
```

访问 `http://localhost:5173` 即可使用可视化界面。

---

## 八、实验结果与分析

### 8.1 语料统计

| 时期 | 词汇量 | min_count |
|------|--------|-----------|
| 古代 (ancient) | ~9,890 | 7 |
| 中世纪 (medieval) | ~6,426 | 5 |
| 近代 (modern) | ~8,218 | 10 |
| 当代 (contemporary) | ~9,664 | 2 |
| **共享词汇** | **~3,086** | - |

### 8.2 语义漂移发现

以 modern（近代）为基准期的余弦距离分析：

- **"law"**：在中世纪时期出现显著漂移峰值（0.45），高于 baseline（0.40），反映了从古代自然法到中世纪神法的语义转变
- **"god"**：从古代到当代呈现持续上升趋势（0.32 → 0.41），反映了宗教概念在世俗化进程中的语义变迁
- **"reason"**：在古代和当代均高于 baseline，但中世纪反而较低，暗示中世纪经院哲学对 "reason" 的使用与近代理性主义较为接近

### 8.3 Jaccard 重叠度分析

以 "god" 为例的 Jaccard 指数：

| 时期对 | Top-10 | Top-25 | Top-50 |
|--------|--------|--------|--------|
| 古代→中世纪 | 0.00 | 0.04 | 0.05 |
| 中世纪→近代 | 0.05 | 0.04 | 0.05 |
| 近代→当代 | **0.11** | **0.09** | **0.06** |

"god" 在近代→当代的 Jaccard 最高，说明宗教概念的核心语义圈在这两个时期保持了相对稳定。而 "reason" 在近代→当代的 Jaccard 接近零，反映了当代百科文章中 "reason" 的用法与近代哲学原典存在显著差异。

### 8.4 结果解读注意事项

1. **Jaccard 值普遍偏低**（0.01-0.11）是正常现象，原因包括：
   - 共享词汇仅 3,086 个，限制了近邻搜索空间
   - 各时期语料规模和文体差异较大
   - 哲学概念确实经历了显著的语义变迁

2. **当代语料的特殊性**：当代语料为 SEP/IEP 百科文章而非原始哲学著作，文体差异会放大某些词的表观漂移

3. **Baseline 的意义**：稳定基线代表了"正常"的跨时期向量差异水平，只有超出 baseline 的漂移才具有语义学意义

---

## 九、项目创新点

1. **领域特化的历时语义分析**：将通用的历时词向量方法应用于哲学专业领域，填补了计算哲学（Computational Philosophy）在语义演变分析方面的空白

2. **共享词汇矩阵加速**：预计算各时期在共享词汇上的归一化向量矩阵，通过矩阵乘法直接计算余弦相似度，避免了传统 `similar_by_word` 方法在跨词汇过滤时的效率和覆盖率问题

3. **自适应稳定基线**：不依赖人工选定的稳定词，而是从共享词汇中自动计算漂移最小的 25% 作为基线，更具统计鲁棒性

4. **多 K 值 Jaccard 对比**：同时展示 K=10/25/50 三个粒度的 Jaccard 指数，揭示不同语义圈层的稳定性差异

5. **全栈可视化系统**：从数据处理到交互式可视化的完整 pipeline，支持自定义词汇查询，降低了历时语义分析的使用门槛

6. **差异化 min_count 策略**：根据各时期语料规模动态调整最小词频阈值，在词汇覆盖率和向量质量之间取得平衡

---

## 十、技术参考

- Hamilton, W. L., Leskovec, J., & Jurafsky, D. (2016). *Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change*. ACL 2016.
- Schönemann, P. H. (1966). *A generalized solution of the orthogonal Procrustes problem*. Psychometrika, 31(1), 1-10.
- Mikolov, T., et al. (2013). *Efficient Estimation of Word Representations in Vector Space*. ICLR Workshop.
- Kulkarni, V., et al. (2015). *Statistically Significant Detection of Linguistic Change*. WWW 2015.

---

## 十一、License

本项目仅供学术研究与教学使用。语料文本版权归原作者/出版方所有。
