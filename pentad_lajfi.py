"""
GEMESIS - Evolutionary Life Simulation
github.com/jinkieyz/gemesis

Gielis supershape organisms that live, eat, mate and die.
Each generation produces new sculptural forms through mutation.
Exports STL meshes for glass casting and 3D printing.

Usage: Open in Blender, run script (Alt+P)
Or: blender --python pentad_lajfi.py
"""

import bpy
import math
import random
import sys
import os
import time
from datetime import datetime
from mathutils import Vector

WORLD_SIZE = 20
MAX_CREATURES = 3
MAX_PLANTS = 8
TICK_SPEED = 0.3
START_ENERGY = 40
MOVEMENT_COST = 0.6
IDLE_COST = 0.2
PLANT_ENERGY = 25
EAT_RANGE = 2.0
STARVATION_THRESHOLD = 0
MATING_RANGE = 3.0
MATING_ENERGY = 60
MATING_COST = 30
MUTATION_RATE = 0.20
MUTATION_STRENGTH = 0.25
ATTACK_COST = 8
KILL_ENERGY_GAIN = 0.7
CANNIBAL_RANGE = 3.0
SATISFIED_ENERGY = 70
MIN_FRACTAL_LEVELS = 2
MAX_FRACTAL_LEVELS = 3
MIN_CHILDREN = 2
MAX_CHILDREN = 5
OUTPUT_DIR = os.environ.get('LAJFI_OUTPUT', '/tmp/pentad_output')
EXPORT_INTERVAL = 120

PENTAD_GENES = ['lajfi_1', 'lajfi_2', 'lajfi_3', 'lajfi_4', 'lajfi_5']


def log(msg):
    sys.stdout.write(f"[PENTAD] {msg}\n")
    sys.stdout.flush()


def gielis_r(angle, m, n1, n2, n3):
    if abs(n1) < 0.001:
        n1 = 0.001
    t = m * angle / 4.0
    term1 = abs(math.cos(t)) ** n2
    term2 = abs(math.sin(t)) ** n3
    denom = term1 + term2
    if denom < 0.0001:
        return 1.0
    return max(0.1, min(5.0, denom ** (-1.0 / n1)))


def create_gielis_mesh(params, resolution=24, scale=1.0, location=(0, 0, 0)):
    verts = []
    faces = []
    m1, m2 = params['m1'], params['m2']
    n1, n2, n3 = params['n1'], params['n2'], params['n3']
    n1b, n2b, n3b = params['n1b'], params['n2b'], params['n3b']
    theta_steps = resolution
    phi_steps = resolution // 2
    for j in range(phi_steps + 1):
        phi = (j / phi_steps) * math.pi
        for i in range(theta_steps):
            theta = (i / theta_steps) * 2 * math.pi
            r1 = gielis_r(theta, m1, n1, n2, n3)
            r2 = gielis_r(phi, m2, n1b, n2b, n3b)
            r = r1 * r2 * scale
            x = r * math.sin(phi) * math.cos(theta) + location[0]
            y = r * math.sin(phi) * math.sin(theta) + location[1]
            z = r * math.cos(phi) + location[2]
            verts.append((x, y, z))
    for j in range(phi_steps):
        for i in range(theta_steps):
            next_i = (i + 1) % theta_steps
            v1 = j * theta_steps + i
            v2 = j * theta_steps + next_i
            v3 = (j + 1) * theta_steps + next_i
            v4 = (j + 1) * theta_steps + i
            faces.append((v1, v2, v3, v4))
    mesh = bpy.data.meshes.new("Gielis")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Gielis", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def random_gielis_gene():
    return {
        'm1': random.randint(3, 14),
        'm2': random.randint(2, 12),
        'n1': random.uniform(0.08, 0.9),
        'n2': random.uniform(0.5, 3.5),
        'n3': random.uniform(0.5, 3.5),
        'n1b': random.uniform(0.1, 0.95),
        'n2b': random.uniform(0.4, 3.2),
        'n3b': random.uniform(0.4, 3.2),
    }


