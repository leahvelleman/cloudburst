import re
import pynini

def _constructiveOp(op):
    def innerFunction(self, other):
        cls = type(self)
        return cls.fromFSM(op(self._fsm, other._fsm))
    return innerFunction




def pynini_decode(inputBytes):
    """ Pynini often outputs bytestrings with unprintable characters
    represented in an unusual way. Run them through this to get plain unicode.
    """
    asString = inputBytes.decode("utf8")
    asTokens = (from_att_symbol(symbol) for symbol in asString.split(' '))
    return "".join(asTokens)

def from_att_symbol(string):
    """ OpenFST outputs symbol table representations in an awkward
    format. Attempt to deal with that gracefully. """
    # pylint: disable=too-many-return-statements
    if string.startswith("<0"):
        return six.unichr(int(string.strip('<>'), 16))
    if string.startswith("<") and string.endswith(">"):
        return {
            "NUL": chr(0),  "":    chr(0),  "epsilon": chr(0),
            "SOH": chr(1),  "STX": chr(2),  "ETX": chr(3),  "EOT": chr(4),
            "ENQ": chr(5),  "ACK": chr(6),  "BEL": chr(7),  "BS":  chr(8),
            "HT":  chr(9),  "LF":  chr(10), "VT":  chr(11), "FF":  chr(12),
            "CR":  chr(13), "SO":  chr(14), "SI":  chr(15), "DLE": chr(16),
            "DC1": chr(17), "DC2": chr(18), "DC3": chr(19), "DC4": chr(20),
            "NAK": chr(21), "SYN": chr(22), "ETB": chr(23), "CAN": chr(24),
            "EM":  chr(25), "SUB": chr(26), "ESC": chr(27), "FS":  chr(28),
            "GS":  chr(29), "RS":  chr(30), "US":  chr(31), "SPACE": chr(32),
            "DEL": chr(127)
        }[string.strip('<>')]
    if len(string) > 1:
        return "[" + string + "]"
    if string == "[":
        return "\\["
    if string == "]":
        return "\\]"
    if string == "\\":
        return "\\\\"
    return string
