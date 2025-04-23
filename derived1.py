import sys
from cdiagram import Diagram,MatrixDiagram
from jinja2 import Template,FileSystemLoader,Environment

from cdutils import triangle_over

env=Environment(loader=FileSystemLoader('.'),
    line_statement_prefix='%%',variable_start_string='<<',variable_end_string='>>')
t=env.get_template('graphs.tex')

d1=Diagram()
d1.add_node('a',(0,0),label_angle=-45)
d1.add_node('b',(1,0),label_angle=225)
d1.add_arrow('a','b',shape='->',naput='2',color='red')
d1.add_circle('a',position='l',shape='->',nbput='1',color='blue')
d1.add_circle('b',position='r',shape='<-',nbput='1')

d2=MatrixDiagram()
d2.node('a2',label='(a,2)',label_angle=90)
d2.skip(2)
d2.node('b1',label='(b,1)',label_angle=90)
d2.cr()
d2.skip()
d2.node('a1',label='(a,1)',label_angle=180,labelsep='5pt')
d2.node('b0',label='(b,0)',label_angle=0,labelsep='3pt')
d2.cr()
d2.node('a0',label='(a,0)',label_angle=270)
d2.skip(2)
d2.node('b2',label='(b,2)',label_angle=270)
for src in range(3):
    d2.add_arrow('a%d' % src, 'b%d' % ((src+2)%3),shape='->',color='red',naput=src)
    d2.add_arrow('a%d' % src, 'a%d' % ((src+1)%3),shape='->',color='blue',nbput=src)
    d2.add_arrow('b%d' % src, 'b%d' % ((src+1)%3),shape='->',naput=src)
d1.cluster_all().shift((1,3))
sys.stdout.write(t.render(diags=(d1,d2,)))



