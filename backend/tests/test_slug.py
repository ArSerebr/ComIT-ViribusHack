"""app.core.slug: transliteration and ASCII slugs."""

from app.core.slug import project_details_path, slugify_project_identifier, transliterate_cyrillic_to_latin


def test_transliterate_cyrillic_to_latin_basic():
    assert transliterate_cyrillic_to_latin("сырок") == "syrok"
    assert transliterate_cyrillic_to_latin("Сырок") == "syrok"


def test_slugify_project_identifier_from_cyrillic_id():
    assert slugify_project_identifier("сырок-r110") == "syrok-r110"


def test_slugify_project_identifier_from_title_fallback():
    assert slugify_project_identifier("", title="Мой проект") == "moy-proekt"


def test_project_details_path():
    assert project_details_path("syrok-r110") == "/projects/syrok-r110"
