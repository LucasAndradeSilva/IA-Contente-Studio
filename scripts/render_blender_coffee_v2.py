"""Renderiza o protótipo V2 de café no Blender, sem ativos externos."""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets" / "fonts" / "roboto" / "Roboto.ttf"
FPS = 30


def args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "outputs" / "cg-cafe-v2-001" / "prototypes" / "blender.mp4"))
    parser.add_argument("--preview", action="store_true")
    return parser.parse_args(values)


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.55):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_text(text: str, x: float, z: float, size: float, mat, name: str, align="CENTER", extrude=0.018):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = text
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = extrude
    if FONT.exists():
        curve.font = bpy.data.fonts.load(str(FONT), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, -1.8, z)
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.data.materials.append(mat)
    return obj


def cube(name, location, scale, mat, bevel=0.12):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = obj.modifiers.new("Soft edges", "BEVEL")
    mod.width = bevel
    mod.segments = 3
    obj.data.materials.append(mat)
    return obj


def visibility(objects, start: int, end: int):
    for obj in objects:
        for frame, hidden in ((1, start > 1), (max(1, start - 1), True), (start, False), (end, False), (min(240, end + 1), True)):
            obj.hide_render = hidden
            obj.hide_viewport = hidden
            obj.keyframe_insert("hide_render", frame=frame)
            obj.keyframe_insert("hide_viewport", frame=frame)


