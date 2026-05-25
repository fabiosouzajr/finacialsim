import pytest

from app.utils.document_validation import is_valid_cnpj, is_valid_cpf


def test_known_valid_cpf():
    assert is_valid_cpf("52998224725") is True


def test_known_invalid_cpf():
    assert is_valid_cpf("11111111111") is False
    assert is_valid_cpf("123") is False


def test_known_valid_cnpj():
    assert is_valid_cnpj("11444777000161") is True


def test_known_invalid_cnpj():
    assert is_valid_cnpj("00000000000000") is False
