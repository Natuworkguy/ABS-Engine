# Using Build Tools

This is a simple guide to building an ABS Engine project.
First, create the [recommended file structure for ABS Engine projects](game_file_structure.md).
Open ABS Engine, make a new entity, then save the project inside
the game's root folder.
Click "Build Game", then "Yes".

ABS Engine will now compile the game and all of its dependencies
to the folder that contains the project file.
When you run the new `run.py` file in that folder,
ABS Engine will emulate its original environment.
To package the game into a single executable file,
use a tool like Pyinstaller. The command should look like this:

```bash
pyinstaller --onefile --add-data 'scripts:scripts' --add-data 'game.absp:.' --add-data "data:data" run.py
```

Pyinstaller adds `engine/` without any additional flags because
it is directly imported.
Use `--icon <file>` to add an icon.

Here is the command template I find most useful:

```bash
pyinstaller --onefile --noconsole --name MyGame --add-data "game.absp:." --add-data "scripts:scripts" --add-data "data:data" run.py
```

>[!IMPORTANT]
> Make sure your project file is named exactly "game.absp".
> If you want to change the name, modify the "PROJECT_FILE"
> variable in run.py.
