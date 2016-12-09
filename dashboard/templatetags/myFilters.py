from django import template

register = template.Library()


@register.filter
def has_secondary_role(query, role):
    """
    Checks if member has 'role' in the secondary_roles
    :param query: member.secondary_role query
    :param role: role to be checked
    :return: True if member has role
    """
    count = query.filter(short_name=role).count()
    return count > 0
