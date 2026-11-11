"""Minimal S-expression reader/writer and KiCad symbol library helpers."""
import re

SYMDIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
FPDIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"


class Sym(str):
    """Unquoted atom."""


def parse(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif t[0] == '"':
            cur.append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\"))
        else:
            cur.append(Sym(t))
    return cur[0]


def dump(node, indent=0):
    pad = "\t" * indent
    if not isinstance(node, list):
        if isinstance(node, Sym):
            return str(node)
        if isinstance(node, (int, float)):
            return fmt(node)
        return '"' + str(node).replace("\\", "\\\\").replace('"', '\\"') + '"'
    if all(not isinstance(x, list) for x in node):
        return "(" + " ".join(dump(x) for x in node) + ")"
    head = []
    i = 0
    while i < len(node) and not isinstance(node[i], list):
        head.append(dump(node[i]))
        i += 1
    out = pad + "(" + " ".join(head)
    for ch in node[i:]:
        if isinstance(ch, list):
            out += "\n" + pad + "\t" + dump(ch, indent + 1).lstrip("\t")
        else:
            out += " " + dump(ch)
    out += "\n" + pad + ")"
    return out


def fmt(v):
    if isinstance(v, int):
        return str(v)
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def find(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


_libs = {}


def lib(name):
    if name not in _libs:
        _libs[name] = parse(open(f"{SYMDIR}/{name}.kicad_sym").read())
    return _libs[name]


def get_symbol(libname, sym):
    """Return flattened symbol node (extends resolved), named libname:sym."""
    L = lib(libname)
    for s in find(L, "symbol"):
        if s[1] == sym:
            break
    else:
        raise KeyError(f"{libname}:{sym}")
    ext = find(s, "extends")
    if not ext:
        return s
    parent = get_symbol(libname, ext[0][1])
    base = parent[1]
    out = [Sym("symbol"), sym]
    props = {p[1]: p for p in find(s, "property")}
    for c in parent[2:]:
        if c[0] == "property" and c[1] in props:
            out.append(props.pop(c[1]))
        elif c[0] == "symbol":
            c = list(c)
            c[1] = sym + c[1][len(base):]
            out.append(c)
        else:
            out.append(c)
    out += list(props.values())
    return out


def pins(sym):
    """Return {number: (name, x, y, angle, type)} from flattened symbol."""
    res = {}
    for u in find(sym, "symbol"):
        for p in find(u, "pin"):
            at = find(p, "at")[0]
            num = find(p, "number")[0][1]
            name = find(p, "name")[0][1]
            nums = [n.strip() for n in num[1:-1].split(",")] if num.startswith("[") else [num]
            for n in nums:
                res[n] = (name, float(at[1]), float(at[2]), float(at[3]), p[1], float(find(p, "length")[0][1]))
    return res
