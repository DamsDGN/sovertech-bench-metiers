import hashlib

VERSION = "v0"

CHAT_SYSTEME = (
    "Tu es un assistant d'un cabinet d'expertise comptable. Tu réponds en français, de façon claire et "
    "professionnelle, en respectant strictement les consignes de la demande. Si une information demandée "
    "ne figure pas dans les éléments fournis, tu le dis au lieu de l'inventer."
)

RAG_SYSTEME = (
    "Tu es un assistant d'un cabinet d'expertise comptable. Réponds uniquement à partir des extraits de "
    "documents fournis. Cite le titre du document dont provient l'information. Quand plusieurs versions d'un "
    "document existent, appuie-toi sur la version en vigueur. Si les extraits ne contiennent pas la réponse, "
    "ou seulement une partie, dis clairement ce qui manque, sans rien inventer. Réponds en français, de "
    "façon concise."
)


def chat_utilisateur(consigne: str, passages: list) -> str:
    if not passages:
        return consigne
    return "Documents fournis :\n\n" + "\n\n".join(passages) + "\n\n---\n\n" + consigne


def rag_utilisateur(question: str, passages: list) -> str:
    return "Extraits :\n\n" + "\n\n".join(passages) + "\n\n---\n\nQuestion : " + question


def empreinte(systeme_agent: str) -> str:
    texte = "\n".join([VERSION, CHAT_SYSTEME, RAG_SYSTEME, systeme_agent])
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]
