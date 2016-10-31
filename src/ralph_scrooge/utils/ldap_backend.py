from django_auth_ldap import backend


class ScroogeLDAPBackend(backend.LDAPBackend):
    # add new settings - AUTH_LDAP_GROUP_MAPPING (django-auth-ldap will fetch
    # it automatically from Scrooge settings)
    default_settings = dict(
        GROUP_MAPPING={}  # LDAP group -> Django group mapping
    )
