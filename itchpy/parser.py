from sly import Parser


from lexer import ITCHLexer
import itch_ast as i_ast


class ITCHParser(Parser):
    # Get the token list from the lexer (required)
    tokens = ITCHLexer.tokens
    
    # debugfile = 'parser.out'

    @_('declaration_specifiers init_declarator_list_opt')
    def p_decl_body(self, p):
        spec = p[1]

        # p[2] (init_declarator_list_opt) is either a list or None
        #
        if p[2] is None:
            # By the standard, you must have at least one declarator unless
            # declaring a structure tag, a union tag, or the members of an
            # enumeration.
            #
            ty = spec['type']
            s_or_e = (i_ast.Struct, i_ast.Enum)
            if len(ty) == 1 and isinstance(ty[0], s_or_e):
                decls = [i_ast.Decl(
                    name=None,
                    quals=spec['qual'],
                    storage=spec['storage'],
                    funcspec=spec['function'],
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

    # Since each declaration is a list of declarations, this
    # rule will combine all the declarations and return a single
    # list
    #
    @_('declaration_list declaration',
       'declaration_list declaration_list declaration')
    def declaration_list(self, p):
        p[0] = p[1] if len(p) == 2 else p[1] + p[2]

    # Grammar rules and actions
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
    
    @_('CHAR',
       'USHORT',
       'SHORT',
       'ULONG',
       'LONG',
       'DOUBLE')
    def typeid(self, p):
        return p[0]

    
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