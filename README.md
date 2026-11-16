# python3-ipex-b2b

Python client for the [IPEX B2B REST API](https://restapi.ipex.cz/documentation) (swagger 8.113.2).
Python counterpart of the PHP library [ipex-b2b](https://github.com/Spoje-NET/ipex-b2b).

```sh
apt install python3-ipex-b2b     # or: pip install ipex-b2b
```

```python
from ipexb2b import Ipex

ipex = Ipex()                      # IPEX_URL / IPEX_LOGIN / IPEX_PASSWORD from the environment
customers = ipex.list_customers(fulltext="Novak", page=1)
calls = ipex.get_calls(dateFrom="2026-11-01 00:00:00", number="420123456789")
ipex.add_voip_credit("420123456789", body={"amount": 100})   # PUT /v1/voip/{number}/credit
```

* One method per API operation, named in `ipexb2b/operations.py` (path parameters are positional,
  query parameters keyword arguments, JSON body as `body=`). Anything else: `ipex.call("GET", "/v1/...")`.
* Login (`POST /v1/token`) is lazy; the token is sent as is in `Authorization`, refreshed before expiry
  and once after an HTTP 401.
* Errors are `IpexError` / `IpexAuthError`; credentials and tokens never appear in messages or `repr`.
* `IPEX_VERIFY_SSL=false` disables TLS verification (IPEX test endpoints use self-signed certificates).

Used by [mcp-server-ipex](https://github.com/Spoje-NET/mcp-server-ipex). License: MIT.
