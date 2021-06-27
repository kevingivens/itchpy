import pytest
from itchpy.lexer import ITCHLexer


# Test basic recognition of various tokens and literals
def test_tokens():
    lexer = ITCHLexer()
    toks = list(lexer.tokenize('{ } , ; : struct enum add short char time'))
    types = [t.type for t in toks]
    vals = [t.value for t in toks]
    assert types == ['LBRACE','RBRACE','COMMA','SEMI','COLON','STRUCT','ENUM','ID','SHORT','CHAR','TIME']
    assert vals == ['{', '}', ',', ';', ':', 'struct', 'enum', 'add', 'short', 'char', 'time']