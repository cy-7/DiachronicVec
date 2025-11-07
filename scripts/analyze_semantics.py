"""历时词向量分析工具。

提醒：运行前请确保已安装下列依赖库：
    pip install gensim numpy matplotlib pandas
"""

import logging
import os
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors


LOGGER = logging.getLogger(__name__)


def _configure_matplotlib_font() -> None:
    """配置Matplotlib字体以避免中文字符显示为方框。"""

    candidate_fonts = [
        "SimHei",
        "Microsoft YaHei",
        "Microsoft YaHei UI",
        "PingFang SC",
        "PingFang HK",
        "Noto Sans CJK SC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
    ]

    chosen_font = None
    for font_name in candidate_fonts:
        try:
            font_manager.findfont(font_name, fallback_to_default=False)
            chosen_font = font_name
            break
        except ValueError:
            continue

    if chosen_font is not None:
        plt.rcParams["font.sans-serif"] = [chosen_font, "DejaVu Sans", "sans-serif"]
        LOGGER.info("Matplotlib 使用字体：%s", chosen_font)
    else:
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "sans-serif"]
        LOGGER.warning("未找到常见中文字体，图表可能仍显示方框。请安装 SimHei 或 Microsoft YaHei 等字体。")

    plt.rcParams["axes.unicode_minus"] = False


_configure_matplotlib_font()


class DiachronicAnalyzer:
    """针对对齐后的历时词向量进行分析与可视化的工具类。"""

    def __init__(self, models_dir: str) -> None:
        """加载对齐后的词向量模型并准备分析配置。"""

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s - %(message)s",
        )

        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isabs(models_dir):
            resolved_models_dir = models_dir
        else:
            resolved_models_dir = os.path.abspath(os.path.join(script_dir, models_dir))
        self.models_dir = resolved_models_dir
        self.periods: List[str] = ["ancient", "medieval", "modern", "contemporary"]
        self.period_years: Dict[str, int] = {
            "ancient": -400,
            "medieval": 1200,
            "modern": 1800,
            "contemporary": 2000,
        }

        self.models: Dict[str, KeyedVectors] = {}
        for period in self.periods:
            model_path = os.path.join(self.models_dir, f"{period}_aligned.kv")
            if not os.path.isfile(model_path):
                raise FileNotFoundError(f"未找到对齐模型：{model_path}")
            LOGGER.info("加载对齐模型：%s", model_path)
            self.models[period] = KeyedVectors.load(model_path, mmap="r")

        os.makedirs("results", exist_ok=True)

    def _ensure_word_exists(self, word: str) -> None:
        """确认所有时期模型都包含目标词。"""

        missing = [p for p in self.periods if word not in self.models[p]]
        if missing:
            raise KeyError(f"词汇 '{word}' 未在以下时期的模型中出现：{missing}")

    def plot_macro_drift(
        self,
        target_words: Sequence[str],
        benchmark_period: str = "modern",
        save_path: Optional[str] = None,
    ) -> None:
        """绘制目标词相对于基准时期的语义漂移折线图。"""

        if benchmark_period not in self.periods:
            raise ValueError(f"benchmark_period 必须是 {self.periods} 之一")

        years = [self.period_years[p] for p in self.periods]

        plt.figure(figsize=(10, 6))
        for word in target_words:
            self._ensure_word_exists(word)
            benchmark_vector = self.models[benchmark_period][word]

            drift_scores = []
            for period in self.periods:
                period_vector = self.models[period][word]
                cosine_similarity = np.dot(period_vector, benchmark_vector) / (
                    np.linalg.norm(period_vector) * np.linalg.norm(benchmark_vector)
                )
                cosine_distance = 1 - cosine_similarity
                drift_scores.append(cosine_distance)

            plt.plot(years, drift_scores, marker="o", label=word)

        plt.title("语义漂移趋势 (相对现代时期)")
        plt.xlabel("年份")
        plt.ylabel("余弦距离")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()

        if save_path is not None:
            plt.tight_layout()
            plt.savefig(save_path, dpi=300)
            LOGGER.info("折线图已保存：%s", save_path)

        plt.close()

    def get_neighbor_evolution_table(
        self,
        target_word: str,
        top_n: int = 10,
    ) -> pd.DataFrame:
        """返回目标词在各时期的Top-N近邻演化情况表。"""

        self._ensure_word_exists(target_word)

        data: Dict[str, List[str]] = {}
        for period in self.periods:
            similar_words = self.models[period].similar_by_word(target_word, topn=top_n)
            formatted = [f"{word} ({score:.3f})" for word, score in similar_words]
            data[period] = formatted

        df = pd.DataFrame(data)
        return df

    def plot_jaccard_similarity(
        self,
        target_word: str,
        top_n: int = 50,
        save_path: Optional[str] = None,
    ) -> None:
        """绘制相邻时期Top-N近邻词集合的Jaccard相似度柱状图。"""

        self._ensure_word_exists(target_word)

        neighbor_sets: Dict[str, set] = {}
        for period in self.periods:
            similar_words = self.models[period].similar_by_word(target_word, topn=top_n)
            neighbor_sets[period] = {word for word, _ in similar_words}

        period_pairs: List[Tuple[str, str]] = list(zip(self.periods[:-1], self.periods[1:]))
        labels = [f"{a.title()}-{b.title()}" for a, b in period_pairs]
        scores: List[float] = []

        for period_a, period_b in period_pairs:
            set_a = neighbor_sets[period_a]
            set_b = neighbor_sets[period_b]
            intersection = len(set_a.intersection(set_b))
            union = len(set_a.union(set_b)) or 1
            jaccard = intersection / union
            scores.append(jaccard)

        plt.figure(figsize=(8, 5))
        plt.bar(labels, scores, color="#4C72B0")
        plt.ylim(0, 1)
        plt.ylabel("Jaccard 相似度")
        plt.title(f"{target_word} 的近邻集合重叠度")
        plt.grid(axis="y", linestyle="--", alpha=0.4)

        if save_path is not None:
            plt.tight_layout()
            plt.savefig(save_path, dpi=300)
            LOGGER.info("柱状图已保存：%s", save_path)

        plt.close()

    def find_top_drifters(
        self,
        start_period: str = "ancient",
        end_period: str = "contemporary",
        top_n: int = 20,
    ) -> List[Tuple[str, float]]:
        """找出在给定起止时期之间语义漂移幅度最大的词。"""

        if start_period not in self.periods or end_period not in self.periods:
            raise ValueError(f"start_period/end_period 必须在 {self.periods} 中")

        start_index = self.periods.index(start_period)
        end_index = self.periods.index(end_period)
        if start_index >= end_index:
            raise ValueError("start_period 必须早于 end_period")

        shared_vocab = set(self.models[start_period].key_to_index)
        for period in self.periods[start_index + 1 : end_index + 1]:
            shared_vocab.intersection_update(self.models[period].key_to_index)

        LOGGER.info("共享词汇量：%d", len(shared_vocab))

        start_vectors = self.models[start_period]
        end_vectors = self.models[end_period]

        drift_scores: List[Tuple[str, float]] = []
        for word in shared_vocab:
            start_vec = start_vectors[word]
            end_vec = end_vectors[word]
            cosine_similarity = np.dot(start_vec, end_vec) / (
                np.linalg.norm(start_vec) * np.linalg.norm(end_vec)
            )
            cosine_distance = 1 - cosine_similarity
            drift_scores.append((word, float(cosine_distance)))

        drift_scores.sort(key=lambda item: item[1], reverse=True)
        return drift_scores[:top_n]


