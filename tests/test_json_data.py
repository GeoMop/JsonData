from json_data import *

import sys

print("PYTHONPATH: ", sys.path)

import pytest
import json

# TODO: deserialize tests
# - better structure, use unittest module

def test_json_data():
    # create, serialize
    @jsondata
    class A:
        a: int = 1
        b: str = "test"
        c: float = 2.0

        def __attrs_post_init__(self):
            self._u = 5

    a = A.deserialize({"a": 2})

    assert a.a == 2
    assert a.b == "test"
    assert a.c == 2.0
    assert a._u == 5

    dumped = json.dumps(a.serialize(), sort_keys=True)
    assert  dumped == '{"__class__": "A", "a": 2, "b": "test", "c": 2.0}'

    # JsonData object
    @jsondata
    class B:
        a: int = 1
        b: A = attr.ib(factory=A)

    b = B.deserialize({"a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa"}})

    assert b.a == 2
    assert b.b.__class__ is A
    assert b.b.a == 3
    assert b.b.b == "aaa"

    assert json.dumps(b.serialize(), sort_keys=True) ==\
        '{"__class__": "B", "a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa", "c": 2.0}}'

    # ClassFactory
    @jsondata
    class A2:
        x: int = 2
        y: str = "test2"

    @jsondata
    class C:
        a: int = 1
        b: Union[A, A2] = attr.ib(factory=A)

    c = C.deserialize({"a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa"}})

    assert c.a == 2
    assert c.b.__class__ is A
    assert c.b.a == 3
    assert c.b.b == "aaa"

    assert json.dumps(c.serialize(), sort_keys=True) ==\
        '{"__class__": "C", "a": 2, "b": {"__class__": "A", "a": 3, "b": "aaa", "c": 2.0}}'

    # dict
    @jsondata
    class D:
        a: int = 1
        b: Dict[str, int] = {"a": 1, "b": 2}

    d = D.deserialize({"a": 2, "b": {"c": 3, "d": 4}})

    assert d.a == 2
    assert isinstance(d.b, dict)
    assert d.b == {"c": 3, "d": 4}

    assert json.dumps(d.serialize(), sort_keys=True) ==\
        '{"__class__": "D", "a": 2, "b": {"c": 3, "d": 4}}'

    # dict with int index
    @jsondata
    class D2:
        a: int = 1
        b: Dict[int, int] = {1: 1, 2: 2}

    d = D2.deserialize({"a": 2, "b": {"3": 3, "4": 4}})

    assert d.a == 2
    assert isinstance(d.b, dict)
    assert d.b == {3: 3, 4: 4}

    assert json.dumps(d.serialize(), sort_keys=True) ==\
        '{"__class__": "D2", "a": 2, "b": {"3": 3, "4": 4}}'

    # list in list in dict
    @jsondata
    class D3:
        a: int = 1
        b: Dict[str, List[List[int]]] = {"a": [[1]]}

    d2 = D3.deserialize({"a": 2, "b": {"a": [[6, 7]], "c": [[2, 3], [4, 5]]}})

    assert d2.b["c"][0][0] == 2
    assert d2.b["c"][1][1] == 5

    assert json.dumps(d2.serialize(), sort_keys=True) ==\
        '{"__class__": "D3", "a": 2, "b": {"a": [[6, 7]], "c": [[2, 3], [4, 5]]}}'

    # empty list
    # @jsondata
    # class E:
    #     a: int = 1
    #     b: List[Any] = []
    #
    # e = E.deserialize({"a": 2, "b": [1, 2.0, "aaa"]})
    #
    # assert e.b[0] == 1
    # assert e.b[1] == 2.0
    # assert e.b[2] == "aaa"
    #
    # assert json.dumps(e.serialize(), sort_keys=True) == '{"__class__": "E", "a": 2, "b": [1, 2.0, "aaa"]}'

    # list with one item
    @jsondata
    class E2:
        a: int = 1
        b: List[A] = [A({"a": 2})]

    e2 = E2.deserialize({"a": 2, "b": [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]})

    assert e2.b[0].__class__ == A
    assert e2.b[0].a == 3
    assert e2.b[1].a == 5

    assert json.dumps(e2.serialize(), sort_keys=True) ==\
        '{"__class__": "E2", "a": 2, "b": [{"__class__": "A", "a": 3, "b": "test", "c": 2.0}, ' \
        '{"__class__": "A", "a": 5, "b": "test", "c": 2.0}]}'

    # tuple
    @jsondata
    class F:
        a: int = 1
        b: Tuple[int, float, A] = (1, 2.0, A({"a": 2}))

    f = F.deserialize({"a": 2, "b": [2, 3.0, {"__class__": "A", "a": 3}]})

    assert isinstance(f.b, tuple)
    assert f.b[0] == 2
    assert f.b[2].__class__ is A
    assert f.b[2].a == 3

    assert json.dumps(f.serialize(), sort_keys=True) ==\
        '{"__class__": "F", "a": 2, "b": [2, 3.0, {"__class__": "A", "a": 3, "b": "test", "c": 2.0}]}'

    # WrongKeyError
    try:
        a = A({"a": 2, "d": 3})
        assert False
    #except WrongKeyError:
    except:
        pass

    # recursion
    @jsondata
    class G:
        a: int = 1
        b: Tuple[int, float, List[A]] = (1, 2.0, [A({"a": 2})])

    g = G.deserialize({"a": 2, "b": [2, 3.0, [{"__class__": "A", "a": 3}, {"__class__": "A", "a": 5}]]})

    assert isinstance(g.b, tuple)
    assert g.b[1] == 3.0
    assert g.b[2].__class__ is list
    assert g.b[2][1].__class__ is A
    assert g.b[2][1].a == 5

    assert json.dumps(g.serialize(), sort_keys=True) ==\
        '{"__class__": "G", "a": 2, "b": [2, 3.0, [{"__class__": "A", "a": 3, "b": "test", "c": 2.0}, ' \
        '{"__class__": "A", "a": 5, "b": "test", "c": 2.0}]]}'

    # IntEnum
    class MyEnum(IntEnum):
        E1 = 1
        E2 = 2
        E3 = 3

    @jsondata
    class I:
        a: int = 1
        b: str = "test"
        c: MyEnum = MyEnum.E1

    i = I.deserialize({"a": 2, "c": {"__class__": "MyEnum", "item_name": "E2"}})

    assert i.a == 2
    assert i.b == "test"
    assert i.c == MyEnum.E2

    assert json.dumps(i.serialize(), sort_keys=True) == '{"__class__": "I", "a": 2, "b": "test", ' \
                                                        '"c": {"__class__": "MyEnum", "item_name": "E2"}}'


