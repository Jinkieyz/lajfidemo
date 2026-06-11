# GEMESIS

Evolutionary life simulation in Blender. Organisms built from Gielis supershape segments that eat, mate, fight and die. Each generation produces new sculptural forms through mutation and natural selection.

Gems + genesis. Generative sculpture through code-driven evolution.

## What it does

Spawns a population of 5-segment creatures in 3D space. Each creature carries DNA that encodes its morphology (Gielis superformula parameters) and behavior. Creatures with more energy survive longer, reproduce, and pass mutated genes to offspring. The simulation exports STL meshes at regular intervals: every organism that ever lived is preserved as a printable/castable 3D file.

## Features

- 5-segment Gielis supershape organisms with fractal outgrowths
- DNA-based heredity (offspring resemble parents with mutation)
- Omnivore behavior (creatures eat plants and each other)
- Spawn/death animations with Blender particle systems
- Auto-rotating camera with event zoom (births, combat)
- Voxel remesh for manifold meshes (3D-print/cast ready)
- STL export every 120 seconds

## Requirements

- Blender 3.6+ (tested with 4.2 and 5.0)

## Usage

```bash
blender --python pentad_lajfi.py
```

Or open Blender, load the script in the text editor, and press Alt+P.

Output STL files go to `/tmp/pentad_output/` by default. Set `LAJFI_OUTPUT` environment variable to change.

## Context

Part of my artistic practice where code-generated forms are materialized through glass casting, 3D printing, and hot blowmold techniques. The simulation produces organisms that become physical sculptures.

Related repositories:
- [lajfi](https://github.com/Jinkieyz/lajfi) - The simulation engine (population dynamics, energy, mating)
- [pentad](https://github.com/Jinkieyz/pentad) - The organism generator (Gielis morphology)
- [holi](https://github.com/Jinkieyz/holi) - Headless organism generator with Boolean tunnels for glass blowing
- [min_bild_ai](https://github.com/Jinkieyz/min_bild_ai_latent_space_walker) - Progressive GAN trained on sculptural images

## License

MIT
