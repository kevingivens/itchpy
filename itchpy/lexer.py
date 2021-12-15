from sly import Lexer


class ITCHLexer(Lexer):
    # Set of token names
    tokens = {
        # Identifiers
        ID,
        # Delimeters
        LBRACE,  # {
        RBRACE,  # }
        COMMA,  # ,
        SEMI,  # ;
        COLON,  # :
        # Assignment
        # ASSIGN,
        # Keywords
        ENUM,
        STRUCT,
        # Types
        CHAR,  # 1 byte
        USHORT,  # 2 bytes, unsigned
        SHORT,  # 2 bytes, signed
        ULONG,  # 4 bytes, unsigned
        LONG,  # 4 bytes, signed
        DOUBLE,  # 8 bytes, floating point
        TIME  # 8 bytes, converted from 6 bytes on the wire
        # NUMBER,
    }

    # String containing ignored characters between tokens
    ignore = " \t"

    # Other ignored patterns
    ignore_comment = r"\#.*"

    # Identifiers and keywords
    ID = r"[a-zA-Z_][a-zA-Z0-9_]*"

    # keywords
    ID["enum"] = ENUM
    ID["struct"] = STRUCT

    # types
    ID["char"] = CHAR
    ID["ushort"] = USHORT
    ID["short"] = SHORT
    ID["ulong"] = ULONG
    ID["long"] = LONG
    ID["double"] = DOUBLE
    ID["time"] = TIME

    # ASSIGN = r'='

    # Delimeters
    LBRACE = r"\{"
    RBRACE = r"\}"
    COMMA = r","
    SEMI = r";"
    COLON = r":"
    # NUMBER  = r'\d+'
    # INT = r'^[0-9]+$'

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.errors.append(t.value)
        self.index += 1
        if hasattr(self, "return_error"):
            return t

    def __init__(self):
        self.errors = []

