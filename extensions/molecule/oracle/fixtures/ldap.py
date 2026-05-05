import json
import os


OPT_REFERRALS = 8
SCOPE_SUBTREE = 2
SCOPE_ONELEVEL = 1


class LDAPError(Exception):
    pass


class _Connection:
    def __init__(self, uri):
        self.uri = uri

    def set_option(self, option, value):
        return None

    def simple_bind_s(self, binddn, password):
        return None

    def search_s(self, basedn, scope, filterstr, attrlist):
        fixture = os.environ.get("MOLECULE_LDAP_FIXTURE")
        if not fixture:
            raise LDAPError("MOLECULE_LDAP_FIXTURE is not set")

        with open(fixture, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = []
        for item in data:
            attrs = {}
            for key, value in item["attributes"].items():
                if isinstance(value, list):
                    values = value
                else:
                    values = [value]

                encoded = []
                for v in values:
                    if isinstance(v, bytes):
                        encoded.append(v)
                    else:
                        encoded.append(str(v).encode("utf-8"))
                attrs[key] = encoded

            result.append((item["dn"], attrs))
        return result

    def unbind(self):
        return None


def initialize(uri):
    return _Connection(uri)
