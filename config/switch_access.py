LOGIN_SCENARIO = {
    "https_ldap": {"authentication": "ldap", "secure_access": True},
    "http_ldap": {"authentication": "ldap", "secure_access": False},
    "https_local": {"authentication": "local", "secure_access": True},
    "http_local": {"authentication": "local", "secure_access": False}
}

SWITCH_ACCESS = {
    "10.213.164.101": LOGIN_SCENARIO["http_local"],
    "10.213.164.102": LOGIN_SCENARIO["http_local"]
}


