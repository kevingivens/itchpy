from sly import Parser

from lexer import ITCHLexer
import itch_ast as i_ast

# adapted from pycparser

class ITCHParser(Parser):
    # Get the token list from the lexer (required)
    tokens = ITCHLexer.tokens
    
    # debugfile = 'parser.out'

    # Grammar rules and actions
    @_("translation_unit")
    def translation_unit_or_empty(self, p):
       return i_ast.FileAST(p.translation_unit)
    
    @_("empty")
    def translation_unit_or_empty(self, p):
        return i_ast.FileAST([])

    @_('declaration_specifiers init_declarator_list_opt')
    def decl_body(self, p):
        spec = p[1]

        # p[2] (init_declarator_list_opt) is either a list or None
        #
        if p[2] is None:
            ty = spec['type']
            s_or_e = (i_ast.Struct, i_ast.Enum)
            if len(ty) == 1 and isinstance(ty[0], s_or_e):
                decls = [i_ast.Decl(
                    name=None,
                    type=ty[0],
                    init=None,
                    bitsize=None,
                    coord=ty[0].coord)]

            # However, this case can also occur on redeclared identifiers in
            # an inner scope.  The trouble is that the redeclared type's name
            # gets grouped into declaration_specifiers; _build_declarations
            # compensates for this.
            #
            else:
                decls = self._build_declarations(
                    spec=spec,
                    decls=[dict(decl=None, init=None)],
                    typedef_namespace=True)

        else:
            decls = self._build_declarations(
                spec=spec,
                decls=p[2],
                typedef_namespace=True)

        p[0] = decls

    @_('decl_body SEMI')
    def declaration(self, p):
        return p.decl_body

    @_('struct_declaration')
    def struct_declaration_list(self, p):
        return p[0] or []
    
    @_('struct_declaration_list struct_declaration')
    def struct_declaration_list(self, p):
        return p[0] + (p[1] or [])

    @_('struct_declarator_list_opt SEMI')
    def struct_declaration(self, p):
        spec = p[0]

        if p[1] is not None:
            decls = self._build_declarations(
                spec=spec,
                decls=p[2])

        elif len(spec['type']) == 1:
            # Anonymous struct/union, gcc extension, C1x feature.
            # Although the standard only allows structs/unions here, I see no
            # reason to disallow other types since some compilers have typedefs
            # here, and pycparser isn't about rejecting all invalid code.
            #
            node = spec['type'][0]
            if isinstance(node, i_ast.Node):
                decl_type = node
            else:
                decl_type = i_ast.IdentifierType(node)

            decls = self._build_declarations(
                spec=spec,
                decls=[dict(decl=decl_type)])

        else:
            # Structure/union members can have the same names as typedefs.
            # The trouble is that the member's name gets grouped into
            # specifier_qualifier_list; _build_declarations compensates.
            decls = self._build_declarations(
                spec=spec,
                decls=[dict(decl=None, init=None)])

        return decls

    @_('struct_declarator',
       'struct_declarator_list COMMA struct_declarator')
    def struct_declarator_list(self, p):
        return p[0] + [p[2]] if len(p) == 3 else [p[0]]

    # struct_declarator passes up a dict with the keys: decl (for
    # the underlying declarator) and bitsize (for the bitsize)
    @_('struct_declarator')
    def struct_declarator(self, p):
        return {'decl': p[0], 'bitsize': None}

    @_('declarator COLON constant_expression',
       'COLON constant_expression')
    def struct_declarator(self, p):
        if len(p) > 2:
            return {'decl': p[0], 'bitsize': p[2]}
        else:
            return {'decl': i_ast.TypeDecl(None, None, None), 'bitsize': p[1]}

    @_('STRUCT ID LBRACE struct_declaration_list RBRACE')
    def struct_specifier(self, p):
        return i_ast.Struct(
                name=p.ID,
                decls=p.struct_declaration_list,
                coord=self._token_coord(p, 2))

    @_('enum_specifier',
       'struct_specifier')
    def type_specifier(self, p):
        return p[0]
    
    @_('ENUM ID COLON typeid LBRACE enumerator_list RBRACE')
    def enum_specifier(self, p):
        return i_ast.Enum(p.ID, p.typeid, p.enumerator_list)

    @_('enumerator')
    def enumerator_list(self, p):
        return i_ast.EnumeratorList([p.enumerator])

    @_('enumerator_list COMMA')
    def enumerator_list(self, p):
        return p.enumerator_list
    
    @_('enumerator_list COMMA enumerator')
    def enumerator_list(self, p):
        p.enumerator_list.enumerators.append(p.enumerator)
        return p.enumerator_list
    
    @_('ID')
    def enumerator(self, p):
        return i_ast.Enumerator(p.ID, None)

    @_('enum_specifier',
       'struct_specifier',
       'type_specifier_no_typeid')
    def type_specifier(self, p):
        return p[0]
    
    @_('CHAR',
       'USHORT',
       'SHORT',
       'ULONG',
       'LONG',
       'DOUBLE',
       'TIME')
    def type_specifier_no_typeid(self, p):
        return i_ast.IdentifierType([p[0]], coord=self._token_coord(p, 1))

    
if __name__ == '__main__':
    data = """
    enum Ticket: char {
        Stop, 
        Speed
    }
    """
    # enum Color: char {Red, Blue}
    
    lexer = ITCHLexer()
    
    parser = ITCHParser()

    result = parser.parse(lexer.tokenize(data))
    print(result)