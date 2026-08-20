"""Foundry Local yaşam döngüsü (plan §19.1, §66).

Modeller süreç başına bir kez initialize/load edilir; her soru için yeniden
yüklenmez. Bu modül runtime'da hiçbir dış ağ çağrısı yapmaz — model indirme
yalnız `scripts/prepare_models.py` içindedir (plan §53).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from foundry_local_sdk import Configuration, FoundryLocalManager

from app.settings import settings

_initialized = False


def _ensure_manager():
    global _initialized
    if not _initialized:
        FoundryLocalManager.initialize(Configuration(app_name="accessible_local_rag"))
        _initialized = True
    return FoundryLocalManager.instance


@dataclass
class ModelHandles:
    embedding_client: object
    chat_client: object
    embedding_alias: str
    chat_alias: str


_handles: Optional[ModelHandles] = None


def get_handles(*, allow_download: bool = False) -> ModelHandles:
    """Embedding ve chat modellerini yükler ve önbelleğe alır.

    allow_download yalnız build-time betiklerinden True verilir; runtime'da
    model cache'te değilse hata yükseltilir (plan §11.3, §42).
    """
    global _handles
    if _handles is not None:
        return _handles

    manager = _ensure_manager()
    clients = {}
    for role, alias in (
        ("embedding", settings.embedding_model),
        ("chat", settings.chat_model),
    ):
        model = manager.catalog.get_model(alias)
        if not model.is_cached:
            if not allow_download:
                raise RuntimeError(
                    f"Yerel model önbellekte bulunamadı: {alias}. "
                    "Çevrimdışı çalışmadan önce `python scripts/prepare_models.py` "
                    "komutunu internet bağlıyken bir kez çalıştırın."
                )
            model.download()
        model.load()
        clients[role] = (
            model.get_embedding_client() if role == "embedding" else model.get_chat_client()
        )

    _handles = ModelHandles(
        embedding_client=clients["embedding"],
        chat_client=clients["chat"],
        embedding_alias=settings.embedding_model,
        chat_alias=settings.chat_model,
    )
    return _handles


def is_cached(alias: str) -> bool:
    """Model ağırlıkları yerel cache'te mi? (health/offline göstergesi, plan §42)"""
    return bool(_ensure_manager().catalog.get_model(alias).is_cached)
