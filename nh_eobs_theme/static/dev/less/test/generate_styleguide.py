__author__ = 'colin'
import pykss
from jinja2 import Template

styleguide = pykss.Parser('css/files/')
tmpl = open('styleguide_template.html', 'r').read()
jquery = open('js/jquery.js', 'r').read()
jquery_scrollspy = open('js/jquery-scrollspy.js', 'r').read()
template = Template(tmpl.decode('utf-8').encode('ascii','ignore'))
styleguide_render = template.render(sections=sorted(styleguide.sections.items()),
                                    nav_sections=sorted(styleguide.sections.items()),
                                    css_sections=sorted(styleguide.sections.items()),
                                    jquery=jquery,
                                    jquery_scrollspy=jquery_scrollspy)
styleguide_file = open('styleguide.html', 'w')
styleguide_file.write(styleguide_render)
styleguide_file.close()