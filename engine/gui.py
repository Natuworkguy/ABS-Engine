# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

import sys
import os
import json
import subprocess  # nosec B404
import tempfile
import shutil
import threading
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QInputDialog,
    QDialog,
    QCheckBox,
    QTextEdit,
    QFileDialog,
)
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QFont

from .saveload import resource_path
from .logger import logger, Status as LoggerStatus
from .build_tools import build

GP_BASE_PATH: str = str(Path(__file__).parent.parent)
ENGINE_DATA_PATH = resource_path("data")


def game_path(relative: Optional[str]) -> Optional[str]:
    if relative is None:
        return None
    return os.path.join(str(GP_BASE_PATH), relative)


class GameSignals(QObject):
    finished = Signal()


LAUNCHER_TEMPLATE = """#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, {engine_root})

from engine.core import Game as CoreGame, Entity

with open({data_file}) as f:
    data = json.load(f)

base_path = data["base_path"]
settings = data["settings"]
core_game = CoreGame(
    data["name"],
    width=settings["dimensions"][0],
    height=settings["dimensions"][1],
    cursor_visible=settings["cursor_visible"],
    fullscreen=settings["fullscreen"],
    IS_EDITOR=True,
)

for entity_name, entity_data in data["entities"].items():
    scriptfile = entity_data.get("scriptfile")
    image_path = entity_data.get("image")

    if scriptfile:
        scriptfile = os.path.join(base_path, scriptfile)
    if image_path:
        image = os.path.join(base_path, image_path)
    else:
        image = None

    entity = Entity(
        x=entity_data.get("x", 0),
        y=entity_data.get("y", 0),
        width=entity_data.get("width", 50),
        height=entity_data.get("height", 50),
        color=tuple(entity_data.get("color", (255, 255, 255))),
        scriptfile=scriptfile,
        image=image,
    )
    print("[ABS] Entity '" + str(entity_name) + "': script=" + repr(scriptfile) + " exists=" + str(scriptfile is not None and os.path.exists(scriptfile)) + " init=" + str(entity.scriptfile_init_exists) + " update=" + str(entity.scriptfile_update_exists))
    core_game.scenes[core_game.current_scene].add(entity)

core_game.run()
"""


class EntityDataDialog(QDialog):
    def __init__(self, entity_name: str, entity_data: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.entity_name = entity_name
        self.result_data = entity_data.copy()

        self.setWindowTitle("Entity Data | ABS Engine")
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(json.dumps(entity_data, indent=4))
        self.text_edit.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def save_data(self) -> None:
        try:
            data = json.loads(self.text_edit.toPlainText())
            if isinstance(data, list):
                QMessageBox.critical(
                    self, "Error", "Failed to save entity data. Ensure that the data is a dictionary."
                )
                return
            self.result_data = data
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save entity data: {e}\nPlease ensure the data is in valid JSON format.",
            )


class GameSettingsDialog(QDialog):
    def __init__(
        self,
        dimensions: list[int],
        cursor_visible: bool,
        fullscreen: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Game Settings | ABS Engine")
        self.setFixedSize(300, 300)

        self.result_dimensions = dimensions.copy()
        self.result_cursor_visible = cursor_visible
        self.result_fullscreen = fullscreen

        layout = QVBoxLayout(self)

        dims_group = QGroupBox("Dimensions")
        dims_layout = QVBoxLayout(dims_group)

        dims_layout.addWidget(QLabel("Width"))
        self.width_input = QLineEdit(str(dimensions[0]))
        dims_layout.addWidget(self.width_input)

        dims_layout.addWidget(QLabel("Height"))
        self.height_input = QLineEdit(str(dimensions[1]))
        dims_layout.addWidget(self.height_input)

        layout.addWidget(dims_group)

        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)

        self.cursor_checkbox = QCheckBox("Cursor Visible")
        self.cursor_checkbox.setChecked(cursor_visible)
        display_layout.addWidget(self.cursor_checkbox)

        self.fullscreen_checkbox = QCheckBox("Fullscreen")
        self.fullscreen_checkbox.setChecked(fullscreen)
        display_layout.addWidget(self.fullscreen_checkbox)

        layout.addWidget(display_group)

        save_button = QPushButton("Save and Close")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self) -> None:
        width = self.width_input.text()
        height = self.height_input.text()

        if not width.strip() or not height.strip():
            QMessageBox.critical(self, "Error", "Width and height values must be given.")
            return

        try:
            self.result_dimensions[0] = int(width)
            self.result_dimensions[1] = int(height)
            self.result_cursor_visible = self.cursor_checkbox.isChecked()
            self.result_fullscreen = self.fullscreen_checkbox.isChecked()
        except ValueError:
            QMessageBox.critical(
                self, "Error", "Width and height values must both be of type integer."
            )
            return

        QMessageBox.information(self, "Success", "Settings saved")
        self.accept()


