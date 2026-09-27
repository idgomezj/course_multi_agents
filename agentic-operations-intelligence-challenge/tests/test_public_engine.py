from pathlib import Path

from challenge.rag import RagIndex


def test_rag_accepts_documents_from_api(tmp_path: Path):
    config = tmp_path / "config.yaml"
    config.write_text("chunk_size: 50\noverlap: 5\ntop_k: 2\nmin_score: 0.0\nngram_max: 1\n")
    documents = [
        {"name": "policy.md", "content": "JIT inventory must stay low. Supplier delivery timing is critical."},
        {"name": "contract.md", "content": "High value purchases require approval."},
    ]
    index = RagIndex(documents, config)
    results = index.search("supplier delivery JIT")
    assert results
    assert results[0]["source"] == "policy.md"
