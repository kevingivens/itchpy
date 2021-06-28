import pytest
from itchpy.lexer import ITCHLexer


@pytest.fixture
def lexer():
    return ITCHLexer()

# Test basic recognition of various tokens and literals
def test_tokens(lexer):
    toks = list(lexer.tokenize('{ } , ; : struct enum add short char time'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['LBRACE','RBRACE','COMMA','SEMI','COLON','STRUCT','ENUM','ID','SHORT','CHAR','TIME']
    assert vals == ['{', '}', ',', ';', ':', 'struct', 'enum', 'add', 'short', 'char', 'time']

# Test ignored comments and newlines
def test_ignored(lexer):
    toks = list(lexer.tokenize('\n\n# A comment\nadd\norder\n'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    linenos = [t.lineno for t in toks]
    assert types == ['ID', 'ID']
    assert vals == ['add', 'order']
    assert linenos == [4,5]
    assert lexer.lineno == 6

# Test error handling
def test_error(lexer):
    toks = list(lexer.tokenize('add **{'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['ID', 'LBRACE']
    assert vals == ['add', '{']
    assert lexer.errors == [ '**{', '*{' ]

# Test error token return handling
def test_error_return(lexer):
    lexer.return_error = True
    toks = list(lexer.tokenize('add **{'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['ID', 'ERROR', 'ERROR', 'LBRACE']
    assert vals == ['add', '**{', '*{','{']
    assert lexer.errors == [ '**{', '*{' ]