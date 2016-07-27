# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- export selected parts to obj with colors materials from FreeCAD
#--
#-- microelly 2015 - easyw 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import Draft
import Mesh,MeshPart, Part
from math import sin,cos,pi
import random
import sys, os
from os.path import expanduser

version="1.1.0"
FreeCAD.Console.PrintMessage("version "+version+"\n")

def removeObj(obj):
    print "remove ", obj.Name, " == ", obj.Label
    App.ActiveDocument.removeObject(obj.Name)
###

def splitToFaces(sel):
    global gg
    result=[]
    for sx in sel:
        shape=sx.Shape
        s=App.ActiveDocument.addObject('Part::Feature','copy')
        s.Shape=shape
        App.ActiveDocument.ActiveObject.Label=sx.Label
        FreeCADGui.ActiveDocument.ActiveObject.DiffuseColor=sx.ViewObject.DiffuseColor
        ll=Draft.downgrade(s,delete=False)
        faces=ll[0]
        n=0
        multi= len(s.ViewObject.DiffuseColor)<>1
        for f in faces:
            gg.addObject(f)
            print f.ViewObject
            if multi:
                f.ViewObject.DiffuseColor=s.ViewObject.DiffuseColor[n]
            else:
                f.ViewObject.DiffuseColor=s.ViewObject.DiffuseColor
            n += 1
            result.append(f)
        removeObj(s)
        FreeCAD.ActiveDocument.recompute()
    return result
###

def color_value(r,g,b):
    mmin=min(r,g,b)
    mmax=max(r,g,b)
    mdiff=mmax-mmin
    if mmax==mmin:
        h=0
    elif mmax==r:
        h=2+(g-b)/mdiff
    elif mmax==g:
        h=4+(b-r)/mdiff
    elif mmax==b:
        h=(r-g)/mdiff
    else:
        raise Exception("color_calculation")
    h =   h * pi/3
    return h
###

