"""Merkezi yapılandırma (plan §89, §90). Magic number yok; tüm ayarlar buradan."""

from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


class Settings(BaseSettings):
    app_name: str = "Accessible Local RAG"
    product_name_tr: str = "Erişilebilir Yerel Bilgi Asistanı"
    app_version: str = "1.1.0"

    # Modeller — plan §11.2
    embedding_model: str = "qwen3-embedding-0.6b"
    chat_model: str = "qwen2.5-1.5b"  # plan §11.2 uyarınca değiştirildi; gerekçe PROJECT_SPEC §6

    # Retrieval — plan §20
    top_k: int = 4
    # 2026-08-20 ölçümü: cevaplanabilir min=0.4395, kapsam dışı max=0.3413.
    min_similarity: float = 0.39

    # Chunking — plan §18.1
    chunk_target_tokens: int = 550
    chunk_overlap_tokens: int = 80

    # Dil ve sürüm
    language: str = "tr"
    knowledge_version: str = "2026-08-20"

    # Girdi doğrulama — plan §68
    max_question_chars: int = 1000

    # Gizlilik — plan §52
    conversation_persistence: bool = False
    analytics: bool = False
    remote_logging: bool = False

    # Yollar
    manifest_path: Path = KNOWLEDGE_DIR / "manifest" / "sources.yaml"
    raw_dir: Path = KNOWLEDGE_DIR / "raw"
    normalized_dir: Path = KNOWLEDGE_DIR / "normalized"
    chunks_path: Path = KNOWLEDGE_DIR / "chunks" / "chunks.jsonl"
    index_dir: Path = KNOWLEDGE_DIR / "index"

    @property
    def embeddings_path(self) -> Path:
        return self.index_dir / "embeddings.npy"

    @property
    def chunk_ids_path(self) -> Path:
        return self.index_dir / "chunk_ids.json"

    @property
    def index_meta_path(self) -> Path:
        return self.index_dir / "index_meta.json"


settings = Settings()
