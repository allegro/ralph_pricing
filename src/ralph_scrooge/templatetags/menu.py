from django import template


register = template.Library()


def main_menu(items, selected, title=None, search=None, white=False,
              position='', title_url="/"):
    """
    Show main menu bar.
    :param items: The list of :class:`bob.menu.MenuItem` instances to show.
    :param selected: The :data:`name` of the currently selected item.
    :param title: The title to show in the menu bar.
    :param search: The URL for the search form.
    :param white: If True, the menu bar will be white.
    :param position: Empty, or one of ``'fixed'``, ``'static'``, ``'bottom'``.
    """
    positions = {
        'static': 'navbar-static-top',
        'fixed': 'navbar-fixed-top',
        'bottom': 'navbar-fixed-bottom',
    }
    klass = ['navbar', positions.get(position, '')]
    if not white:
        klass.append('navbar-inverse')

    return {
        'items': items,
        'selected': selected,
        'title': title,
        'search': search,
        'position': position,
        'white': bool(white),
        'title_url': title_url,
        'class': ' '.join(klass),
    }

register.inclusion_tag(
    'ralph_scrooge/main_menu.html', name='main_menu_bs3fake'
)(main_menu)
