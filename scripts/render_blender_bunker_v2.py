"""Maquete Blender original; 900 quadros nativos, com câmera e peças animadas."""
import argparse
import math
import sys
import time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/cg-bunker-v2-001/blender'
OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--preview',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
concrete=mat('Concreto',(0.57,.67,.7));steel=mat('Metal azulado',(.19,.32,.41));soil=mat('Solo',(.25,.16,.11));grass=mat('Superficie',(.28,.36,.25));blue=mat('Ciano',(.16,.77,.87));orange=mat('Laranja',(.88,.48,.22));cream=mat('Creme',(.88,.83,.69));dark=mat('Fundo',(.035,.07,.12))
def pos(x,y,z):return (x,-z,y)
def box(name,x,y,z,w,h,d,m,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos(x,y,z));o=bpy.context.object;o.name=name;o.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    mod=o.modifiers.new('Cantos suaves','BEVEL');mod.width=.045;mod.segments=2
    if parent:o.parent=parent
    return o
def cylinder(name,x,y,z,r,h,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=h,location=pos(x,y,z));o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def tube(name,points,r,m):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,xyz in zip(s.points,points):p.co=(*pos(*xyz),1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def empty(name):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);return o
box('Solo',0,-1.95,0,9.4,.8,6.4,soil)
box('Piso',0,-1.45,0,8.6,.34,5.5,concrete)
box('Parede traseira',0,.05,-2.55,8.6,3.3,.32,concrete)
box('Parede esquerda',-4.15,.05,0,.32,3.3,5.4,concrete)
box('Parede cortada',4.15,-.7,-.2,.32,1.8,5,concrete)
for i in range(17):box('Marca de corte',-4+i*.5,-1.3,2.78,.05,.1,.1,orange)
roof=empty('Teto revelado')
box('Laje',0,1.82,0,8.8,.3,5.7,concrete,roof);box('Solo superior',0,2.05,0,9.4,.18,6.2,grass,roof);box('Entrada superior',0,2.4,-.5,1.1,.65,1.1,steel,roof)
door=empty('Porta animada');door.location=pos(-3.95,-.05,1.05)
box('Folha da porta',.65,0,0,1.3,2.4,.24,steel,door);box('Macaneta',.97,0,.18,.12,.45,.08,orange,door)
air_points=[(1.5,2.9,-2.8),(1.5,1.1,-2.1),(1.5,.25,-1.85),(.3,.15,-1.85),(-1.1,.15,-1.85),(-1.1,.7,-.8)]
tube('Duto de ventilacao',air_points,.13,steel)
box('Filtro',.3,.15,-1.85,1.05,1.15,.6,blue)
for i in range(4):box('Grelha',-.07+i*.24,.15,-1.51,.055,.87,.05,dark)
fan=empty('Ventilador');fan.location=pos(-1.15,.7,-.75)
for i in range(3):
    blade=box('Pa',0,0,0,.12,.75,.05,blue,fan);blade.rotation_euler.y=i*math.pi/3
for x in [-2.8,-.8]:
    for z in [-.8,.9]:
        for dx in [-.65,.65]:cylinder('Coluna beliche',x+dx,.05,z,.045,2.6,steel)
    for y in [-.8,.55]:
        box('Cama',x,y,.05,1.45,.18,2,steel);box('Colchao',x,y+.15,.05,1.35,.22,1.9,orange);box('Travesseiro',x,y+.31,-.55,1.1,.13,.43,cream)
