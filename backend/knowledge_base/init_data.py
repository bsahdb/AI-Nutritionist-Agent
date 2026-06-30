"""
知识库初始化脚本

作用：
1. 初始化 MySQL 中的 nutrition_knowledge 表数据；
2. 初始化 Chroma 向量知识库；
3. 默认使用本地免费 embedding 模型；
4. 避免重复插入相同知识内容。

注意：
- 本文件应放在 backend/knowledge_base/init_data.py
- main.py 中应使用：
  from knowledge_base.init_data import init_knowledge_base
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import inspect

from core.database import SessionLocal
from core.models import NutritionKnowledge

try:
    from core.config import settings
except Exception:
    settings = None


# =========================
# 基础营养知识
# =========================

KNOWLEDGE_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "nutrition_001",
        "title": "高血压人群低盐饮食原则",
        "category": "高血压",
        "content": (
            "高血压人群应控制钠盐摄入，建议减少腌制食品、咸菜、火腿、方便面、"
            "高盐调味品等食物。日常饮食应以清淡为主，多选择新鲜蔬菜、水果、全谷物、"
            "低脂奶制品和优质蛋白。烹饪时可使用葱、姜、蒜、柠檬汁、香草等方式增加风味，"
            "减少食盐和酱油用量。"
        ),
        "source": "system_seed",
        "tags": "高血压,低盐,控钠",
    },
    {
        "id": "nutrition_002",
        "title": "糖尿病和血糖偏高人群饮食建议",
        "category": "血糖管理",
        "content": (
            "血糖偏高或糖尿病人群应控制精制碳水化合物摄入，减少含糖饮料、甜点、"
            "白米粥、白面包等升糖较快的食物。主食可适当选择燕麦、糙米、杂豆、全麦食品等，"
            "并注意控制总量。每餐应搭配蔬菜和优质蛋白，有助于延缓餐后血糖上升。"
        ),
        "source": "system_seed",
        "tags": "血糖,糖尿病,低GI",
    },
    {
        "id": "nutrition_003",
        "title": "高尿酸和痛风人群饮食原则",
        "category": "尿酸管理",
        "content": (
            "高尿酸或痛风人群应减少高嘌呤食物摄入，如动物内脏、浓肉汤、部分海鲜、"
            "大量红肉和啤酒。建议增加饮水量，保持规律饮食，选择鸡蛋、低脂奶、部分豆制品、"
            "新鲜蔬菜等相对安全的食物。急性痛风发作期应更加严格控制高嘌呤食物。"
        ),
        "source": "system_seed",
        "tags": "尿酸,痛风,低嘌呤",
    },
    {
        "id": "nutrition_004",
        "title": "血脂异常人群饮食建议",
        "category": "血脂管理",
        "content": (
            "血脂异常人群应减少饱和脂肪和反式脂肪摄入，少吃油炸食品、肥肉、奶油点心、"
            "加工肉制品等。建议选择鱼类、禽肉、豆制品、坚果、橄榄油等脂肪来源，"
            "同时增加膳食纤维摄入，如燕麦、蔬菜、水果和全谷物。"
        ),
        "source": "system_seed",
        "tags": "血脂,胆固醇,低脂",
    },
    {
        "id": "nutrition_005",
        "title": "减重人群饮食原则",
        "category": "体重管理",
        "content": (
            "减重饮食的核心是控制总能量摄入，同时保证蛋白质、膳食纤维、维生素和矿物质充足。"
            "建议减少高糖、高油、高能量密度食物，增加蔬菜、优质蛋白和全谷物。"
            "不建议长期采用极低热量饮食，以免影响代谢和营养状态。"
        ),
        "source": "system_seed",
        "tags": "减重,控热量,均衡饮食",
    },
    {
        "id": "nutrition_006",
        "title": "脂肪肝人群饮食建议",
        "category": "肝脏健康",
        "content": (
            "脂肪肝人群应控制总能量和精制糖摄入，减少含糖饮料、甜点、酒精和高脂食物。"
            "饮食应以清淡、均衡为主，适当增加优质蛋白、蔬菜、全谷物和膳食纤维。"
            "配合规律运动和体重管理，有助于改善脂肪肝。"
        ),
        "source": "system_seed",
        "tags": "脂肪肝,控糖,控脂",
    },
    {
        "id": "nutrition_007",
        "title": "蛋白质摄入建议",
        "category": "营养基础",
        "content": (
            "蛋白质是维持肌肉、免疫和组织修复的重要营养素。常见优质蛋白来源包括鱼、禽、蛋、奶、"
            "瘦肉和大豆制品。普通成年人应根据体重、运动量和健康状况合理摄入蛋白质，"
            "肾功能异常人群应在医生或营养师指导下调整蛋白质摄入。"
        ),
        "source": "system_seed",
        "tags": "蛋白质,优质蛋白,营养基础",
    },
    {
        "id": "nutrition_008",
        "title": "膳食纤维的作用",
        "category": "营养基础",
        "content": (
            "膳食纤维有助于改善肠道功能、增加饱腹感、延缓餐后血糖上升，并有助于血脂管理。"
            "常见来源包括蔬菜、水果、全谷物、杂豆、燕麦和菌菇类。"
            "增加膳食纤维时应循序渐进，并注意充足饮水。"
        ),
        "source": "system_seed",
        "tags": "膳食纤维,肠道健康,血糖管理",
    },
    {
        "id": "nutrition_009",
        "title": "老年人饮食注意事项",
        "category": "特殊人群",
        "content": (
            "老年人饮食应注意营养密度和消化吸收，保证优质蛋白、钙、维生素D和膳食纤维摄入。"
            "食物应软硬适中、清淡少盐，避免过度油腻和过甜。"
            "如果存在慢性病，应结合血压、血糖、血脂、肾功能等指标进行个体化调整。"
        ),
        "source": "system_seed",
        "tags": "老年人,慢病管理,营养均衡",
    },
    {
        "id": "nutrition_010",
        "title": "饮食建议不能替代医学诊疗",
        "category": "安全提示",
        "content": (
            "AI 生成的饮食计划只能作为健康管理参考，不能替代医生诊断、治疗或处方。"
            "如果存在严重异常指标、慢性病、妊娠、肾功能异常、肝功能异常或特殊疾病，"
            "应及时咨询医生或注册营养师。"
        ),
        "source": "system_seed",
        "tags": "安全提示,医学建议,免责声明",
    },
]


# =========================
# 配置读取工具
# =========================

def _get_config_value(name: str, default: Any = None) -> Any:
    """
    优先从 settings 读取配置；
    如果 settings 中没有，则从环境变量读取；
    如果都没有，则使用默认值。
    """
    if settings is not None and hasattr(settings, name):
        value = getattr(settings, name)
        if value is not None:
            return value

    return os.getenv(name, default)


def _get_backend_dir() -> Path:
    """
    当前文件路径：
    backend/knowledge_base/init_data.py

    parents[1] 是 backend 目录。
    """
    return Path(__file__).resolve().parents[1]


def _get_chroma_dir() -> str:
    """
    获取 Chroma 持久化目录。
    默认是 backend/knowledge_base。
    """
    persist_dir = _get_config_value("CHROMA_PERSIST_DIR", "./knowledge_base")
    persist_path = Path(str(persist_dir))

    if not persist_path.is_absolute():
        persist_path = _get_backend_dir() / persist_path

    persist_path.mkdir(parents=True, exist_ok=True)
    return str(persist_path)


# =========================
# MySQL 初始化
# =========================

def _get_model_columns() -> set:
    """
    自动读取 NutritionKnowledge 模型字段，
    避免字段名和模型不一致时报错。
    """
    mapper = inspect(NutritionKnowledge)
    return {column.key for column in mapper.attrs}


def _filter_payload_by_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    只保留 NutritionKnowledge 模型中存在的字段。
    """
    model_columns = _get_model_columns()
    return {key: value for key, value in payload.items() if key in model_columns}


