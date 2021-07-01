import pytest

from itchpy.cpp_gen import CPPGenerator


def test_cpp_gen_enum(lexer, parser, generator):
    input = """
    enum a: char {
        b, 
        c
    }
    """
    output = """enum a
{
  b,
  c
}
"""

    ast = parser.parse(lexer.tokenize(input))

    result = generator.visit(ast)

    assert result == output


def test_cpp_gen_struct(lexer, parser, generator):
    input = """
    struct a {
        b:char;
        c:short;
    }
    """
    output = """struct a
{
  char b;
  short c;
}
"""

    ast = parser.parse(lexer.tokenize(input))

    result = generator.visit(ast)

    assert result == output
