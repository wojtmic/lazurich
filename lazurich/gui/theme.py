import json
from pathlib import Path
import slint

ICON_NAMES = ["dashboard", "list", "settings", "skin"]

def apply_theme(app, theme_dir: Path) -> None:
    palette = json.loads((theme_dir / "palette.json").read_text())
    for key, hex_value in palette.items():
        setattr(app.Theme, key, slint.Color(hex_value))

    for name in ICON_NAMES:
        icon_path = theme_dir / "assets" / f"{name}.png"
        if icon_path.exists():
            setattr(app.Theme, f"{name}_icon", slint.Image.load_from_path(str(icon_path)))