box('Divisoria sanitaria',2.8,-.3,-1.4,1.9,2.25,.1,steel);box('Lateral sanitaria',3.72,-.3,-.75,.1,2.25,1.3,steel)
cylinder('Sanitario seco',2.7,-.85,-.65,.38,.8,cream)
bpy.ops.mesh.primitive_torus_add(major_radius=.34,minor_radius=.08,major_segments=24,minor_segments=8,location=pos(2.7,-.43,-.65));bpy.context.object.data.materials.append(cream)
route_points=[(2.6,-1.18,1.25),(4.6,-1.18,1.25),(5.1,-.8,1.25),(5.1,1.5,1.25)]
tube('Rota esquematica',route_points,.085,blue)
box('Poco de saida',5.1,-.1,1.7,1,3,.1,steel)
for i in range(9):box('Degrau',5.1,-1.2+i*.3,1.25,.8,.065,.08,orange)
box('Tampa da saida',5.1,1.55,1.25,1.2,.15,1.2,steel)
debris=[]
for i in range(7):
    o=box('Escombro',-3.2+math.sin(i*7)*.6,-1+(i%3)*.3,1.8+math.cos(i*2)*.35,.6,.5,.5,concrete);o.rotation_euler=(i*.3,i*.8,i*.4);debris.append(o)
def dot(name,r):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r);o=bpy.context.object;o.name=name;o.data.materials.append(blue);return o
dots=[dot('Fluxo de ar',.105) for _ in range(12)];route_dot=dot('Indicador de saida',.2)
def point(points,u):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];distance=u*sum(lengths)
    for a,b,length in zip(points,points[1:],lengths):
        if distance<=length:return tuple(a[j]+(b[j]-a[j])*distance/length for j in range(3))
        distance-=length
    return points[-1]
bpy.ops.object.camera_add(location=(11,-14,10));cam=bpy.context.object;cam.name='Camera';cam.data.type='ORTHO';cam.data.ortho_scale=13.5
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=720;scene.render.resolution_y=630;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.compression=15;scene.render.film_transparent=True
scene.render.fps=30;scene.frame_start=1;scene.frame_end=900
scene.display.render_aa='16';s=scene.display.shading;s.light='STUDIO';s.color_type='MATERIAL';s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.curvature_ridge_factor=1.3;s.curvature_valley_factor=1.1;s.show_specular_highlight=True
scene.view_settings.view_transform='Standard'
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def update(frame,keys=False):
    t=(frame-1)/30;idx=int(t//5);p=(t%5)/5
    roof.location.z=smooth((p-.06)/.5)*4 if idx==0 else 8
    roof.scale=(1-.25*smooth(p/.6),)*3 if idx==0 else (.001,)*3
    door.rotation_euler.z=.9*(1-smooth(p*2)) if idx==1 else .15
    fan.rotation_euler.y=t*(5 if idx==2 else 1)
    cam.location=(10.5+math.sin(t*.15)*.65,-14,9.5)
    cam.rotation_euler=(Vector((.3,0,-.1))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=13.5/([.94,1.03,1.07,1.06,.92,.97][idx]+.025*math.sin(p*math.pi))
    for i,o in enumerate(dots):o.location=pos(*point(air_points,(t*.23+i/12)%1));o.scale=(1 if idx in [2,5] else .001,)*3
    route_dot.location=pos(*point(route_points,(t*.35)%1));route_dot.scale=(1 if idx in [4,5] else .001,)*3
    for o in debris:o.scale=(.2+.8*smooth(p*3) if idx==4 else .001,)*3
    if keys:
        for o in [roof,door,fan,cam,*dots,route_dot,*debris]:
            for prop in ['location','rotation_euler','scale']:o.keyframe_insert(prop,frame=frame)
        cam.data.keyframe_insert('ortho_scale',frame=frame)
if args.preview:
    for frame in [361,362,363]:
        update(frame);scene.render.filepath=str(OUT/f'preview-{frame}.png');bpy.ops.render.render(write_still=True)
else:
    for frame in range(1,901):update(frame,True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'bunker-v2.blend'))
    frames=OUT/'frames';frames.mkdir(exist_ok=True)
    for frame in range(1,901):
        scene.frame_set(frame);update(frame);scene.render.filepath=str(frames/f'{frame:05d}.png');bpy.ops.render.render(write_still=True)
        if frame%30==0:print(f'PROGRESS {frame}/900',flush=True)
