"""KAN-6: AI-generated room titles must be saved as plain text (no markdown)."""

import pytest

from src.utils.title_generator import clean_ai_title


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("**Healthcare Inequality: Structural Roots**", "Healthcare Inequality: Structural Roots"),
        ("*Creative Writing*", "Creative Writing"),
        ("__Bold__ and _italic_", "Bold and italic"),
        ("# Photography Studio\n\nThis title reflects the goals...", "Photography Studio"),
        ('Title: "Disease Metaphors"', "Disease Metaphors"),
        ("**Room Title:** Climate Ethics", "Climate Ethics"),
        ("Intro to Statistics.", "Intro to Statistics"),
        ("  Plain   Title  ", "Plain Title"),
        ("Data_Science Basics", "Data_Science Basics"),  # underscores inside words survive
        ("", ""),
        (None, ""),
    ],
)
def test_clean_ai_title(raw, expected):
    assert clean_ai_title(raw) == expected
