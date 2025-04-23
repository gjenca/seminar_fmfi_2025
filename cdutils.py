from numpy import array,dot,cos,sin,radians
import sys

def rotmatrix(theta_deg):

    theta = radians(theta_deg)
    return array([[cos(theta),-sin(theta)],[sin(theta),cos(theta)]])

def triangle_over(node1,node2):

    a=array(node1.position)
    b=array(node2.position)
    c=(rotmatrix(60) @ (a-b))+b
    return (float(c[0]),float(c[1]))

