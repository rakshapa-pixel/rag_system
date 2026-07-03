from rag import load_vectorstore, build_qa_chain, collection_has_data

# In-memory cache: {user_id: (qa_chain, retriever)}
_chains: dict = {}


def has_vectorstore(user_id: int) -> bool:
    return collection_has_data(user_id)


def get_chain(user_id: int):
    if user_id not in _chains:
        vs = load_vectorstore(user_id)
        _chains[user_id] = build_qa_chain(vs)
    return _chains[user_id]


def set_chain(user_id: int, chain_tuple: tuple):
    _chains[user_id] = chain_tuple


def evict_chain(user_id: int):
    _chains.pop(user_id, None)
