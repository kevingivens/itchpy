import sys

import click

from cpp_gen import CPPGenerator
from parser import ITCHParser
from lexer import ITCHLexer
from itch_ast import Enum, Struct


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
        enums_str = self._gen_enums()
        structs_str = self._gen_structs(enums_fp)
        parser_str = self._gen_parser(enums_fp, structs_fp)
        return enums_str, structs_str, parser_str

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
        header = f'#include "{enums_fp.name}"\n\n {self.namespace}'
        struct_str = "/n ".join(self.gen.visit_Struct(e) for e in self.structs)
        return header + "#pragma pack(push, 1):\n\n" + struct_str + "\n\n#pragma pack(pop)" + self.footer
    
    def _gen_parser(self, enums_fp, structs_fp):
        """ generate file (str) of parser """
        header = f'#pragma once\n#include "{enums_fp.name}"\n#include "{structs_fp.name}"\n\n {self.namespace}'
        header += """    enum class ParseStatus
    {
        // Message was parsed successfully and handler was invoked.
        OK,

        // The message was of a type not in the specification.
        UnknownMessageType,

        // The message was too short for the given message type and is possibly corrupted.
        Truncated,
    };
"""
        header += """ 
    template<typename MsgType, typename Handler>
    ParseStatus parseAs(const char* buf, size_t len, Handler&& handler)
    {
        if (len < sizeof(MsgType))
            return ParseStatus::Truncated;
        MsgType msg{*reinterpret_cast<const MsgType*>(buf)};
        network_to_host(msg);
        handler(msg);
        return ParseStatus::OK;
    }
"""
        body = """
    template<typename Handler>
    ParseStatus parse(const char* msg, size_t len, Handler&& handler)
    {
        if (len < 1)
            return ParseStatus::Truncated;
        switch (MessageType(msg[0])) {
"""
        for s in self.structs:
            body += f"\ncase MessageType::{s.name}:\n"
            body += f"return parseAs<{s.name}>(msg, len, std::forward<Handler>(handler));\n"
        body += """ default:
            return ParseStatus::UnknownMessageType;
        }
    }
"""
        return header + body + self.footer


@click.command()
@click.argument('itch', type=click.File('r'))
@click.argument('enums', type=click.File('w'))
@click.argument('structs', type=click.File('w'))
@click.argument('parser', type=click.File('w'))
def compile(itch, enums, structs, parser):
    """Generate C++ ITCH parser from itch specification file"""
    data = itch.read()
    comp = ItchCompiler()
    enums_str, structs_str, parser_str = comp.compile(data, enums, structs)
    enums.write(enums_str)
    structs.write(structs_str)
    parser.write(parser_str)


if __name__ == "__main__":
    compile()