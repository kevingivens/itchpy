import sys

# adapter from pycparser


def _repr(obj):
    """
    Get the representation of an object, with dedicated pprint-like format for lists.
    """
    if isinstance(obj, list):
        return "[" + (",\n ".join((_repr(e).replace("\n", "\n ") for e in obj))) + "\n]"
    else:
        return repr(obj)


class NodeVisitor(object):
    """A base NodeVisitor class for visiting c_ast nodes.
    Subclass it and define your own visit_XXX methods, where
    XXX is the class name you want to visit with these
    methods.
    For example:
    class ConstantVisitor(NodeVisitor):
        def __init__(self):
            self.values = []
        def visit_Constant(self, node):
            self.values.append(node.value)
    Creates a list of values of all the constant nodes
    encountered below the given node. To use it:
    cv = ConstantVisitor()
    cv.visit(node)
    Notes:
    *   generic_visit() will be called for AST nodes for which
        no visit_XXX method was defined.
    *   The children of nodes for which a visit_XXX was
        defined will not be visited - if you need this, call
        generic_visit() on the node.
        You can use:
            NodeVisitor.generic_visit(self, node)
    *   Modeled after Python's own AST visiting facilities
        (the ast module of Python 3.0)
    """

    _method_cache = None

    def visit(self, node):
        """Visit a node."""

        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = "visit_" + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a
        node. Implements preorder visiting of the node.
        """
        for c in node:
            self.visit(c)


class Node(object):
    __slots__ = ()
    """ Abstract base class for AST nodes.
    """

    def __repr__(self):
        """Generates a python representation of the current node"""
        result = self.__class__.__name__ + "("

        indent = ""
        separator = ""
        for name in self.__slots__[:-2]:
            result += separator
            result += indent
            result += (
                name
                + "="
                + (
                    _repr(getattr(self, name)).replace(
                        "\n",
                        "\n  " + (" " * (len(name) + len(self.__class__.__name__))),
                    )
                )
            )

            separator = ","
            indent = "\n " + (" " * len(self.__class__.__name__))

        result += indent + ")"

        return result

    def children(self):
        """A sequence of all children that are Nodes"""
        pass

    def show(
        self,
        buf=sys.stdout,
        offset=0,
        attrnames=False,
        nodenames=False,
        showcoord=False,
        _my_node_name=None,
    ):
        """Pretty print the Node and all its attributes and
        children (recursively) to a buffer.
        buf:
            Open IO buffer into which the Node is printed.
        offset:
            Initial offset (amount of leading spaces)
        attrnames:
            True if you want to see the attribute names in
            name=value pairs. False to only see the values.
        nodenames:
            True if you want to see the actual node names
            within their parents.
        showcoord:
            Do you want the coordinates of each Node to be
            displayed.
        """
        lead = " " * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__ + " <" + _my_node_name + ">: ")
        else:
            buf.write(lead + self.__class__.__name__ + ": ")

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self, n)) for n in self.attr_names]
                attrstr = ", ".join("%s=%s" % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ", ".join("%s" % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(" (at %s)" % self.coord)
        buf.write("\n")

        for (child_name, child) in self.children():
            child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name,
            )


class Assignment(Node):
    __slots__ = ("op", "lvalue", "rvalue", "coord", "__weakref__")

    def __init__(self, op, lvalue, rvalue, coord=None):
        self.op = op
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.coord = coord

    def children(self):
        nodelist = []
        if self.lvalue is not None:
            nodelist.append(("lvalue", self.lvalue))
        if self.rvalue is not None:
            nodelist.append(("rvalue", self.rvalue))
        return tuple(nodelist)

    def __iter__(self):
        if self.lvalue is not None:
            yield self.lvalue
        if self.rvalue is not None:
            yield self.rvalue

    attr_names = ("op",)


class Decl(Node):
    __slots__ = ("name", "type", "init", "coord", "__weakref__")

    def __init__(self, name, type, init, coord=None):
        self.name = name
        self.type = type
        self.init = init
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None:
            nodelist.append(("type", self.type))
        if self.init is not None:
            nodelist.append(("init", self.init))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type
        if self.init is not None:
            yield self.init

    attr_names = ("name",)


class DeclList(Node):
    __slots__ = ("decls", "coord", "__weakref__")

    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in self.decls or []:
            yield child

    attr_names = ()


class Enum(Node):
    __slots__ = ("name", "values", "typeid", "coord", "__weakref__")

    def __init__(self, name, typeid, values, coord=None):
        self.name = name
        self.typeid = typeid
        self.values = values
        self.coord = coord

    def children(self):
        nodelist = []
        if self.values is not None:
            nodelist.append(("values", self.values))
        return tuple(nodelist)

    def __iter__(self):
        if self.values is not None:
            yield self.values

    attr_names = ("name",)


class Enumerator(Node):
    __slots__ = ("name", "value", "coord", "__weakref__")

    def __init__(self, name, value, coord=None):
        self.name = name
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        if self.value is not None:
            nodelist.append(("value", self.value))
        return tuple(nodelist)

    def __iter__(self):
        if self.value is not None:
            yield self.value

    attr_names = ("name",)


class EnumeratorList(Node):
    __slots__ = ("enumerators", "coord", "__weakref__")

    def __init__(self, enumerators, coord=None):
        self.enumerators = enumerators
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.enumerators or []):
            nodelist.append(("enumerators[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in self.enumerators or []:
            yield child

    attr_names = ()


class FieldDecl(Node):
    __slots__ = ("name", "type", "coord", "__weakref__")

    def __init__(self, name, type, coord=None):
        self.name = name
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None:
            nodelist.append(("type", self.type))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type

    attr_names = ("name",)


class FileAST(Node):
    __slots__ = ("decls", "coord", "__weakref__")

    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.ext or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in self.ext or []:
            yield child

    attr_names = ()


class ID(Node):
    __slots__ = ("name", "coord", "__weakref__")

    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ("name",)


class IdentifierType(Node):
    __slots__ = ("names", "coord", "__weakref__")

    def __init__(self, names, coord=None):
        self.names = names
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    def __iter__(self):
        return
        yield

    attr_names = ("names",)


class Typename(Node):
    __slots__ = ("name", "type", "coord", "__weakref__")

    def __init__(self, name, type, coord=None):
        self.name = name
        self.type = type
        self.coord = coord

    def children(self):
        nodelist = []
        if self.type is not None:
            nodelist.append(("type", self.type))
        return tuple(nodelist)

    def __iter__(self):
        if self.type is not None:
            yield self.type

    attr_names = (
        "name",
        "quals",
    )


class Struct(Node):
    __slots__ = ("name", "fields", "coord", "__weakref__")

    def __init__(self, name, fields, coord=None):
        self.name = name
        self.fields = fields
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.fields or []):
            nodelist.append(("fields[%d]" % i, child))
        return tuple(nodelist)

    def __iter__(self):
        for child in self.fields or []:
            yield child

    attr_names = ("name",)
