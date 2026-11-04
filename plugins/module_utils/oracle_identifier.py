# -*- coding: utf-8 -*-
# Handling of Oracle identifiers (names of users, profiles, jobs, ...) for the
# modules of opitzconsulting.ansible_oracle.
# Like in SQL (ANSI), an identifier in double quotes is case sensitive, otherwise it is
# converted to uppercase.
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

# one part of a qualified name: in double quotes or letters, digits, _, $ and #
IDENTIFIER_PART = r'(?:"[^"]+"|[A-Za-z0-9_$#]+)'


def normalize_identifier(name, convert_to_upper=True):
    """Return the identifier as stored in the data dictionary.

    - in double quotes: without the quotes, case sensitive
    - otherwise: in uppercase (or unchanged with convert_to_upper=False)
    """
    if len(name) > 1 and name.startswith('"') and name.endswith('"'):
        return name[1:-1]
    return name.upper() if convert_to_upper else name


def quote_identifier(name):
    """Quote a normalized identifier for SQL statements.

    Always quoted, so names with special characters like '/' are possible.
    """
    return '"%s"' % name


def split_qualified_identifier(name, convert_to_upper=True):
    """Split OWNER.NAME into the normalized parts [owner, name].

    Each part can be in double quotes (case sensitive).
    Returns None, if name is no valid qualified name.
    """
    match = re.match(r'^(%s)\.(%s)$' % (IDENTIFIER_PART, IDENTIFIER_PART), name)
    if not match:
        return None
    return [normalize_identifier(part, convert_to_upper) for part in match.groups()]


def split_object_identifier(name, default_owner):
    """Split [OWNER.]NAME into the normalized parts [owner, name].

    Each part can be in double quotes (case sensitive).
    Without OWNER, default_owner (already normalized) is used.
    Returns None, if name is no valid object name.
    """
    match = re.match(
        r'^(?:(%s)\.)?(%s)$' % (IDENTIFIER_PART, IDENTIFIER_PART), name.strip()
    )
    if not match:
        return None
    owner, object_name = match.groups()
    return [
        normalize_identifier(owner) if owner else default_owner,
        normalize_identifier(object_name),
    ]
