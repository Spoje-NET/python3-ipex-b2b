import time

import pytest

from ipexb2b import BY_NAME, OPERATIONS, Ipex, IpexAuthError, IpexError


class FakeResp:
    def __init__(self, status=200, data=None, text=""):
        self.status_code = status
        self._data = data
        self.text = text or ("x" if data is not None else "")
        self.content = b"x" if data is not None or text else b""

    def json(self):
        if self._data is None:
            raise ValueError
        return self._data


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kw):
        self.calls.append(("POST", url, kw))
        return self.responses.pop(0)

    def request(self, method, url, **kw):
        self.calls.append((method, url, kw))
        return self.responses.pop(0)


def token(exp=None):
    return FakeResp(200, {"accessToken": "TOK", "expire": exp or time.time() + 600})


def client(responses):
    s = FakeSession(responses)
    return Ipex("https://x.test", "user", "secret-pw", session=s), s


def test_operations_unique_and_parse():
    names = [o.name for o in OPERATIONS]
    assert len(names) == len(set(names)) > 100
    assert BY_NAME["add_voip_credit"].method == "PUT"
    assert BY_NAME["add_voip_credit"].path_params == ("number",)
    assert BY_NAME["get_calls"].required_query == ("dateFrom",)


def test_login_and_raw_authorization_header():
    c, s = client([token(), FakeResp(200, [{"id": 1}])])
    assert c.list_customers(page=1) == [{"id": 1}]
    assert s.calls[1][2]["headers"]["Authorization"] == "TOK"  # no Bearer
    assert s.calls[1][2]["params"] == {"page": 1}


def test_path_and_body():
    c, s = client([token(), FakeResp(200, {"ok": True})])
    c.add_voip_credit("420123", body={"amount": 100})
    method, url, kw = s.calls[1]
    assert (method, url) == ("PUT", "https://x.test/v1/voip/420123/credit")
    assert kw["json"] == {"amount": 100}


def test_required_and_unknown_params():
    c, _ = client([])
    with pytest.raises(TypeError):
        c.get_calls()
    with pytest.raises(TypeError):
        c.list_customers(bogus=1)


def test_refresh_on_401():
    c, s = client([token(), FakeResp(401, {"message": "expired"}), token(), FakeResp(200, {"a": 1})])
    assert c.get_rights() == {"a": 1}
    assert len([x for x in s.calls if x[0] == "POST"]) == 2


def test_errors_do_not_leak_secrets():
    c, _ = client([FakeResp(403)])
    with pytest.raises(IpexAuthError) as e:
        c.get_rights()
    assert "secret-pw" not in str(e.value) and "secret-pw" not in repr(c)
    c, _ = client([token(), FakeResp(500, {"message": "boom"})])
    with pytest.raises(IpexError) as e:
        c.get_rights()
    assert e.value.status == 500 and "boom" in str(e.value)


def test_missing_credentials(monkeypatch):
    monkeypatch.delenv("IPEX_LOGIN", raising=False)
    monkeypatch.delenv("IPEX_PASSWORD", raising=False)
    with pytest.raises(IpexAuthError):
        Ipex("https://x.test", session=FakeSession([])).get_rights()
