import re
import string

def _template_pass(template, params):
    match_pairs = re.findall('(\${([^}]*)})', template)
    any_changes = False
    for (mtch, name) in match_pairs:
        if name not in params:
            raise ValueError("Template required not-provided param %s." % name)
        template = template.replace(mtch, params[name])
        any_changes = True
    return (template, any_changes)

def fill_template(template, params):
    template, another = _template_pass(template, params)
    while another:
        template, another = _template_pass(template, params)
    return template