def _init_mysql_knowledge() -> None:
    """
    初始化 MySQL nutrition_knowledge 表。
    如果 title 已存在，则不重复插入。
    """
    db = SessionLocal()

    try:
        inserted_count = 0

        for item in KNOWLEDGE_ITEMS:
            exists = None

            if hasattr(NutritionKnowledge, "title"):
                exists = (
                    db.query(NutritionKnowledge)
                    .filter(NutritionKnowledge.title == item["title"])
                    .first()
                )
            elif hasattr(NutritionKnowledge, "content"):
                exists = (
                    db.query(NutritionKnowledge)
                    .filter(NutritionKnowledge.content == item["content"])
                    .first()
                )

            if exists:
                continue

            payload = _filter_payload_by_model(
                {
                    "category": item["category"],
                    "title": item["title"],
                    "content": item["content"],
                    "tags": item["tags"],
                    "source": item["source"],
                    "embedding_id": item["id"],
                }
            )

            knowledge = NutritionKnowledge(**payload)
            db.add(knowledge)
            inserted_count += 1

        db.commit()
        print(f"MySQL 知识库初始化完成，新增 {inserted_count} 条知识。")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


# =========================
# Chroma 初始化
# =========================

def _get_embedding_function():
    """
    获取 Chroma 使用的 embedding 函数。

    默认使用本地模型：
    BAAI/bge-small-zh-v1.5

    优点：
    - 免费
    - 不需要 API Key
    - 适合中文
    - 适合开源项目

    如果你以后仍想用 OpenAI，可在 config.py 中设置：
    EMBEDDING_PROVIDER = "openai"
    """
    try:
        from chromadb.utils import embedding_functions
    except ImportError as e:
        raise ImportError("未安装 chromadb，请先执行：pip install chromadb") from e

    provider = str(_get_config_value("EMBEDDING_PROVIDER", "local")).lower()

    if provider == "local":
        local_model = _get_config_value(
            "LOCAL_EMBEDDING_MODEL",
            "BAAI/bge-small-zh-v1.5"
        )

        print(f"使用本地 Embedding 模型：{local_model}")

        try:
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=local_model
            )
        except Exception as e:
            raise RuntimeError(
                "本地 Embedding 模型初始化失败。请确认已安装 sentence-transformers：\n"
                "pip install sentence-transformers\n"
                f"原始错误：{e}"
            ) from e

    if provider == "openai":
        embedding_model = _get_config_value(
            "EMBEDDING_MODEL",
            "text-embedding-3-small"
        )
        embedding_base_url = _get_config_value(
            "EMBEDDING_BASE_URL",
            "https://api.openai.com/v1"
        )

        api_key = (
            _get_config_value("OPENAI_API_KEY", None)
            or _get_config_value("EMBEDDING_API_KEY", None)
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("EMBEDDING_API_KEY")
        )

        if not api_key:
            raise RuntimeError(
                "EMBEDDING_PROVIDER=openai，但未配置 OPENAI_API_KEY 或 EMBEDDING_API_KEY。"
            )

        print(f"使用 OpenAI Embedding 模型：{embedding_model}")

        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=embedding_model,
            api_base=embedding_base_url,
        )

    raise ValueError(
        f"不支持的 EMBEDDING_PROVIDER：{provider}。"
        "请设置为 local 或 openai。"
    )


