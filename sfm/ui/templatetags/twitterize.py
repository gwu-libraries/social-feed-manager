from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='twitterize')
@stringfilter
def twitterize(value, autoescape=None):
    from django.utils.html import urlize
    import re
    # Link URLs
    value = urlize(value, nofollow=False, autoescape=autoescape)
    # Link twitter usernames prefixed with @
    value = re.sub(r'(\s+|\A)@([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://twitter.com/\2">@\2</a>',value)
    # Link hash tags
    value = re.sub(r'(\s+|\A)#([a-zA-Z0-9\-_]*)\b',r'\1<a href="http://twitter.com/search?q=%23\2">#\2</a>',value)
    return mark_safe(value)
twitterize.is_safe=True
twitterize.needs_autoescape = True
