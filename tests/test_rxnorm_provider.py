import sqlite3
from pathlib import Path

import pytest

from providers.rxnorm_provider import RxNormProvider


@pytest.fixture
def tiny_db(tmp_path) -> Path:
    db_path = tmp_path / "rxnorm.db"
    with sqlite3.connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE drugs (rxcui TEXT, tty TEXT, name TEXT, name_lower TEXT);
            CREATE TABLE brand_ingredient (brand_rxcui TEXT, ingredient_rxcui TEXT);
            INSERT INTO drugs VALUES ('11289', 'IN', 'warfarin', 'warfarin');
            INSERT INTO drugs VALUES ('202421', 'BN', 'Coumadin', 'coumadin');
            INSERT INTO brand_ingredient VALUES ('202421', '11289');
            """
        )
    return db_path


def test_lookup_ingredient(tiny_db):
    result = RxNormProvider(tiny_db).lookup("Warfarin")
    assert result is not None
    assert result.rxcui == "11289"
    assert not result.is_brand
    assert result.ingredients == ["warfarin"]


def test_lookup_brand_resolves_ingredients(tiny_db):
    result = RxNormProvider(tiny_db).lookup("coumadin")
    assert result is not None
    assert result.is_brand
    assert result.ingredients == ["warfarin"]


def test_lookup_unknown_returns_none(tiny_db):
    assert RxNormProvider(tiny_db).lookup("nonexistent") is None


def test_suggest_prefix(tiny_db):
    assert RxNormProvider(tiny_db).suggest("warf") == ["warfarin"]


def test_missing_db_degrades_gracefully(tmp_path):
    provider = RxNormProvider(tmp_path / "missing.db")
    assert not provider.available
    assert provider.lookup("warfarin") is None
    assert provider.suggest("warf") == []
