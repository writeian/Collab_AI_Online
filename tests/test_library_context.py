"""Unit tests for adaptive Library document context (read scope + snippet sizing)."""

from src.utils.openai_utils import _library_read_scope, build_document_context_block


def test_library_read_scope_empty_is_targeted():
    assert _library_read_scope("") == "targeted"
    assert _library_read_scope("   ") == "targeted"


def test_library_read_scope_whole_document_markers():
    assert _library_read_scope("please read the entire document") == "full_document"
    assert _library_read_scope("what does my full text say about x") == "full_document"
    assert _library_read_scope("go through the essay from beginning to end") == "full_document"


def test_library_read_scope_summarize_document_phrases():
    assert _library_read_scope("summarize my essay") == "full_document"
    assert _library_read_scope("can you summarize this document") == "full_document"


def test_library_read_scope_targeted_by_default():
    assert (
        _library_read_scope(
            "in my library document what happened in chapter 3 regarding the treaty"
        )
        == "targeted"
    )


def test_build_document_context_block_respects_max_chars():
    snippets = [
        {
            "title": "Doc",
            "content": "x" * 500,
            "chunk_index": 1,
            "rank": 0.5,
        }
    ]
    block = build_document_context_block(snippets, max_chars_per_snippet=100)
    content_lines = [ln for ln in block.split("\n") if ln.startswith("x")]
    assert content_lines and content_lines[0] == "x" * 100 + "..."
