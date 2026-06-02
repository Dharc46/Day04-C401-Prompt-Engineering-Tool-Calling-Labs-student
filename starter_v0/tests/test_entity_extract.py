from tools import TOOL_FUNCTIONS


def test_entity_extract_basic():
    fn = TOOL_FUNCTIONS.get('entity_extract')
    assert fn is not None
    res = fn("OpenAI released GPT-4. Elon Musk attended.", top_k=3)
    assert 'entities' in res
    texts = [e['text'] for e in res['entities']]
    assert any('Elon Musk' in t for t in texts) or any('GPT' in t for t in texts)
