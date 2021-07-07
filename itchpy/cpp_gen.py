

class CPPGenerator(object):
    """Uses the same visitor pattern as itch_ast.NodeVisitor, but modified to
    return a value from each visit method, using string accumulation in
    generic_visit.
    """

    def __init__(self):
        """Constructs CPP-parser"""
        # Statements start with indentation of self.indent_level spaces, using
        # the _make_indent method.
        self.indent_level = 0

    def _make_indent(self):
        return " " * self.indent_level

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        if node is None:
            return ""
        else:
            return "".join(self.visit(c) for c_name, c in node.children())

    def visit_ID(self, n):
        return n.name

    def visit_Enum(self, n):
        members = None if n.values is None else n.values.enumerators
        s = "enum " + (n.name or "")
        if members is not None:
            # None means no members
            # Empty sequence means an empty list of members
            s += "\n"
            s += self._make_indent()
            self.indent_level += 2
            s += "{\n"
            s += self._generate_enum_body(members)
            self.indent_level -= 2
            s += self._make_indent() + "}"
        return s

    def visit_Enumerator(self, n):
        if not n.value:
            return f"{self._make_indent()}{n.name},\n"
        else:
            return f"{self._make_indent()}{n.name} = {self.visit(n.value)},\n"

    def visit_FileAST(self, n):
        s = ""
        for decl in n.decls:
            s += self.visit(decl) + "\n"
        return s

    def visit_FieldDecl(self, n):
        s = f"{self.visit(n.type)} {n.name}"
        return s

    def visit_Struct(self, n):
        s = "struct " + (n.name or "")
        if n.fields is not None:
            # None means no members
            # Empty sequence means an empty list of members
            s += "\n"
            s += self._make_indent()
            self.indent_level += 2
            s += "{\n"
            s += self._generate_struct_body(n.fields)
            self.indent_level -= 2
            s += self._make_indent() + "}"
        return s

    def _generate_struct_body(self, members):
        return "".join(self._generate_stmt(member) for member in members)

    def _generate_enum_body(self, members):
        # `[:-2] + '\n'` removes the final `,` from the enumerator list
        return "".join(self.visit(value) for value in members)[:-2] + "\n"

    def _generate_stmt(self, n, add_indent=False):
        """Generation from a statement node."""
        if add_indent:
            self.indent_level += 2
        indent = self._make_indent()
        if add_indent:
            self.indent_level -= 2
        return indent + self.visit(n) + ";\n"


if __name__ == "__main__":

    from .lexer import ITCHLexer
    from .parser import ITCHParser

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

    lexer = ITCHLexer()

    parser = ITCHParser()

    ast = parser.parse(lexer.tokenize(data))

    generator = CPPGenerator()

    print(generator.visit(ast))