def _get_or_recreate_collection(client, collection_name: str, embedding_function):
    """
    获取或创建 Chroma collection。

    如果检测到旧 collection 的 embedding 配置冲突，
    自动删除旧 collection 并重新创建。
    """
    try:
        return client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
        )

    except Exception as e:
        error_text = str(e).lower()

        if (
            "embedding function conflict" in error_text
            or "embedding function already exists" in error_text
            or "conflict" in error_text
        ):
            print("检测到 Chroma embedding 配置冲突，正在删除旧集合并重建...")

            try:
                client.delete_collection(name=collection_name)
            except Exception:
                pass

            return client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function,
            )

        raise e


def _init_chroma_knowledge() -> None:
    """
    初始化 Chroma 向量知识库。
    """
    try:
        import chromadb
    except ImportError:
        print("未安装 chromadb，跳过 Chroma 向量库初始化。")
        print("请执行：pip install chromadb")
        return

    chroma_dir = _get_chroma_dir()
    collection_name = _get_config_value(
        "CHROMA_COLLECTION_NAME",
        "nutrition_knowledge"
    )

    client = chromadb.PersistentClient(path=chroma_dir)

    embedding_function = _get_embedding_function()

    collection = _get_or_recreate_collection(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_function,
    )

    ids = [item["id"] for item in KNOWLEDGE_ITEMS]
    documents = [item["content"] for item in KNOWLEDGE_ITEMS]
    metadatas = [
        {
            "title": item["title"],
            "category": item["category"],
            "source": item["source"],
            "tags": item["tags"],
        }
        for item in KNOWLEDGE_ITEMS
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        f"Chroma 向量知识库初始化完成，"
        f"集合：{collection_name}，文档数：{len(ids)}"
    )
    print(f"Chroma 存储目录：{chroma_dir}")


# =========================
# 对外初始化入口
# =========================

def _init_knowledge_base_sync() -> None:
    """
    同步初始化函数。
    """
    _init_mysql_knowledge()
    _init_chroma_knowledge()


async def init_knowledge_base() -> None:
    """
    main.py 中调用的异步初始化入口。
    """
    await asyncio.to_thread(_init_knowledge_base_sync)