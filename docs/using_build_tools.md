# Using Build Tools

This is a simple guide to building an ABS Engine project.
First, create the [recommended file structure for ABS Engine projects](game_file_structure.md).
Open ABS Engine, make a new entity, then save the project inside
the game's root folder.
Click "Build Game", then "Yes".

ABS Engine will now compile the game and all of its dependencies
to the folder that contains the project file, using Pyinstaller
under the hood. A "Building Game" window stays open with a progress
bar and log while this happens, and only closes once Pyinstaller has
actually finished.

When you run the new `run.py` file in that folder,
ABS Engine will emulate its original environment.

The finished build is written to a `dist/<ProjectName>/` folder
next to your project file (spaces in the project name are replaced
with hyphens), containing the game's executable alongside an
`_internal/` folder with its bundled dependencies. Pyinstaller's
intermediate files are written to a `build/` folder and a generated
`<ProjectName>.spec` file, also next to your project file.
Building again automatically replaces a previous `dist/<ProjectName>/`
folder, even if it still exists from an earlier build.

## Building Manually

Build Game already runs Pyinstaller for you, but if you'd rather
package the game yourself, for example to produce a single
executable file instead of a folder, you can invoke Pyinstaller
directly:

```bash
pyinstaller --onefile --noconsole --name MyGame --add-data "game.absp:." --add-data "scripts:scripts" --add-data "data:data" run.py
```

>[!NOTE]
> On Windows, use a semicolon (`;`) instead of a colon between the
> source and destination of each `--add-data` flag, since Windows
> paths already use a colon after the drive letter (e.g. `C:\`).

Pyinstaller adds `engine/` without any additional flags because
it is directly imported.
Use `--icon <file>` to add an icon.

>[!IMPORTANT]
> Make sure your project file is named "game.absp".
> If you want to change the name, modify the "PROJECT_FILE"
> variable in `run.py`.
