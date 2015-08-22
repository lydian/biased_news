from pyramid.view import view_config


@view_config(route_name='articles', renderer='templates/keywords.jinja2')
def my_view(request):
    return {'name': 'biased_news'}
