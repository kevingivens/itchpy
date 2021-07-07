from .cpp_gen import CPPGenerator
from .parser import ITCHParser
from .lexer import ITCHLexer
from .itch_ast import Enum, Struct


class ItchCompiler(object):
    def __init__(self):
        self.gen = CPPGenerator()
        self.lexer = ITCHLexer()
        self.parser = ITCHParser()
        self.ast = None

    def compile(self, data):
        self.ast = self.parser.parse(self.lexer.tokenize(data))
        enums_str = self._gen_enums()
        struct_str = self._gen_structs()
        return enums_str, struct_str

    @property
    def enums(self):
        return [d for d in self.ast.decls if isinstance(d, Enum)]

    @property
    def structs(self):
        return [d for d in self.ast.decls if isinstance(d, Struct)]

    def _gen_enums(self):
        return "/n".join(self.gen.visit_Enum(e) for e in self.enums)

    def _gen_structs(self):
        struct_str = "/n ".join(self.gen.visit_Struct(e) for e in self.structs)
        return "#pragma pack(1):\n" + struct_str + "\npop()"

