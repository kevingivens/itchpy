import pytest
from itchpy.lexer import ITCHLexer
from itchpy.parser import ITCHParser
from itchpy.cpp_gen import CPPGenerator


@pytest.fixture
def lexer():
    return ITCHLexer()


@pytest.fixture
def parser():
    return ITCHParser()


@pytest.fixture
def generator():
    return CPPGenerator()