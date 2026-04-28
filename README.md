# PENTAD LAJFI Demo

Evolutionary life simulation in Blender. PENTAD organisms (5 Gielis supershape segments) that eat, mate, fight and die.

Combines the simulation engine from [lajfi](https://github.com/jinkieyz/lajfi) with the organism morphology from [pentad](https://github.com/jinkieyz/pentad).

## Features

- 5-segment Gielis supershape organisms with fractal outgrowths
- DNA-based heredity (offspring resemble parents)
- Omnivore behavior (creatures eat plants and each other)
- Spawn/death animations
- Auto-rotating camera with event zoom (births, combat)
- Voxel remesh for manifold meshes

## Requirements

- Blender 3.6+ (tested with 5.0)

## Usage

Open Blender and run the script:

```
blender --python pentad_lajfi.py
```

Or open Blender, load the script in the text editor, and press Alt+P.

## License

MIT
