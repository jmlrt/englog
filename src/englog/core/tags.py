"""Tag parsing and formatting for englog."""

import re

TAG_PATTERN = re.compile(r"@([a-zA-Z0-9_-]+)")


def parse_tags(text: str) -> list[str]:
    """Extract tags from text. Returns list of tags without @ prefix."""
    return TAG_PATTERN.findall(text)


def extract_tags_from_text(text: str) -> tuple[str, list[str]]:
    """Extract tags from text and return (content_without_tags, tags)."""
    tags = parse_tags(text)
    # Remove tags from text
    content = TAG_PATTERN.sub("", text).strip()
    # Clean up multiple spaces
    content = re.sub(r"\s+", " ", content).strip()
    return content, tags


def format_tags(tags: list[str]) -> str:
    """Format tags for display/storage. Returns '@tag1 @tag2' format."""
    if not tags:
        return ""
    return " ".join(f"@{tag}" for tag in tags)
