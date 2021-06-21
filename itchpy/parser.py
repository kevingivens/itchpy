from sly import Parser

from lexer import ITCHLexer
import itch_ast as i_ast

# adapted from pycparser

class ITCHParser(Parser):
    # builds an AST
        
    # Get the token list from the lexer (required)
    tokens = ITCHLexer.tokens
    
    # debugfile = 'parser.out'

    # Grammar rules and actions
    
    #@_("translation_unit")
    #def translation_unit_or_empty(self, p):
    #   # print("in tue 1")
    #   return i_ast.FileAST(p.translation_unit)
    #
    #@_("empty")
    #def translation_unit_or_empty(self, p):
    #    # print("in tue 2")
    #    return i_ast.FileAST([])
    
    @_('declaration')
    def translation_unit(self, p):
        return i_ast.FileAST([p.declaration])

    @_('translation_unit declaration')
    def translation_unit(self, p):
        return p[0].decls.extend(p[1])

    @_("struct_decl",
       "enum_decl")
    def declaration(self, p):
        return p[0]
    
    @_('STRUCT ID LBRACE field_declarator_list RBRACE')
    def struct_decl(self, p):
        return i_ast.Struct(name=p.ID, fields=p.field_declarator_list)
    
    @_('field_declarator')
    def field_declarator_list(self, p):
        return [p[0]]

    @_('field_declarator_list field_declarator')
    def field_declarator_list(self, p):
        return p[0] + [p[1]]
    
    # TODO: consider type_specifier instead of second ID
    @_('ID COLON typeid SEMI')
    def field_declarator(self, p):
        return i_ast.FieldDecl(p[0], p[2])

    @_('ENUM ID COLON typeid LBRACE enum_value_list RBRACE')
    def enum_decl(self, p):
        return i_ast.Enum(p.ID, p.typeid, p.enum_value_list)

    @_('enum_value')
    def enum_value_list(self, p):
        return i_ast.EnumeratorList([p.enum_value])

    @_('enum_value_list COMMA')
    def enum_value_list(self, p):
        return p.enum_value_list
    
    @_('enum_value_list COMMA enum_value')
    def enum_value_list(self, p):
        p.enum_value_list.enumerators.append(p.enum_value)
        return p.enum_value_list
    
    @_('ID')
    def enum_value(self, p):
        return i_ast.Enumerator(p.ID, None)

    #@_('ENUM')
    #def enum_specifier(self, p):
    #    return p[0]
    
    #@_('STRUCT')
    #def struct_specifier(self, p):
    #    return p[0]

    #@_('enum_specifier',
    #   'struct_specifier',
    #   'typeid')
    #def type_specifier(self, p):
    #    return p[0]

    @_('CHAR',
       'USHORT',
       'SHORT',
       'ULONG',
       'LONG',
       'DOUBLE',
       'TIME')
    def typeid(self, p):
        return i_ast.IdentifierType([p[0]])

    #@_('')
    #def empty(self, p):
    #    pass

    
if __name__ == '__main__':
    data = """
    enum Ticket: char {
        Stop, 
        Speed
    }"""
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
    """
    
    lexer = ITCHLexer()
    
    parser = ITCHParser()

    result = parser.parse(lexer.tokenize(data))
    print(result)