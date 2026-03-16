# Using Build Tools

This is a simple guide to building an ABS Engine project.
First, create the [recommended file structure for ABS Engine projects](game_file_structure.md).
Open ABS Engine, make a new entity, then save the project inside
the game's root folder.
Click "Build Game", then "Yes".

ABS Engine will now compile the game and all of it's dependencies
to the folder that contains the project file.
When you run the new run.py file in that folder,
ABS Engine will emulate it's original enviroment.
To package the game into a single execuatable file,
use a tool like Pyinstaller. The command should look like this:

```bash
pyinstaller --onefile --add-file "data:data MyGame/run.py
```

Or, for windows users:
```powershell
pyinstaller --onefile --add-file "data;data" MyGame/run.py
```

>[!IMPORTANT]
> Make sure your project file is named exactly "game.absp".
> If you want to change the name, modify the "PROJECT_FILE"
> variable in run.py.