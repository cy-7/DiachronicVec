"""训练多个历史阶段的Word2Vec模型。"""

import json
import logging
import multiprocessing
import os
from typing import List

from gensim.models import Word2Vec


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


INPUT_DIR = "../processed_corpus/"
OUTPUT_DIR = "../models/word2vec/"
VECTOR_SIZE = 300
WINDOW = 10
WORKERS = multiprocessing.cpu_count()


PERIOD_CONFIGS = [
    {
        "period_name": "ancient",
        "input_file": "ancient_sentences.json",
        "min_count": 7,
    },
    {
        "period_name": "medieval",
        "input_file": "medieval_sentences.json",
        "min_count": 5,
    },
    {
        "period_name": "modern",
        "input_file": "modern_sentences.json",
        "min_count": 10,
    },
    {
        "period_name": "contemporary",
        "input_file": "contemporary_sentences.json",
        "min_count": 2,
    },
]


def _resolve_path(relative_path: str) -> str:
    """将相对路径解析为脚本所在目录的绝对路径。"""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, relative_path))


def load_sentences(file_path: str) -> List[List[str]]:
    """从JSON文件中加载分词后的句子列表。"""

    LOGGER.info("加载数据：%s", file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        sentences = json.load(file)
    if not isinstance(sentences, list):
        raise ValueError(f"文件内容格式不正确：{file_path}")
    return sentences


def train_and_save_model(period_config: dict, input_base: str, output_base: str) -> None:
    """针对单个历史时期训练并保存Word2Vec模型。"""

    period_name = period_config["period_name"]
    input_file = period_config["input_file"]
    min_count = period_config["min_count"]

    input_path = os.path.join(input_base, input_file)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"未找到输入文件：{input_path}")

    sentences = load_sentences(input_path)

    LOGGER.info(
        "开始训练模型：%s (vector_size=%d, window=%d, min_count=%d)",
        period_name,
        VECTOR_SIZE,
        WINDOW,
        min_count,
    )

    model = Word2Vec(
        sentences=sentences,
        vector_size=VECTOR_SIZE,
        window=WINDOW,
        min_count=min_count,
        workers=WORKERS,
    )

    LOGGER.info("模型训练完成：%s", period_name)

    output_path = os.path.join(output_base, f"{period_name}.model")
    model.save(output_path)
    LOGGER.info("模型已保存：%s", output_path)


def main() -> None:
    """脚本入口。"""

    input_base = _resolve_path(INPUT_DIR)
    output_base = _resolve_path(OUTPUT_DIR)

    os.makedirs(output_base, exist_ok=True)

    for period_config in PERIOD_CONFIGS:
        train_and_save_model(period_config, input_base, output_base)


if __name__ == "__main__":
    main()