def random_dna():
    dna = {}
    for gene in PENTAD_GENES:
        dna[gene] = random_gielis_gene()
    dna['fractal_levels'] = random.randint(MIN_FRACTAL_LEVELS, MAX_FRACTAL_LEVELS)
    dna['fractal_children'] = random.randint(MIN_CHILDREN, MAX_CHILDREN)
    dna['scale_factor'] = random.uniform(0.45, 0.70)
    dna['speed'] = random.uniform(0.2, 0.5)
    dna['build_seed'] = random.randint(0, 999999)
    return dna


def combine_dna(dna1, dna2):
    child_dna = {}
    for key in dna1.keys():
        if key == 'build_seed':
            child_dna[key] = (dna1[key] + dna2[key]) // 2 + random.randint(-1000, 1000)
        elif isinstance(dna1[key], dict):
            child_dna[key] = (dna1[key] if random.random() < 0.5 else dna2[key]).copy()
        elif isinstance(dna1[key], int):
            child_dna[key] = random.choice([dna1[key], dna2[key]])
        else:
            mix = random.uniform(0.3, 0.7)
            child_dna[key] = dna1[key] * mix + dna2[key] * (1 - mix)
    return child_dna


def mutate_dna(dna):
    mutated = {}
    for key, value in dna.items():
        if isinstance(value, dict):
            new_gene = value.copy()
            for gkey, gval in value.items():
                if random.random() < MUTATION_RATE:
                    if gkey in ['m1', 'm2']:
                        new_gene[gkey] = max(3, min(12, gval + random.randint(-2, 2)))
                    else:
                        change = gval * MUTATION_STRENGTH * random.uniform(-1, 1)
                        new_gene[gkey] = max(0.1, min(3.0, gval + change))
            mutated[key] = new_gene
        elif key == 'fractal_levels':
            if random.random() < MUTATION_RATE:
                mutated[key] = max(MIN_FRACTAL_LEVELS, min(MAX_FRACTAL_LEVELS,
                    value + random.choice([-1, 0, 1])))
            else:
                mutated[key] = value
        elif key == 'fractal_children':
            if random.random() < MUTATION_RATE:
                mutated[key] = max(MIN_CHILDREN, min(MAX_CHILDREN,
                    value + random.choice([-1, 0, 1])))
            else:
                mutated[key] = value
        elif isinstance(value, float):
            if random.random() < MUTATION_RATE:
                change = value * MUTATION_STRENGTH * random.uniform(-1, 1)
                mutated[key] = max(0.1, value + change)
            else:
                mutated[key] = value
        else:
            mutated[key] = value
    return mutated


class Plant:
    __slots__ = ['position', 'energy', 'obj', 'age']

    def __init__(self, position=None):
        self.position = position or [
            random.uniform(-WORLD_SIZE/2 + 2, WORLD_SIZE/2 - 2),
            random.uniform(-WORLD_SIZE/2 + 2, WORLD_SIZE/2 - 2),
            0.3
        ]
        self.energy = PLANT_ENERGY
        self.obj = None
        self.age = 0

    def build_mesh(self):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=0.3, location=self.position
        )
        self.obj = bpy.context.active_object
        self.obj.name = "Plant"

    def update(self):
        self.age += 1
        if self.age % 30 == 0 and self.energy < PLANT_ENERGY * 1.5:
            self.energy += 3

    def destroy(self):
        if self.obj:
            bpy.data.objects.remove(self.obj, do_unlink=True)
            self.obj = None


