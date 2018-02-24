from hansel._utils import _yield_items


def test__yield_items():
    # for (literal_text, field_name, format_spec, conversion) in fmt.parse(crumb_path):
    # (txt, fld, fmt, conv)
    assert [('/data/', 'crumb', '', None), ('/file/', 'img', '', None)] == \
           list(_yield_items("/data/{crumb}/file/{img}"))

    assert [('/data/crumb/file/img', None, None, None)] == list(_yield_items('/data/crumb/file/img'))
