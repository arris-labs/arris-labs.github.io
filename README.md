# arris-labs.github.io

The site at <https://arris-labs.github.io>: the showcase bracket from
[Arris](https://github.com/arris-labs/arris) in 3D, every face coloured by
the operation that made it.

The page is static. `assets/bracket.py` is the script that builds the part;
`tools/export.py` runs it and writes the mesh, the labels and the STEP the
page loads:

```sh
pip install arris==0.9.1
python tools/export.py
```

The export is deterministic: rerunning it with the same arris version
leaves `assets/` unchanged. The page loads three.js from jsDelivr and has
no build step.

Licence: MIT OR Apache-2.0, as Arris.
