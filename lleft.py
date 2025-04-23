import sys
from cdiagram import Diagram,MatrixDiagram
from jinja2 import Template,FileSystemLoader,Environment

from cdutils import triangle_over

env=Environment(loader=FileSystemLoader('.'),
    line_statement_prefix='%%',variable_start_string='<<',variable_end_string='>>')
t=env.get_template('graphs.tex')

d1=Diagram()
d1.add_node('a',(0,0),label='0',label_angle=-135)
d1.add_node('b',(1,0),label='0',label_angle=-45)
pos_c=triangle_over(d1['a'],d1['b'])
d1.add_node('c',(pos_c[0],pos_c[1]),label_angle=90,label='1')
d1.add_arrow('b','a',shape='->')
d1.add_arrow('a','c',shape='->')
d1.add_arrow('c','b',shape='->')

d2=Diagram()
d2.add_node('a',(0,0),label=' ')
d2.add_node('b',(1,0),label=' ')
pos_c=triangle_over(d2['a'],d2['b'])
d2.add_node('c',(pos_c[0],pos_c[1]),label=' ')
d2.add_arrow('b','a',shape='->',naput='0')
d2.add_arrow('a','c',shape='->',naput='1')
d2.add_arrow('c','b',shape='->',naput='2')
d2.cluster_all().shift((1.5,0))

sys.stdout.write(t.render(diags=(d1,d2,)))