class PentadCreature:
    counter = 0

    def __init__(self, dna=None, position=None, parents=None):
        PentadCreature.counter += 1
        self.id = PentadCreature.counter
        self.name = self._generate_name()
        self.dna = dna or random_dna()
        self.position = position or [
            random.uniform(-WORLD_SIZE/2 + 3, WORLD_SIZE/2 - 3),
            random.uniform(-WORLD_SIZE/2 + 3, WORLD_SIZE/2 - 3),
            1.0
        ]
        self.energy = START_ENERGY
        self.age = 0
        self.obj = None
        self.generation = 1
        self.parents = parents or []
        self.children_count = 0
        self.meals_eaten = 0
        self.mating_cooldown = 0

    def _generate_name(self):
        vowels = "aeiou"
        consonants = "bdfgklmnprstvz"
        return ''.join(
            random.choice(consonants if i % 2 == 0 else vowels)
            for i in range(random.randint(3, 5))
        ).upper()

    def build_mesh(self, resolution=20):
        build_rng = random.Random(self.dna.get('build_seed', 0))
        all_objects = []
        segment_positions = []
        segment_scales = []

        for i, key in enumerate(PENTAD_GENES):
            params = self.dna[key]
            scale = build_rng.uniform(0.5, 0.85)

            if i == 0:
                loc = (0, 0, 0)
            else:
                attach_to = build_rng.randint(0, i - 1)
                parent_pos = segment_positions[attach_to]
                parent_scale = segment_scales[attach_to]
                angle_h = build_rng.uniform(0, 2 * math.pi)
                angle_v = build_rng.uniform(-0.7, 0.7)
                dist = parent_scale * 0.6
                loc = (
                    parent_pos[0] + dist * math.cos(angle_h) * math.cos(angle_v),
                    parent_pos[1] + dist * math.sin(angle_h) * math.cos(angle_v),
                    parent_pos[2] + dist * math.sin(angle_v)
                )

            segment_positions.append(loc)
            segment_scales.append(scale)
            obj = create_gielis_mesh(params, resolution=resolution, scale=scale, location=loc)
            all_objects.append(obj)

        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = all_objects[0]
        bpy.ops.object.join()
        base = bpy.context.active_object

        current_level = [base]
        current_scale = 1.0
        all_objects = [base]

        for level in range(1, self.dna['fractal_levels'] + 1):
            current_scale *= self.dna['scale_factor']
            level_res = max(10, resolution // (level + 1))
            new_level = []

            for parent in current_level:
                mesh = parent.data
                num_verts = len(mesh.vertices)
                step = max(1, num_verts // self.dna['fractal_children'])
                indices = list(range(0, num_verts, step))[:self.dna['fractal_children']]

                for idx in indices:
                    vert = mesh.vertices[idx]
                    pos = parent.matrix_world @ vert.co
                    normal = vert.co.normalized()
                    gene_key = build_rng.choice(PENTAD_GENES)
                    params = self.dna[gene_key]
                    direction = Vector([
                        normal.x + build_rng.uniform(-0.3, 0.3),
                        normal.y + build_rng.uniform(-0.3, 0.3),
                        normal.z + build_rng.uniform(-0.2, 0.2)
                    ]).normalized()
                    overlap = current_scale * 0.3
                    child_pos = (
                        pos.x + direction.x * overlap,
                        pos.y + direction.y * overlap,
                        pos.z + direction.z * overlap
                    )
                    child_scale = current_scale * build_rng.uniform(0.85, 1.15)
                    child = create_gielis_mesh(
                        params, resolution=level_res,
                        scale=child_scale, location=child_pos
                    )
                    all_objects.append(child)
                    new_level.append(child)

            current_level = new_level

        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = all_objects[0]
        bpy.ops.object.join()
        joined = bpy.context.active_object

        remesh = joined.modifiers.new(name="Remesh", type='REMESH')
        remesh.mode = 'VOXEL'
        remesh.voxel_size = 0.05
        remesh.use_smooth_shade = True
        bpy.ops.object.modifier_apply(modifier="Remesh")

        self.obj = joined
        self.obj.name = f"PENTAD_{self.name}"

        dims = self.obj.dimensions
        max_dim = max(dims.x, dims.y, dims.z)
        if max_dim > 3.0:
            s = 3.0 / max_dim
            self.obj.scale = (s, s, s)
            bpy.ops.object.transform_apply(scale=True)

        self.obj.location = Vector(self.position)
        self.animate_spawn()
        return self.obj

    def animate_spawn(self):
        if not self.obj:
            return
        obj = self.obj
        obj.scale = (0.01, 0.01, 0.01)
        step = [0]

        def animate_step():
            if obj.name not in bpy.data.objects:
                return None
            step[0] += 1
            if step[0] <= 6:
                size = 0.01 + (step[0] / 6.0) * 1.19
                obj.scale = (size, size, size)
                return 0.04
            elif step[0] <= 10:
                size = 1.2 - ((step[0] - 6) / 4.0) * 0.2
                obj.scale = (size, size, size)
                return 0.04
            else:
                obj.scale = (1.0, 1.0, 1.0)
                return None

        bpy.app.timers.register(animate_step, first_interval=0.02)

    def animate_death(self):
        if not self.obj:
            return
        ghost_mesh = self.obj.data.copy()
        ghost = bpy.data.objects.new(f"GHOST_{self.name}", ghost_mesh)
        bpy.context.collection.objects.link(ghost)
        ghost.location = self.obj.location.copy()
        start_z = ghost.location.z
        ghost.rotation_euler = self.obj.rotation_euler.copy()
        step = [0]

        def animate_step():
            if ghost.name not in bpy.data.objects:
                return None
            step[0] += 1
            if step[0] <= 6:
                progress = step[0] / 6.0
                ghost.scale = (1.0 + progress * 0.8, 1.0 + progress * 0.8, 1.0 - progress * 0.98)
                ghost.location.z = start_z - progress * 0.3
                return 0.05
            elif step[0] <= 10:
                progress = (step[0] - 6) / 4.0
                size = 1.8 * (1.0 - progress)
                ghost.scale = (size, size, 0.02 * (1.0 - progress))
                return 0.05
            else:
                if ghost.name in bpy.data.objects:
                    bpy.data.objects.remove(ghost, do_unlink=True)
                return None

        bpy.app.timers.register(animate_step, first_interval=0.03)

    def update(self):
        self.age += 1
        self.energy -= IDLE_COST
        if self.mating_cooldown > 0:
            self.mating_cooldown -= 1

    def move_towards(self, target_pos):
        if not self.obj:
            return
        direction = Vector(target_pos) - Vector(self.position)
        direction.z *= 0.2
        if direction.length > 0.1:
            direction.normalize()
            self.obj.location += direction * self.dna['speed']
            self.position = list(self.obj.location)
            self.energy -= MOVEMENT_COST
        self._clamp_to_world()

    def move_random(self):
        if not self.obj:
            return
        direction = Vector([random.uniform(-1, 1) for _ in range(3)])
        direction.z *= 0.1
        if direction.length > 0:
            direction.normalize()
            self.obj.location += direction * self.dna['speed'] * 0.5
            self.position = list(self.obj.location)
            self.energy -= MOVEMENT_COST * 0.5
        self._clamp_to_world()

    def _clamp_to_world(self):
        if not self.obj:
            return
        boundary = WORLD_SIZE / 2 - 2
        changed = False
        for i in range(2):
            if self.position[i] > boundary:
                self.position[i] = boundary
                changed = True
            elif self.position[i] < -boundary:
                self.position[i] = -boundary
                changed = True
        if self.position[2] < 0.5:
            self.position[2] = 0.5
            changed = True
        elif self.position[2] > 3:
            self.position[2] = 3
            changed = True
        if changed:
            self.obj.location = Vector(self.position)

    def eat(self, plant):
        self.energy += plant.energy
        self.meals_eaten += 1

    def get_strength(self):
        return self.energy * 0.5 + self.dna['fractal_levels'] * 5 + self.dna['fractal_children'] * 2

    def attack(self, prey):
        self.energy -= ATTACK_COST
        return self.get_strength() * random.uniform(0.8, 1.2) > prey.get_strength() * random.uniform(0.6, 1.4)

    def devour(self, victim):
        energy_gained = victim.energy * KILL_ENERGY_GAIN
        self.energy += energy_gained
        self.meals_eaten += 1
        return energy_gained

    def can_mate(self):
        return self.energy >= MATING_ENERGY and self.mating_cooldown == 0 and self.age > 20

    def mate_with(self, partner):
        self.energy -= MATING_COST
        partner.energy -= MATING_COST
        self.mating_cooldown = 50
        partner.mating_cooldown = 50
        child_dna = mutate_dna(combine_dna(self.dna, partner.dna))
        child_pos = [
            (self.position[0] + partner.position[0]) / 2 + random.uniform(-1, 1),
            (self.position[1] + partner.position[1]) / 2 + random.uniform(-1, 1),
            1.0
        ]
        child = PentadCreature(dna=child_dna, position=child_pos, parents=[self.name, partner.name])
        child.generation = max(self.generation, partner.generation) + 1
        self.children_count += 1
        partner.children_count += 1
        return child

    def is_dead(self):
        return self.energy <= STARVATION_THRESHOLD

    def destroy(self):
        if self.obj:
            bpy.data.objects.remove(self.obj, do_unlink=True)


creatures = []
plants = []
last_export_time = 0
generation_record = 1

cam_angle = [0.0]
cam_target = [None]
cam_zoom_timer = [0]
CAM_ORBIT_SPEED = 0.02
CAM_ORBIT_RADIUS = 30
CAM_HEIGHT = 20
CAM_ZOOM_RADIUS = 12
CAM_ZOOM_HEIGHT = 8
CAM_ZOOM_DURATION = 30


def update_camera():
    cam = bpy.context.scene.camera
    if not cam:
        return

    cam_angle[0] += CAM_ORBIT_SPEED

    if cam_zoom_timer[0] > 0:
        cam_zoom_timer[0] -= 1
        target = cam_target[0]
        if target and hasattr(target, 'position'):
            tx, ty, tz = target.position
        elif target:
            tx, ty, tz = target
        else:
            tx, ty, tz = 0, 0, 0
        r = CAM_ZOOM_RADIUS
        h = CAM_ZOOM_HEIGHT
    else:
        tx, ty, tz = 0, 0, 0
        r = CAM_ORBIT_RADIUS
        h = CAM_HEIGHT

    cx = tx + r * math.cos(cam_angle[0])
    cy = ty + r * math.sin(cam_angle[0])
    cz = h

    cam.location = Vector((cx, cy, cz))
    direction = Vector((tx - cx, ty - cy, tz - cz))
    rot = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot.to_euler()


def zoom_to(target, duration=CAM_ZOOM_DURATION):
    cam_target[0] = target
    cam_zoom_timer[0] = duration


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        if mat.users == 0:
            bpy.data.materials.remove(mat)


def setup_world():
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.02, 0.02, 0.06, 1)
    bpy.ops.object.camera_add(location=(0, -30, 20))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(55), 0, 0)
    cam.data.show_passepartout = False
    cam.data.show_limits = False
    bpy.context.scene.camera = cam
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 25))
    bpy.context.active_object.data.energy = 1.5
    bpy.ops.mesh.primitive_plane_add(size=WORLD_SIZE, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    mat = bpy.data.materials.new("FloorMat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.08, 1)
    floor.data.materials.append(mat)


def spawn_creature(dna=None, position=None):
    c = PentadCreature(dna=dna, position=position)
    c.build_mesh()
    creatures.append(c)
    log(f"SPAWN: {c.name} gen{c.generation} - {c.dna['fractal_levels']}L {c.dna['fractal_children']}C")
    return c


def spawn_plant():
    p = Plant()
    p.build_mesh()
    plants.append(p)
    return p


def distance_sq(pos1, pos2):
    return sum((a - b) ** 2 for a, b in zip(pos1, pos2))


def find_nearest(creature, targets):
    if not targets:
        return None, float('inf')
    nearest = None
    min_dist_sq = float('inf')
    for t in targets:
        d = distance_sq(creature.position, t.position)
        if d < min_dist_sq:
            min_dist_sq = d
            nearest = t
    return nearest, math.sqrt(min_dist_sq)


def tick():
    global last_export_time, generation_record
    current_time = time.time()

    for plant in plants:
        plant.update()
    while len(plants) < MAX_PLANTS:
        spawn_plant()

    dead = []
    eaten_plants = []
    new_children = []
    killed = []

    for c in creatures:
        if c in killed:
            continue
        c.update()
        nearest_plant, plant_dist = find_nearest(c, plants)
        other_creatures = [x for x in creatures if x is not c and x not in killed]
        nearest_other, other_dist = find_nearest(c, other_creatures)

        if c.energy >= SATISFIED_ENERGY:
            can_breed = c.can_mate() and len(creatures) + len(new_children) - len(killed) <= MAX_CREATURES
            if can_breed:
                potential_mates = [x for x in other_creatures if x.can_mate() and x.energy >= SATISFIED_ENERGY]
                if potential_mates:
                    mate, dist = find_nearest(c, potential_mates)
                    if mate and dist < MATING_RANGE:
                        child = c.mate_with(mate)
                        new_children.append(child)
                        if child.generation > generation_record:
                            generation_record = child.generation
                        log(f"BABY! {c.name} + {mate.name} = {child.name} (gen {child.generation})")
                        zoom_to(c, 40)
                    elif mate:
                        c.move_towards(mate.position)
                else:
                    c.move_random()
            else:
                c.move_random()
        else:
            target_plant = nearest_plant and (not nearest_other or plant_dist < other_dist)
            target_creature = nearest_other and (not nearest_plant or other_dist <= plant_dist)
            if target_plant and plant_dist < EAT_RANGE:
                c.eat(nearest_plant)
                eaten_plants.append(nearest_plant)
                log(f"NOM: {c.name} ate plant! E={c.energy:.0f}")
            elif target_creature and other_dist < CANNIBAL_RANGE:
                won = c.attack(nearest_other)
                if won:
                    energy = c.devour(nearest_other)
                    killed.append(nearest_other)
                    log(f"CANNIBAL! {c.name} ate {nearest_other.name}! +{energy:.0f}")
                    zoom_to(c, 30)
                else:
                    log(f"FIGHT: {c.name} vs {nearest_other.name} - lost!")
            elif target_plant and nearest_plant:
                c.move_towards(nearest_plant.position)
            elif target_creature and nearest_other:
                c.move_towards(nearest_other.position)
            else:
                c.move_random()

        if c.is_dead():
            dead.append(c)

    for victim in killed:
        if victim not in dead:
            dead.append(victim)
    for plant in eaten_plants:
        plant.destroy()
        if plant in plants:
            plants.remove(plant)
    for child in new_children:
        child.build_mesh()
        creatures.append(child)
    for c in dead:
        legacy = f"{c.children_count} kids" if c.children_count > 0 else "no kids"
        log(f"RIP: {c.name} age={c.age} gen={c.generation} ({legacy})")
        c.animate_death()
        c.destroy()
        creatures.remove(c)
    while len(creatures) < MAX_CREATURES:
        spawn_creature()

    update_camera()

    if cam_zoom_timer[0] == 0 and random.random() < 0.03 and creatures:
        zoom_to(random.choice(creatures), 20)

    if random.random() < 0.05:
        avg_gen = sum(c.generation for c in creatures) / len(creatures) if creatures else 0
        names = ", ".join(c.name for c in creatures)
        log(f"[{len(creatures)} alive] {names} | avg gen {avg_gen:.1f} | record {generation_record}")

    return TICK_SPEED


def main():
    log("=" * 50)
    log("PENTAD LAJFI - 5-segment organisms")
    log("=" * 50)
    log("")

    clear_scene()
    setup_world()

    for _ in range(MAX_PLANTS):
        spawn_plant()
    log(f"Spawned {MAX_PLANTS} plants")

    log("")
    for _ in range(MAX_CREATURES):
        spawn_creature()

    bpy.app.timers.register(tick)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    space.lock_camera = True
                    space.show_gizmo = False
                    space.overlay.show_overlays = False
            break

    log("")
    log("SIMULATION STARTED!")


main()