def test_dict_modification():
    @jsondata
    class A:
        a: int = 1
        c: Dict[str, int] = {'x':1, 'y':2}

    a = A.deserialize(dict(a=2))
    assert a.a == 2
    assert a.c == {'x':1, 'y':2}


def test_without_type():
    # JsonData object
    @jsondata
    class A:
        a: int = 1

    @jsondata
    class B:
        b: str = "a"

    a = deserialize({"__class__": "A", "__module__": "__name__", "a": 2}, cls_dict={("__name__", "A"): A, ("__name__", "B"): B})
    assert a.a == 2

    # base types
    b = 2
    assert deserialize(b) == b

    # dicts
    d = {"a": 1, "b": 2}
    assert deserialize(d) == d

    # lists
    l = [2, 3, 4]
    assert deserialize(l) == l

    # IntEnum
    class E(IntEnum):
        E1 = 1
        E2 = 2

    e = deserialize({"__class__": "E", "__module__": "__name__", "item_name": "E2"}, cls_dict={("__name__", "A"): A, ("__name__", "E"): E})
    assert e == E.E2


def test_modules():
    from modules import module1, module2

    a = module1.A(a=2)
    dumped = json.dumps(a.serialize(module=True), sort_keys=True)
    assert dumped == '{"__class__": "A", "__module__": "modules.module1", "a": 2}'

    b = deserialize(json.loads(dumped), type=Union[module1.A, module2.A])
    assert b.__class__ is module1.A