def main() -> None:
    """演示如何使用 DiachronicAnalyzer 进行多种分析。"""

    analyzer = DiachronicAnalyzer("../models/word_vectors_aligned/")

    target_concepts = ["reason", "god", "nature", "law"]
    stable_concepts = ["water", "sun"]

    LOGGER.info("绘制目标词与稳定词的语义漂移曲线...")
    all_words = target_concepts + stable_concepts
    analyzer.plot_macro_drift(
        all_words,
        benchmark_period="modern",
        save_path=os.path.join("results", "macro_drift.png"),
    )

    for word in target_concepts:
        LOGGER.info("生成近邻演化表：%s", word)
        table = analyzer.get_neighbor_evolution_table(word, top_n=10)
        print(f"\n=== {word} 的近邻演化 ===")
        print(table)

        LOGGER.info("绘制Jaccard相似度图：%s", word)
        analyzer.plot_jaccard_similarity(
            word,
            top_n=50,
            save_path=os.path.join("results", f"{word}_jaccard.png"),
        )

    LOGGER.info("计算语义漂移最显著的词汇...")
    top_drifters = analyzer.find_top_drifters(
        start_period="ancient",
        end_period="contemporary",
        top_n=20,
    )
    print("\n=== 语义漂移最显著的词汇 ===")
    for rank, (word, score) in enumerate(top_drifters, start=1):
        print(f"{rank:2d}. {word:<20} 漂移距离：{score:.4f}")

    LOGGER.info("分析完成，图表与结果已输出到 results/ 目录或控制台。")


if __name__ == "__main__":
    main()


