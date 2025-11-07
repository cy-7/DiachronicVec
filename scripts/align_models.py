"""使用中心枢纽策略对齐多个历史时期的Word2Vec模型。"""

import logging
import os
from typing import Dict, Iterable

import numpy as np
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


INPUT_DIR = "../models/word2vec/"
OUTPUT_DIR = "../models/word_vectors_aligned/"
HUB_MODEL_NAME = "modern"
SPOKE_MODEL_NAMES = ["ancient", "medieval", "contemporary"]


def resolve_path(relative_path: str) -> str:
    """将相对路径转换为脚本所在目录的绝对路径。"""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, relative_path))


def load_models(input_base: str) -> Dict[str, KeyedVectors]:
    """加载所有模型并返回KeyedVectors字典。"""

    model_names = [HUB_MODEL_NAME] + SPOKE_MODEL_NAMES
    keyed_vectors: Dict[str, KeyedVectors] = {}

    for name in model_names:
        model_path = os.path.join(input_base, f"{name}.model")
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"未找到模型文件：{model_path}")
        LOGGER.info("正在加载模型：%s", model_path)
        model = Word2Vec.load(model_path)
        keyed_vectors[name] = model.wv

    return keyed_vectors


def _get_shared_vocab(source_wv: KeyedVectors, target_wv: KeyedVectors) -> Iterable[str]:
    """返回source与target之间的共享词汇表。"""

    shared_tokens = set(source_wv.key_to_index).intersection(target_wv.key_to_index)
    if not shared_tokens:
        raise ValueError("两个模型之间没有共享词汇，无法执行对齐。")
    return sorted(shared_tokens)


def align_and_create_new_kv(source_wv: KeyedVectors, target_wv: KeyedVectors) -> KeyedVectors:
    """使用正交普罗克汝斯忒斯方法将source向量旋转到target空间。

    该过程基于两个词向量模型的共享词汇：
    1. 提取共享词汇的向量并中心化。
    2. 通过SVD求得最优旋转矩阵。
    3. 将旋转矩阵应用到source模型的全部词向量上，
       同时使用共享词汇的均值对齐偏移，使得整体分布与target一致。
    4. 返回包含对齐后向量的新KeyedVectors对象。
    """

    shared_vocab = _get_shared_vocab(source_wv, target_wv)

    source_matrix = np.vstack([source_wv[word] for word in shared_vocab])
    target_matrix = np.vstack([target_wv[word] for word in shared_vocab])

    source_mean = source_matrix.mean(axis=0, keepdims=True)
    target_mean = target_matrix.mean(axis=0, keepdims=True)
    source_centered = source_matrix - source_mean
    target_centered = target_matrix - target_mean

    covariance = target_centered.T @ source_centered
    U, _, Vt = np.linalg.svd(covariance)
    rotation = U @ Vt

    aligned_vectors = (source_wv.vectors - source_mean) @ rotation + target_mean

    aligned_kv = KeyedVectors(vector_size=source_wv.vector_size)
    aligned_kv.add_vectors(source_wv.index_to_key, aligned_vectors)
    aligned_kv.fill_norms(force=True)

    return aligned_kv


def align_models(models: Dict[str, KeyedVectors], output_base: str) -> None:
    """将所有spoke模型旋转对齐到hub模型并保存结果。"""

    os.makedirs(output_base, exist_ok=True)

    hub_wv = models[HUB_MODEL_NAME]

    hub_output_path = os.path.join(output_base, f"{HUB_MODEL_NAME}_aligned.kv")
    LOGGER.info("保存枢纽模型向量：%s", hub_output_path)
    hub_wv.save(hub_output_path)

    for spoke_name in SPOKE_MODEL_NAMES:
        spoke_wv = models[spoke_name]
        LOGGER.info("开始对齐 %s -> %s", spoke_name, HUB_MODEL_NAME)

        aligned_spoke_wv = align_and_create_new_kv(spoke_wv, hub_wv)

        output_path = os.path.join(output_base, f"{spoke_name}_aligned.kv")
        LOGGER.info("对齐完成，正在保存：%s", output_path)
        aligned_spoke_wv.save(output_path)


def main() -> None:
    """脚本执行入口。"""

    input_base = resolve_path(INPUT_DIR)
    output_base = resolve_path(OUTPUT_DIR)

    models = load_models(input_base)
    align_models(models, output_base)


if __name__ == "__main__":
    main()


