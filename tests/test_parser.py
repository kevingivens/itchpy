import pytest

from itchpy.itch_ast import (FileAST, Struct, FieldDecl, ID, 
                             Enum, Enumerator, EnumeratorList)


# Test basic recognition of various tokens and literals
def test_parse_enum(lexer, parser):
    result = parser.parse(lexer.tokenize('enum Ticket: char {Stop, Speed}'))
    assert isinstance(result, FileAST)
    assert isinstance(result.decls[0], Enum)
    assert result.decls[0].name == 'Ticket'
    assert isinstance(result.decls[0].values, EnumeratorList)

def test_parse_struct(lexer, parser):
    result = parser.parse(lexer.tokenize('struct add { m_type:char; stamp:time; }'))
    assert isinstance(result, FileAST)
    assert isinstance(result.decls[0], Struct)
    assert result.decls[0].name == 'add'
    assert isinstance(result.decls[0].fields[0], FieldDecl)

def test_parse_error(lexer, parser):
    result = parser.parse(lexer.tokenize('enum Ticket: thing'))
    assert parser.errors[0].type == 'ID'
    assert parser.errors[0].value == 'thing'