class Engine(QMainWindow):
    def __init__(self, base_path: str) -> None:
        super().__init__()
        global GP_BASE_PATH
        GP_BASE_PATH = base_path

        self.game_signals = GameSignals()
        self.game_signals.finished.connect(self._on_game_finished)
        self._game_process: Optional[subprocess.Popen] = None
        self._game_tmpdir: Optional[str] = None
        self._game_error: Optional[str] = None

        absp_path = os.path.join(base_path, "game.absp")
        if os.path.exists(absp_path):
            with open(absp_path, "r") as f:
                data = json.load(f)
            game = data.get("game", {})
            self.project_name = data.get("name", "Untitled Project")
            self.entities = data.get("entities", {})
            self.game_dimensions = game.get("dimensions", [800, 600])
            self.cursor_visible = game.get("cursor_visible", True)
            self.fullscreen = game.get("fullscreen", False)
        else:
            os.makedirs(os.path.join(base_path, "scripts"), exist_ok=True)
            self.project_name = os.path.basename(base_path)
            self.entities = {}
            self.game_dimensions = [800, 600]
            self.cursor_visible = True
            self.fullscreen = False

        self.setWindowTitle(f"ABS Engine - {self.project_name} ({base_path})")
        self.setFixedSize(530, 700)

        if "-noicon" not in sys.argv:
            icon_path = os.path.join(ENGINE_DATA_PATH, "images", "abs_icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        self._build_project_section(layout)
        self._build_entities_section(layout)
        self._build_engine_section(layout)

        self.project_name_input.setText(self.project_name)
        for entity_name in self.entities.keys():
            self.entity_list.addItem(entity_name)
        self.build_game_button.setEnabled(True)

    def _build_project_section(self, parent_layout: QVBoxLayout) -> None:
        group = QGroupBox("Project")
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Project Name:"))

        self.project_name_input = QLineEdit()
        self.project_name_input.setText("Untitled Project")
        layout.addWidget(self.project_name_input)

        name_save_button = QPushButton("Save Name")
        name_save_button.clicked.connect(lambda: self.save_name(self.project_name_input.text()))
        layout.addWidget(name_save_button)

        parent_layout.addWidget(group)

        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)

        save_button = QPushButton("Save Project")
        save_button.clicked.connect(self.save_project)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Open Project")
        load_button.clicked.connect(self.open_project)
        button_layout.addWidget(load_button)

        parent_layout.addWidget(button_group)

    def _build_entities_section(self, parent_layout: QVBoxLayout) -> None:
        group = QGroupBox("Entities")
        layout = QVBoxLayout(group)

        layout.addWidget(QLabel("Entity List"))

        self.entity_list = QListWidget()
        self.entity_list.setMaximumHeight(150)
        layout.addWidget(self.entity_list)

        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)

        edit_button = QPushButton("Edit Data")
        edit_button.clicked.connect(lambda: self.view_entity())
        button_layout.addWidget(edit_button)

        rename_button = QPushButton("Rename Entity")
        rename_button.clicked.connect(self.rename_entity)
        button_layout.addWidget(rename_button)

        delete_button = QPushButton("Delete Entity")
        delete_button.clicked.connect(self.delete_entity)
        button_layout.addWidget(delete_button)

        layout.addWidget(button_row)

        self.add_entity_input = QLineEdit()
        self.add_entity_input.setPlaceholderText("Entity name...")
        layout.addWidget(self.add_entity_input)

        add_button = QPushButton("Add Entity")
        add_button.clicked.connect(lambda: self.add_entity(self.add_entity_input.text()))
        layout.addWidget(add_button)

        parent_layout.addWidget(group)

    def _build_engine_section(self, parent_layout: QVBoxLayout) -> None:
        group = QGroupBox("Engine")
        layout = QVBoxLayout(group)

        self.run_game_button = QPushButton("Run Game")
        self.run_game_button.clicked.connect(self.run_game)
        layout.addWidget(self.run_game_button)

        self.build_game_button = QPushButton("Build Game")
        self.build_game_button.clicked.connect(self.build_game)
        self.build_game_button.setEnabled(False)
        layout.addWidget(self.build_game_button)

        settings_button = QPushButton("Game Settings")
        settings_button.clicked.connect(self.game_settings)
        layout.addWidget(settings_button)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.quit_application)
        layout.addWidget(exit_button)

        parent_layout.addWidget(group)

    def build_game(self) -> None:
        do_build = QMessageBox.question(
            self,
            "Build Tools | ABS Engine",
            "This will build to the folder containing the .absp project file. Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if do_build != QMessageBox.StandardButton.Yes:
            return

        logger("Build Tools: Starting build")
        build(Path(GP_BASE_PATH), ENGINE_DATA_PATH=ENGINE_DATA_PATH)
        logger("Build Tools: Build completed")
        QMessageBox.information(self, "Build Tools | ABS Engine", "The build has been completed.")

    def game_settings(self) -> None:
        dialog = GameSettingsDialog(
            self.game_dimensions, self.cursor_visible, self.fullscreen, self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.game_dimensions = dialog.result_dimensions
            self.cursor_visible = dialog.result_cursor_visible
            self.fullscreen = dialog.result_fullscreen

    def delete_entity(self) -> None:
        current_item = self.entity_list.currentItem()
        if current_item is None:
            QMessageBox.critical(self, "Error", "No entity selected.")
            return

        selected_item = current_item.text()

        do_delete = QMessageBox.question(
            self,
            "Delete Entity",
            "Are you sure you want to delete the selected entity?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if do_delete != QMessageBox.StandardButton.Ok:
            return

        del self.entities[selected_item]
        self.entity_list.takeItem(self.entity_list.row(current_item))

    def rename_entity(self) -> None:
        current_item = self.entity_list.currentItem()
        if current_item is None:
            QMessageBox.critical(self, "Error", "No entity selected.")
            return

        selected_item = current_item.text()

        new_name, ok = QInputDialog.getText(
            self, "Rename Entity", "Enter new entity name:", text=selected_item
        )

        if not ok or new_name is None:
            return

        if not new_name.strip():
            QMessageBox.critical(self, "Error", "Entity name cannot be empty.")
            return

        self.entities[new_name] = self.entities.pop(selected_item)
        current_item.setText(new_name)

    def add_entity(self, name: str) -> None:
        if not name.strip():
            QMessageBox.critical(self, "Error", "Entity name cannot be empty.")
            return
        elif name in self.entities:
            QMessageBox.critical(self, "Error", "Entity already exists.")
            return

        self.add_entity_input.clear()
        self.entities[name] = {}
        self.entity_list.addItem(name)

    def view_entity(self) -> None:
        current_item = self.entity_list.currentItem()
        if current_item is None:
            QMessageBox.critical(self, "Error", "No entity selected.")
            return

        selected_item = current_item.text()

        dialog = EntityDataDialog(selected_item, self.entities[selected_item], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.entities[selected_item] = dialog.result_data

    def open_project(self) -> None:
        project_dir = QFileDialog.getExistingDirectory(
            self, "Open Project Folder", "", QFileDialog.Option.ShowDirsOnly
        )
        if not project_dir:
            return

        global GP_BASE_PATH
        GP_BASE_PATH = project_dir

        absp_path = os.path.join(project_dir, "game.absp")
        if os.path.exists(absp_path):
            with open(absp_path, "r") as f:
                data = json.load(f)
            game = data.get("game", {})
            self.project_name = data.get("name", os.path.basename(project_dir))
            self.entities = data.get("entities", {})
            self.game_dimensions = game.get("dimensions", [800, 600])
            self.cursor_visible = game.get("cursor_visible", True)
            self.fullscreen = game.get("fullscreen", False)
        else:
            os.makedirs(os.path.join(project_dir, "scripts"), exist_ok=True)
            self.project_name = os.path.basename(project_dir)
            self.entities = {}
            self.game_dimensions = [800, 600]
            self.cursor_visible = True
            self.fullscreen = False

        self.setWindowTitle(f"ABS Engine - {self.project_name} ({project_dir})")
        self.project_name_input.setText(self.project_name)
        self.entity_list.clear()
        for entity_name in self.entities.keys():
            self.entity_list.addItem(entity_name)

    def save_project(self) -> None:
        absp_path = os.path.join(GP_BASE_PATH, "game.absp")
        project_data = {
            "name": self.project_name,
            "game": {
                "dimensions": self.game_dimensions,
                "cursor_visible": self.cursor_visible,
                "fullscreen": self.fullscreen,
            },
            "entities": self.entities,
        }
        try:
            with open(absp_path, "w") as f:
                json.dump(project_data, f, indent=2)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to save project:\n{e}")
            return

        QMessageBox.information(self, "Saved", f"Project saved to {absp_path}")

    def save_name(self, name: str) -> None:
        self.project_name = name
        QMessageBox.information(self, "Info", f"Project name set to: {self.project_name}")

    def run_game(self) -> None:
        logger("Launching game in subprocess")
        logger(f"Entity count: {len(self.entities)}")
        for name, data in self.entities.items():
            logger(f"  Entity '{name}': scriptfile={data.get('scriptfile', '<NOT SET>')!r}")
        self._game_tmpdir = tempfile.mkdtemp(prefix="abs_game_")
        engine_root = str(Path(__file__).parent.parent)

        project_data = {
            "name": self.project_name,
            "settings": {
                "dimensions": self.game_dimensions,
                "cursor_visible": self.cursor_visible,
                "fullscreen": self.fullscreen,
            },
            "entities": self.entities,
            "base_path": GP_BASE_PATH,
        }

        data_file = os.path.join(self._game_tmpdir, "game_data.json")
        with open(data_file, "w") as f:
            json.dump(project_data, f)
        launcher = os.path.join(self._game_tmpdir, "_run_game.py")
        with open(launcher, "w") as f:
            f.write(
                LAUNCHER_TEMPLATE.format(
                    engine_root=repr(engine_root),
                    data_file=repr(data_file),
                )
            )

        try:
            self._game_process = subprocess.Popen(  # nosec B603
                [sys.executable, launcher],
                cwd=self._game_tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            logger(f"Failed to launch game subprocess: {e}", status=LoggerStatus.CRITICAL)
            QMessageBox.critical(self, "Launch Error", f"Failed to launch game:\n{e}")
            self._game_tmpdir = None
            return

        def _wait() -> None:
            if self._game_process is None:
                return
            stdout, stderr = self._game_process.communicate()
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            for line in stdout_str.splitlines():
                if "[ABS]" in line:
                    logger(f"[GAME] {line.strip()}")
            if self._game_process.returncode != 0:
                error_msg = stderr_str if stderr_str else "Unknown error"
                logger(f"Game subprocess failed: {error_msg}", status=LoggerStatus.CRITICAL)
                self._game_error = error_msg
            else:
                self._game_error = None
            self.game_signals.finished.emit()

        threading.Thread(target=_wait, daemon=True).start()

    def _on_game_finished(self) -> None:
        had_error = self._game_error is not None
        if had_error:
            QMessageBox.critical(
                self,
                "Game Error",
                f"The game exited with an error:\n\n{self._game_error}",
            )
        if self._game_tmpdir and os.path.exists(self._game_tmpdir):
            shutil.rmtree(self._game_tmpdir, ignore_errors=True)
        self._game_process = None
        self._game_tmpdir = None
        self._game_error = None

    def run(self) -> None:
        self.show()

    def quit_application(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()


def run() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet(
        """
        QMainWindow {
            background-color: #FFFFFF;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #333333;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #E0E0E0;
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            padding: 4px 12px;
            color: #333333;
        }
        QPushButton:hover {
            background-color: #D0D0D0;
        }
        QPushButton:pressed {
            background-color: #C0C0C0;
        }
        QPushButton:disabled {
            background-color: #F0F0F0;
            color: #999999;
        }
        QLineEdit {
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            padding: 3px;
            color: #333333;
            background-color: #FFFFFF;
        }
        QListWidget {
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            color: #333333;
            background-color: #FFFFFF;
        }
        QListWidget::item:selected {
            background-color: #0078D7;
            color: #FFFFFF;
        }
        QCheckBox {
            color: #333333;
        }
        QTextEdit {
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            color: #333333;
            background-color: #FFFFFF;
        }
        """
    )

    project_dir = QFileDialog.getExistingDirectory(
        None, "Open Project Folder", "", QFileDialog.Option.ShowDirsOnly
    )
    if not project_dir:
        sys.exit(0)

    engine = Engine(project_dir)
    engine.run()
    sys.exit(app.exec())
