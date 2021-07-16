import sys

import click

from .cpp_gen import CPPGenerator
from .parser import ITCHParser
from .lexer import ITCHLexer
from .itch_ast import Enum, Struct


class ItchCompiler(object):
    namespace = "\nnamespace itchpy {\n"
    footer = "\n}\n"
    def __init__(self):
        self.gen = CPPGenerator()
        self.lexer = ITCHLexer()
        self.parser = ITCHParser()
        self.ast = None

    def compile(self, data, enums_fp, structs_fp):
        self.ast = self.parser.parse(self.lexer.tokenize(data))
        enums = self._gen_enums()
        structs = self._gen_structs(enums_fp)
        parser = self._gen_parser(enums_fp, structs_fp)
        return enums, structs, parser

    @property
    def enums(self):
        return [d for d in self.ast.decls if isinstance(d, Enum)]

    @property
    def structs(self):
        return [d for d in self.ast.decls if isinstance(d, Struct)]
    
    def _gen_enums(self):
        """ generate file (str) of enum definitions """
        header = f"{self.namespace}"
        return header + "/n".join(self.gen.visit_Enum(e) for e in self.enums) + self.footer

    def _gen_structs(self, enums_fp):
        """ generate file (str) of struct (message) definitions """
        header = f"#include {enums_fp}\n\n {self.namespace}"
        struct_str = "/n ".join(self.gen.visit_Struct(e) for e in self.structs)
        return header + "#pragma pack(push, 1):\n" + struct_str + "\npop(push)" + self.footer
    
    def _gen_parser(self, enums_fp, structs_fp):
        """ generate file (str) of parser """
        header = f"#include {enums_fp}\n#include {structs_fp}\n\n {self.namespace}"
        return header + self.footer


@click.command()
@click.argument('itch', type=click.File('r'), help='ITCH spec filename')
@click.argument('enum', type=click.File('w'), help='enums filename')
@click.argument('structs', type=click.File('w'), help='structs filename')
@click.argument('parser', type=click.File('w'), help='parser filename')
def compile(itch, enums, structs, parser):
    """Generate C++ ITCH parser from itch specification file"""
    data = itch.read()
    comp = ItchCompiler()
    enums_str, structs_str, parser_str = comp.compile(data, enums, structs, parser)
    enums.write(enums_str)
    structs.write(structs_str)
    parser.write(parser_str)


if __name__ == "__main__":
    compile()