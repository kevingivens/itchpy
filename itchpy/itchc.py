from itchpy.cpp_gen import CPPGenerator
from itchpy.parser import ITCHParser
from itchpy.lexer import ITCHLexer
from itchpy.itch_ast import Enum, Struct


class ItchCompiler(object):
    def __init__(self):
        self.gen = CPPGenerator()
        self.lexer = ITCHLexer()
        self.parser = ITCHParser()
        self.ast = None

    def compile(self, data):
        self.ast = self.parser.parse(self.lexer.tokenize(data))
        self._gen_cpp()

    @property
    def enums(self):
        return [d for d in self.ast.DeclList if isinstance(d, Enum)]

    @property
    def structs(self):
        return [d for d in self.ast.DeclList if isinstance(d, Struct)]
    
    def _gen_cpp(self):
        self._gen_enums()
        self._gen_structs()

    def _gen_enums(self):
        return "/n".join(self.gen.visit_Enum(e) for e in self.enums)

    def _gen_structs(self):
        struct_str = "/n ".join(self.gen.visit_Struct(e) for e in self.structs)
        return "pragma push(1):\n" + struct_str + "\npop(1)"

if __name__ == "__main__":
    data = """
    struct AddOrder {
        message_type:char;
        stock_locate:short;
        tracking_number:short;
        timestamp:time;
    }
    struct LimitOrder {
        message_type:char;
        stock_locate:short;
        tracking_number:short;
        timestamp:time;
    }
    enum Ticket: char {
        Stop, 
        Speed
    }
    """
   
    comp = ItchCompiler()
    print(comp.compile(data))