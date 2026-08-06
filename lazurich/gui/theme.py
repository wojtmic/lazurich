import json
from pathlib import Path
import slint

ICON_NAMES = ["dashboard", "list", "settings", "skin"]
CURRENT_VERSION = 1

def apply_theme(app, theme_dir: Path) -> tuple[dict[str, str], int]:
    code = 0
    palette = json.loads((theme_dir / "palette.json").read_text())
    if palette.get('version', 0) < CURRENT_VERSION:
        print('TRIGGER ON FUCKING THIS HERE')
        print(palette.get('version', 0))
        code = 1
        theme_dir = Path(__file__).parent / 'theme'
        palette = json.loads((theme_dir / "palette.json").read_text())
    print(palette.get('version', 0))

    options = json.loads((theme_dir / "options.json").read_text())
    if options.get('version', 0) < CURRENT_VERSION:
        print('TRIGGER ON THAT FUCKING OTHER ONE')
        print(options.get('version', 0))
        code = 1
        theme_dir = Path(__file__).parent / 'theme'
        options = json.loads((theme_dir / "options.json").read_text())
    print(options.get('version', 0))

    for key, hex_value in palette.items():
        if key == 'version': continue
        setattr(app.Theme, key, slint.Color(hex_value))

    for name in ICON_NAMES:
        icon_path = theme_dir / "assets" / f"{name}.png"
        if icon_path.exists():
            setattr(app.Theme, f"{name}_icon", slint.Image.load_from_path(str(icon_path)))

    print(code)
    return options, code
