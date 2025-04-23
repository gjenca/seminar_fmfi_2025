
import sys
import copy

class Position(tuple):

    def __add__(self,other):

        return Position((self[0]+other[0],self[1]+other[1]))

    def __sub__(self,other):

        return Position((self[0]-other[0],self[1]-other[1]))

    def __mul__(self,scalars):

        try:
            scalarx,scalary=scalars
        except:
            scalarx=scalars
            scalary=scalars
        return Position((self[0]*scalarx,self[1]*scalary))

class Node(dict):

    def __init__(self,name,position,label=None,**props):

        self.name=name
        self.position=Position(position)
        dict.__init__(self,props)
        if label is None:
            self['label']=name
        else:
            self['label']=label

    def shift(self,delta):

        self.position=self.position+delta

    def mul(self,mu):

        self.position=self.position*mu

    def shift_towards(self,goal,factor):

        self.shift((Position(goal)-self.position)*factor)

    def __repr__(self):

        return r'\psnode%s{%s}{%s}' %(self.position,self.name,self['label'])

class Cluster(list):

    def shift(self,delta):

        for node in self:
            node.shift(delta)
        return self

    def mul(self,mu):

        for node in self:
            node.mul(mu)
        return self

    def centroid(self):

        x=float(sum(node.position[0] for nore in self))/len(self)
        y=float(sum(node.position[1] for nore in self))/len(self)

        return x,y

    def __repr__(self):

        return 'Cluster([%s])' % ','.join(repr(node) for node in self)

class Arrow(dict):

    def __init__(self,from_node,to_node,label='',**props):

        self.from_node=from_node
        self.to_node=to_node

        if label and label[0] in '_^':
            props['label_position']=label[0]
            label=label[1:]
        dict.__init__(self,props)
        self['label']=label



class Circle(dict):

    positions={
        't':0,
        'l':90,
        'b':180,
        'r':270,
    }

    def __init__(self,node,position='t',label='',**props):

        self.node=node
        
        if label and label[0] in '_^':
            props['label_position']=label[0]
            label=label[1:]
        dict.__init__(self,props)
        self['label']=label
        
        self['angleA']=self.positions[position]
        self['angleB']=self['angleA']+180

class Diagram(dict):

    def __init__(self):

        self.arrows=[]
        self.circles=[]
        self.two_cells=[]
        self.defaults={}
        super(Diagram,self).__init__()

    def add_node(self,name,position,label=None,**props):

        props_default=copy.copy(self.defaults)
        props_default.update(props)
        self[name]=Node(name,position,label,**props_default)
        return self[name]

    def add_arrow(self,from_name,to_name,label='',**props):

        arr=Arrow(self[from_name],self[to_name],label,**props)
        self.arrows.append(arr)
        return arr

    def add_arrows(self,*fromtos,label='',**props):

        for frm,to in zip(fromtos,fromtos[1:]):
            self.add_arrow(frm,to,label=label,**props)

    def add_circle(self,node_name,position='t',label='',**props):

        arr=Circle(self[node_name],position,label,**props)
        self.circles.append(arr)
        return arr

    def cluster_by_names(self,*names):

        return Cluster(self[name] for name in names)

    def cluster_all(self):

        return Cluster(iter(self.values()))

    def dimensions(self):

        max0=max(node.position[0] for node in self.values())
        max1=max(node.position[1] for node in self.values())
        return max0,max1

    def set_default(self,**props):

        self.defaults=props

    def unset_default(self,*names):

        for name in names:
            if name in self.defaults:
                del self.defaults[name]

    def resize_to(self,x,y):

        dim_x,dim_y=self.dimensions()
        fac_x=x/dim_x
        fac_y=y/dim_y
        for node in self.values():
            node.position=(
                    node.position[0]*fac_x,
                    node.position[1]*fac_y)

