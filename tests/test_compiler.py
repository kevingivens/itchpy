import pytest

from itchpy.itchc import ItchCompiler

@pytest.mark.skip
def test_compiler():
    input = """
    enum Ticket: char {
        Stop, 
        Speed
    }
    struct LimitOrder {
        message_type:char;
        stock_locate:short;
        tracking_number:short;
        timestamp:time;
    }
    """
    enum_output = ""
    struct_output = """ 
#pragma pack(1):
struct LimitOrder
{
  char message_type;
  short stock_locate;
  short tracking_number;
  time timestamp;
}
pop()
"""
    comp = ItchCompiler()
    enum_file, struct_file = comp.compile(input)
    
    assert enum_file == enum_output
    assert struct_file == struct_output


