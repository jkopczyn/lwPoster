import regex
import string

def template_pass(template, params):
    match_pairs = regex.match('${([^}]*)}', template)
    any_changes = False
    for (mtch, name) in match_pairs:
        if name not in params:
            raise ValueError("Template required not-provided param %s." % name)
        template = string.replace(template, mtch, params[name])
        any_changes = True
    return (template, any_changes)

def fill_template(template, params):
    template, another = template_pass(template, params)
    while another:
        template, another = template_pass(template, params)
    return template