def main() -> None:
    opt = args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass

    ink = material("Ink", (0.018, 0.025, 0.024, 1))
    panel = material("Panel", (0.055, 0.075, 0.070, 1))
    cream = material("Cream", (0.90, 0.84, 0.72, 1))
    lime = material("Lime", (0.68, 1.0, 0.035, 1), roughness=0.32)
    brown = material("Coffee", (0.33, 0.12, 0.055, 1))
    metal = material("Metal", (0.42, 0.50, 0.47, 1), metallic=0.75, roughness=0.24)

    # Fundo e base comuns: o sistema visual não muda entre as cenas.
    cube("Backdrop", (0, 2.4, 0), (6.0, 0.18, 10.6), ink, 0.25)
    cube("Stage", (0, 0.6, -3.8), (4.0, 2.0, 0.22), panel, 0.2)
    add_text("FATONAUTA  •  PROTÓTIPO V2", -5.0, 9.1, 0.28, cream, "Kicker", align="LEFT")
    add_text("CAFÉ", -4.5, 8.35, 0.36, lime, "Pill", align="LEFT")
    add_text("MODELO VISUAL  •  03", 5.0, 8.35, 0.23, cream, "Source", align="RIGHT")
    add_text("BLENDER / EEVEE", 4.9, -9.25, 0.22, cream, "Engine", align="RIGHT")

    scene_ranges = [(1, 90), (91, 150), (151, 240)]
    headings = [("AMARGO?", "O erro pode estar no preparo.", "Sabe por que seu café fica amargo?", "AMARGO"),
                ("NÃO É", "só o pó.", "Não é só o pó.", "PÓ"),
                ("É O JEITO", "como você prepara.", "É o que você faz com ele.", "FAZ")]
    groups: list[list[bpy.types.Object]] = [[], [], []]
    for index, ((start, end), (head, sub, caption, active)) in enumerate(zip(scene_ranges, headings)):
        texts = [add_text(head, 0, 6.65, 1.25 if index < 2 else 0.9, lime, f"Head{index}"),
                 add_text(sub, 0, 5.55, 0.42, cream, f"Sub{index}"),
                 cube(f"CaptionPanel{index}", (0, -1.2, -7.35), (5.1, 0.14, 0.72), panel, 0.3),
                 add_text(caption, 0, -7.2, 0.34, cream, f"Caption{index}"),
                 add_text(active, 0, -8.0, 0.3, lime, f"Active{index}")]
        groups[index].extend(texts)
        visibility(texts, start, end)

    # Cena 1: caneca low-poly.
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.5, depth=2.0, location=(0, 0, -0.7))
    cup = bpy.context.object; cup.name = "Cup"; cup.data.materials.append(cream); groups[0].append(cup)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.38, depth=0.10, location=(0, -0.02, 0.32))
    coffee = bpy.context.object; coffee.data.materials.append(brown); groups[0].append(coffee)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.20, major_segments=24, minor_segments=8, location=(1.52, 0, -0.55), rotation=(math.pi/2,0,0))
    handle = bpy.context.object; handle.data.materials.append(cream); groups[0].append(handle)
    visibility([cup, coffee, handle], *scene_ranges[0])

    # Cena 2: pacote com sinal de negação.
    pack = cube("CoffeePack", (0, 0, -0.4), (1.55, 0.62, 2.0), brown, 0.22)
    label = cube("PackLabel", (0, -0.7, -0.2), (1.15, 0.08, 0.56), cream, 0.06)
    pack_word = add_text("CAFÉ", 0, -0.2, 0.5, brown, "PackWord")
    pack_word.location.y = -0.82
    bpy.ops.mesh.primitive_torus_add(major_radius=2.25, minor_radius=.16, major_segments=32, minor_segments=8, location=(0,-1.0,-.25), rotation=(math.pi/2,0,0))
    ring=bpy.context.object;ring.data.materials.append(lime)
    slash=cube("NoSlash",(0,-1.1,-.25),(2.5,.16,.16),lime,.05);slash.rotation_euler.y=-.62
    groups[1].extend([pack,label,pack_word,ring,slash]);visibility([pack,label,pack_word,ring,slash],*scene_ranges[1])

    # Cena 3: chaleira, filtro e fluxo.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.65, location=(-.65,0,-.15))
    kettle=bpy.context.object;kettle.scale.z=.82;kettle.data.materials.append(metal)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=.48, radius2=.20, depth=2.6, location=(1.05,0,.35), rotation=(0,math.pi/2-.32,0))
    spout=bpy.context.object;spout.data.materials.append(metal)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.05,minor_radius=.18,major_segments=24,minor_segments=8,location=(-.65,.05,1.15),rotation=(math.pi/2,0,0))
    grip=bpy.context.object;grip.data.materials.append(panel)
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.55,radius2=1.0,depth=1.35,location=(2.35,0,-1.85))
    filt=bpy.context.object;filt.data.materials.append(cream)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.075,depth=2.25,location=(1.82,-.15,-.65))
    stream=bpy.context.object;stream.rotation_euler.y=-.24;stream.data.materials.append(lime)
    groups[2].extend([kettle,spout,grip,filt,stream]);visibility([kettle,spout,grip,filt,stream],*scene_ranges[2])

    # Movimento suave e determinístico.
    for group, (start, end) in zip(groups, scene_ranges):
        for obj in group:
            if obj.type != "FONT" and not obj.name.startswith("CaptionPanel"):
                base_z = obj.location.z
                for frame, offset in ((start, 0), ((start+end)//2, .22), (end, 0)):
                    obj.location.z = base_z + offset
                    obj.keyframe_insert("location", frame=frame)

    world = bpy.data.worlds.new("World") if not bpy.data.worlds else bpy.data.worlds[0]
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.011, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .22
    bpy.ops.object.light_add(type="AREA", location=(-4, -5, 6)); key=bpy.context.object;key.data.energy=1050;key.data.shape="DISK";key.data.size=5;key.data.color=(.75,1,.2)
    bpy.ops.object.light_add(type="AREA", location=(4, -3, 1)); fill=bpy.context.object;fill.data.energy=750;fill.data.size=4;fill.data.color=(1,.38,.12)
    bpy.ops.object.camera_add(location=(0,-25,0)); camera=bpy.context.object;camera.data.type="ORTHO";camera.data.ortho_scale=20;camera.rotation_euler=(math.pi/2,0,0);bpy.context.scene.camera=camera

    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE"
    scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG" if opt.preview else "FFMPEG"
    scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=240
    scene.render.film_transparent=False
    scene.view_settings.look="AgX - Medium High Contrast"
    output=Path(opt.output);output.parent.mkdir(parents=True,exist_ok=True)
    if opt.preview:
        scene.frame_set(190);scene.render.filepath=str(output.with_suffix(".png"));bpy.ops.render.render(write_still=True)
    else:
        scene.render.filepath=str(output)
        scene.render.ffmpeg.format="MPEG4";scene.render.ffmpeg.codec="H264";scene.render.ffmpeg.constant_rate_factor="MEDIUM";scene.render.ffmpeg.audio_codec="NONE"
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