def create_obj(sources):
    global gg
    
    obname = sources[0].Label    
    targetname = "TTC"
    #out_path = expanduser("~")
    out_path=os.path.dirname(os.path.realpath(__file__))+os.sep
    #obname = "exp_obj_wmtl"
    
    gg=App.ActiveDocument.addObject("App::DocumentObjectGroup","Group")
    sources=splitToFaces(sources)
    
    f0=open(out_path+obname+".mtl",'wb')
    f0.write("\n\n\nnewmtl Material\n")
    f0.write("Ns 96.078431\n")
    f0.write("Ka 0.000000 0.000000 0.000000\n")
    f0.write("Kd 0.800000 0.80 0.80\n")
    f0.write("Ks 0.00000 0.0 0.0\n")
    f0.write("Ni 1.000000\n")
    f0.write("d 1.000000\n")
    f0.write("illum 2\n")
    f0.write("map_Kd colors64.png\n")
    f0.close()
    
    f1=open(out_path+obname+".obj",'wb')
    f1.write("# FreeCAD export colored OBJ File:\n")
    f1.write("mtllib "+obname+".mtl\n")
    #f1.write("mtllib "+obname+".mtl\n")
    #f1.write("mtllib colors64.mtl\n")
    f1.write("o "+obname+"\n")
    
    sloop=-1
    v_string="#v_string .\n"
    vt_string="#vt_string\n"
    f_string="#f_string\n" + "s off\n" + "usemtl Material" + "\n\n"
    
    z=0
    h=color_value(0,0,1.0)
    x=0.5+ 0.5*cos(h)*0.9
    y=0.5 + 0.5*sin(h)*0.9
    vt_string += "# " + str(z) +  "  miscolor "   + "\n"
    # new color palette
    #vt_string += "vt 0.5 0.5\n"
    vt_string += "vt 0.5 0.3\n"
    v_ix=0
    f_ix=1
    for source in  sources:
        sloop += 1
        __doc__=App.ActiveDocument
        __mesh__=__doc__.addObject("Mesh::Feature","Mesh")
        
        # net method - test maturity and quality #+#
        
        # mefisto
        #__mesh__.Mesh=MeshPart.meshFromShape(Shape=source.Shape,MaxLength=0.5)
        
        # standard
        __mesh__.Mesh=Mesh.Mesh(source.Shape.tessellate(0.1))
        
        # netgen
        #__mesh__.Mesh=MeshPart.meshFromShape(Shape=source.Shape,Fineness=2,SecondOrder=0,Optimize=1,AllowQuad=0)
        
        __mesh__.ViewObject.CreaseAngle=25.0
        target=__doc__.addObject("Part::Feature",targetname)
        __shape__=Part.Shape()
        __shape__.makeShapeFromMesh(__mesh__.Mesh.Topology,0.100000)
    
        target.Shape=__shape__
        target.purgeTouched()
        removeObj(__mesh__)
    
        del __shape__
        del __doc__, __mesh__
    
        s=target.Shape
        vc=0
        points=[]
        for vx in s.Vertexes:
            v=vx.Point
            v_string +="# sloop=" + str(sloop) + " vx=" + str(vc) + "\n"
            v_string += ''.join(["v ", str(v[0])," ",str(v[1])," ",str(v[2]),"\n"])
            points.append(v)
            vc += 1
        fc=0
    
        pref=source.Shape.Faces
        flist={}
        fnlist={}
        fcolorlist={}
        dlist={}
        ez=0
        
        dlist=s.Faces
    
        sc=source.ViewObject.DiffuseColor[0]
        target.ViewObject.DiffuseColor=sc
        
        h=color_value(sc[0],sc[1],sc[2])
        x=0.5+ 0.5*cos(h)*0.9
        y=0.5 + 0.5*sin(h)*0.9
        if 1 or False:
        #   [r,g,b]=[100,100,100]
            FreeCAD.Console.PrintMessage(sc)
            [r,g,b,tt]=sc
        #   print sc
            rr=int(r*15)
            r1=int(rr/4) 
            r2=int(rr%4)
        #   r1=0
        #   r2=0
            g=(g*15)
            b=(b*15)
            # $r1*16+$g,$r2*16+$b,$t);
            FreeCAD.Console.PrintMessage("\n")
            FreeCAD.Console.PrintMessage([rr,b,g,r1,r2])
            FreeCAD.Console.PrintMessage("\n")
            x=(0.0+ r1*16+g)/63
            y=1-(0.0+ r2*16+b)/63
            #[x,y]=[0.1,0.9]
            FreeCAD.Console.PrintMessage([x,y])
            FreeCAD.Console.PrintMessage("\n")
        
        vt_string +="# " + str(z) +  "   " + str(sc)  + "\n"
        #vt_string +="vt " +str(x) + " " + str(y) + "\n"
        vt_string +="vt " +str(x) + " " + str(y) + "\n"
        z += 1
    
        fc=0
        for e in s.Faces:
            try:
                f_string += ''.join(['f ',str(points.index(e.Vertexes[0].Point)+1 + v_ix),
                    '/',str(fc+1 + f_ix),' ',str(points.index(e.Vertexes[1].Point)+1 + v_ix),
                    '/',str(fc+1 + f_ix),' ',str(points.index(e.Vertexes[2].Point)+1 + v_ix),'/',str(fc+1 + f_ix),'\n'])
            except:
                print "Error ",fc
                pass
        v_ix += len(points)
        f_ix += 1
        vt_string += "\n# next part v_ix="  + str(v_ix) + " f_ix=" + str(f_ix) +"\n\n" 
        f_string += "\n# next part v_ix="  + str(v_ix) + " f_ix=" + str(f_ix) +"\n\n" 
        removeObj(target)
    
    f1.write(v_string)
    f1.write(vt_string)
    f1.write(f_string)
    f1.close()
    FreeCAD.Console.PrintMessage("generated "+out_path+obname+".obj\n")
    FreeCAD.Console.PrintMessage("generated "+out_path+obname+".mtl\n")
    FreeCAD.Console.PrintMessage("color png file "+out_path+"color64.png\n")
###

sources = FreeCADGui.Selection.getSelection()
if len(sources)>0:
    FreeCAD.Console.PrintMessage("running\n")
    create_obj(sources);
else:
    FreeCAD.Console.PrintError("select at least one Part\n")