class StringDiagram(Diagram):

    def add_point_node(self,*args,**kwargs):
        kwargs['ntype']='point'
        return self.add_node(*args,**kwargs)
    
    def add_circle_node(self,*args,**kwargs):
        kwargs['label']=''
        kwargs['ntype']='circle'
        return self.add_node(*args,**kwargs)

    def add_top_node(self,*args,**kwargs):
        kwargs['is_top']=True
        tn=self.add_point_node(*args,**kwargs)
        tn.shift((0,0.5))
        return tn

    def add_bottom_node(self,*args,**kwargs):
        kwargs['is_bottom']=True
        bn=self.add_point_node(*args,**kwargs)
        bn.shift((0,-0.5))
        return bn

    def add_state(self,*args,**kwargs):
        kwargs['ntype']='state'
        return self.add_node(*args,**kwargs)
    
    def add_effect(self,*args,**kwargs):
        kwargs['ntype']='effect'
        return self.add_node(*args,**kwargs)

    def add_cup(self,node1,node2,**kwargs):
        kwargs['atype']='cup'
        self.add_arrow(node1,node2,**kwargs)
    
    def add_cap(self,node1,node2,**kwargs):
        kwargs['atype']='cap'
        self.add_arrow(node1,node2,**kwargs)
        

class MatrixDiagram(Diagram):

    def __init__(self):

        self.current_row=0
        self.current_col=0
        self.frozen_arrows={}
        self.node_matrix=[]
        self.current_line=[]
        self.node_matrix.append(self.current_line)
        self.last_node=None
        super(MatrixDiagram,self).__init__()

    def cr(self):

        self.current_row+=1
        self.current_col=0
        self.current_line=[]
        self.node_matrix.append(self.current_line)

    def skip(self,cols=1):

        self.current_col+=cols
        self.current_line.extend([None]*cols)

    def node(self,name,label=None,**props):

        node_added=self.add_node(name,(self.current_col,self.current_row),label=label,**props)
        self.current_line.append(node_added)
        self.last_node=node_added
        current_pos=(self.current_col,self.current_row)
        if current_pos in self.frozen_arrows:
            for frozen_arrow in self.frozen_arrows[current_pos]:
                frozen_arrow(name)
            del self.frozen_arrows[current_pos]
        self.current_col+=1
        return node_added

    def arr(self,direction,label='',**props):

        def make_unfreeze(from_name,label,**props):

            def unfreeze(to_name):
                self.add_arrow(from_name,to_name,label,**props)
            return unfreeze

        udlr=[direction.count(c) for c in "udlr"]
        p2delta=udlr[1]-udlr[0]
        p1delta=udlr[3]-udlr[2]
        pos=(self.last_node.position[0]+p1delta,self.last_node.position[1]+p2delta)
        node_to=self.node_by_pos(pos)
        if node_to:
            self.add_arrow(self.last_node.name,node_to.name,label,**props)
        else:
            if pos not in self.frozen_arrows:
                self.frozen_arrows[pos]=[]
            self.frozen_arrows[pos].append(make_unfreeze(self.last_node.name,label,**props))

    def rows(self,i1,i2):

        return Cluster(
                node for i in range(i1,i2)
                    for node in self.node_matrix[i]
                        if node is not None)
    def row(self,i):

        return self.rows(i,i+1)

    def columns(self,j1,j2):

        return Cluster(
                row[j]
                for row in self.node_matrix
                    for j in range(j1,j2)
                        if j<len(row) and row[j] is not None
        )

    def column(self,j):

        return self.columns(j,j+1)

    def node_by_pos(self,pos):

        if pos[1]>=len(self.node_matrix):
            return None
        if pos[0]>=len(self.node_matrix[pos[1]]):
            return None
        return self.node_matrix[pos[1]][pos[0]]



if __name__=='__main__':

    d=Diagram()
    d.add_node("A",(0,0))
    d.add_node("B",(1,0))
    d.add_arrow("A","B")
    print(d)
    d1=MatrixDiagram()
    d1.node("A",label="AA")
    print('label of node A ==',d1['A']['label'])
    d1.node("B")
    d1.cr()
    d1.skip()
    d1.node("C")
    d1.node("D")
    d1.add_arrow("A","B",label="f",label_position="^")
    d1.add_arrow("A","C")
    d1.add_arrow("C","B")
    d1.cluster_by_names("A","B").shift((0.5,0.5)).shift((0.2,0))
    print(d1)
    print((d1.row(0)))
    print((d1.row(1)))
    print((d1.column(2)))


