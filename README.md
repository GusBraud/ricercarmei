# RicercarMEI

Generate MEI headers from a CSV file, and easily merge those headers in MEI files. Developped by Valentin Crogiez ([@valcrog]([[url](https://github.com/valcrog)](https://github.com/valcrog))), Master student in Computer Science at Université de Lille.

## Getting started

Install the project into your virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Then run the installed command from the repository root:

```bash
ricercarmei --data <path_to_csv> [--mei-files <path_to_mei_files>] [--edition <edition_choice>]
```

If you prefer the script form, `python src/main.py --data <path_to_csv>` also works from the repository root.

## Editing headers

The MEI header template is defined in [src/config.py](src/config.py). This is the only file that you should edit to change the generated header structure.

First, a `MAPPING` defines which CSV column is used for each MEI field.
The template is then built using the following building blocks:

1. `RESP_STMT` contains the responsibility statement inserted into every header.
2. `PUB_STMT` contains the publication and rights statement.
3. `EDITION_SOURCES` defines the source description for each supported edition type.

Finally, `generate_mei()` assembles the final `<mei>` header using the blocks above.

You can write new building blocks by simply declaring them as constants and using `deepcopy(NEW_BLOCK)` in the `generate_mei()` function. It is important to use the element maker `E` as the namespace of this new building block.

If you add a new edition key in `EDITION_SOURCES`, it is automatically exposed by the `--edition` CLI argument.

## License
[MIT](./LICENSE.md)
