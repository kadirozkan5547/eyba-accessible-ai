"""BUILD MODE: modelleri indirir ve bir kez yükler (plan §11.3).

Çevrimdışı demo öncesi zorunludur. İnternet gerektirir.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.foundry import get_handles  # noqa: E402
from app.settings import settings  # noqa: E402


def main() -> int:
    print(f"Embedding modeli: {settings.embedding_model}")
    print(f"Chat modeli     : {settings.chat_model}")
    handles = get_handles(allow_download=True)
    response = handles.embedding_client.generate_embedding("erişilebilirlik testi")
    print(f"[OK] embedding boyutu: {len(response.data[0].embedding)}")
    reply = handles.chat_client.complete_chat(
        [{"role": "user", "content": "Tek kelimeyle cevap ver: merhaba"}]
    )
    print(f"[OK] chat yanıtı: {reply.choices[0].message.content.strip()[:60]}")
    print("Her iki model indirildi ve başarıyla yüklendi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
