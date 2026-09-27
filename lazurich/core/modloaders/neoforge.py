import json
import os
import re
import subprocess
import zipfile
from functools import lru_cache
from pathlib import Path
from shutil import rmtree

import httpx
from loguru import logger

from lazurich.api import neoforge as neoforge_api
from lazurich.core.models.general import DownloadItem, ChecksumEnum
from lazurich.core.network import download_batch
from lazurich.core.paths import WORKING, RENAMED
from lazurich.core.renamer import rename_file
from lazurich.core.store import check_file_stored, store_file, get_file_path, get_file_by_known_name

NEOFORGE_MAVEN = 'https://maven.neoforged.net/releases'


def client_name(neoforge_ver: str) -> str:
    return f'client-neoforge-{neoforge_ver}.jar'


def extra_name(neoforge_ver: str) -> str:
    return f'client-extra-neoforge-{neoforge_ver}.jar'


def version_json_name(neoforge_ver: str) -> str:
    return f'neoforge-{neoforge_ver}-version.json'


def maven_path(coord: str) -> str:
    """coord like 'group.id:artifact:version' or 'group.id:artifact:version:classifier[@ext]'"""
    ext = 'jar'
    if '@' in coord:
        coord, ext = coord.split('@', 1)

    parts = coord.split(':')
    group, artifact, version = parts[0], parts[1], parts[2]
    classifier = parts[3] if len(parts) > 3 else None

    filename = f'{artifact}-{version}' + (f'-{classifier}' if classifier else '') + f'.{ext}'
    return f"{group.replace('.', '/')}/{artifact}/{version}/{filename}"


def _maven_sha1_download(base_url: str, path: str) -> DownloadItem:
    resp = httpx.get(f'{base_url}/{path}.sha1')
    text = resp.text.strip()
    if resp.status_code != 200 or not re.fullmatch(r'[0-9a-fA-F]{40}', text):
        raise RuntimeError(f'Not a valid sha1 for {base_url}/{path}: got {text[:200]!r}')
    return DownloadItem(checksum=text, checksum_type=ChecksumEnum.SHA1, link=f'{base_url}/{path}')


@lru_cache(maxsize=None)
def get_tool_download(coord: str) -> DownloadItem:
    path = maven_path(coord)
    return _maven_sha1_download(NEOFORGE_MAVEN, path)


def make_library_downloads(version_json: dict) -> list[DownloadItem]:
    return [
        DownloadItem(lib['downloads']['artifact']['sha1'], ChecksumEnum.SHA1, lib['downloads']['artifact']['url'])
        for lib in version_json['libraries']
    ]


async def download_libraries(version_json: dict, neoforge_ver: str):
    items = make_library_downloads(version_json)
    p = WORKING / 'neoforge_libs'
    if p.exists(): rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

    downloads = [(i, p / i.checksum) for i in items if not check_file_stored(i)]

    if not downloads:
        logger.info(f'All NeoForge libraries for {neoforge_ver} already downloaded!')
    else:
        logger.info(f'Downloading {len(downloads)} librarie(s) for NeoForge {neoforge_ver}')
        await download_batch(downloads)

    name_map = {i.checksum: i.link.split('/')[-1] for i in items}
    for i in p.iterdir():
        await store_file(i, ChecksumEnum.SHA1, name_map[str(i.name)])

    if p.exists(): rmtree(p)


async def download_tools(coords: list[str]):
    items = [get_tool_download(c) for c in coords]
    p = WORKING / 'neoforge_tools'
    if p.exists(): rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

    downloads = [(i, p / i.checksum) for i in items if not check_file_stored(i)]

    if downloads:
        logger.info(f'Downloading {len(downloads)} processor tool jar(s)')
        await download_batch(downloads)

    name_map = {i.checksum: i.link.split('/')[-1] for i in items}
    for i in p.iterdir():
        await store_file(i, ChecksumEnum.SHA1, name_map[str(i.name)])

    if p.exists(): rmtree(p)


def _coord_key(coord: str) -> str:
    """'group:artifact:version[:classifier][@ext]' -> 'group:artifact', for index lookups."""
    base = coord.split('@', 1)[0]
    parts = base.split(':')
    return f'{parts[0]}:{parts[1]}'


def build_coordinate_index(version_json: dict) -> dict[str, Path]:
    """Maps 'group:artifact' -> stored jar path, for every library in version.json."""
    index = {}
    for lib in version_json['libraries']:
        item = DownloadItem(lib['downloads']['artifact']['sha1'], ChecksumEnum.SHA1, lib['downloads']['artifact']['url'])
        index[_coord_key(lib['name'])] = get_file_path(item)
    return index


def coordinate_to_local_path(coord: str, work: Path) -> Path:
    """Where a coordinate's jar WOULD live under work/libraries, per Maven layout.
    Used for coordinates that are processor OUTPUTS (e.g. PATCHED) rather than downloadable inputs."""
    return work / 'libraries' / maven_path(coord)


def resolve_coordinate(coord: str, lib_index: dict[str, Path], work: Path = None,
                        output_coords: set[str] = frozenset()) -> Path:
    """Resolve a 'group:artifact:version[:classifier][@ext]' coordinate to a jar path.
    Checks downloaded version.json libraries first, then (if it's a known processor
    output, e.g. MAPPINGS/MC_SLIM/MC_SRG/PATCHED) the local libraries/ layout - those
    coordinates are produced by an earlier processor in this same run, not downloadable -
    then finally falls back to fetching it as a real tool jar off Maven."""
    key = _coord_key(coord)
    if key in lib_index:
        return lib_index[key]
    if coord in output_coords and work is not None:
        return coordinate_to_local_path(coord, work)
    return get_file_path(get_tool_download(coord))


def read_main_class(jar_path: Path) -> str:
    with zipfile.ZipFile(jar_path) as zf:
        manifest = zf.read('META-INF/MANIFEST.MF').decode()
    for line in manifest.splitlines():
        if line.startswith('Main-Class:'):
            return line.split(':', 1)[1].strip()
    raise ValueError(f'No Main-Class found in {jar_path}')


_BRACKET_RE = re.compile(r'^\[(.+)]$')
_TOKEN_RE = re.compile(r'\{([A-Z_]+)}')


def resolve_token_value(value: str, data: dict, side: str, extra_tokens: dict, lib_index: dict[str, Path],
                         work: Path = None, output_coords: set[str] = frozenset()) -> str:
    """Resolve a single {TOKEN} or literal value to its final string, per install_profile.json semantics."""
    if value in extra_tokens:
        return str(extra_tokens[value])

    if value in data:
        entry = data[value]
        raw = entry[side] if isinstance(entry, dict) else entry
        return resolve_token_value(raw, data, side, extra_tokens, lib_index, work, output_coords)

    m = _BRACKET_RE.match(value)
    if m:
        return str(resolve_coordinate(m.group(1), lib_index, work, output_coords))

    return value


def substitute_args(args: list[str], data: dict, side: str, extra_tokens: dict, lib_index: dict[str, Path],
                     work: Path, output_coords: set[str]) -> list[str]:
    def sub_one(arg: str) -> str:
        def repl(m):
            return resolve_token_value(m.group(1), data, side, extra_tokens, lib_index, work, output_coords) \
                if (m.group(1) in extra_tokens or m.group(1) in data) else m.group(0)

        result = _TOKEN_RE.sub(repl, arg)

        if _BRACKET_RE.match(result):
            result = resolve_token_value(result, data, side, extra_tokens, lib_index, work, output_coords)

        return result

    return [sub_one(a) for a in args]


def run_processors(install_profile: dict, lib_index: dict[str, Path], data: dict, extra_tokens: dict,
                    work: Path, output_coords: set[str], side: str = 'client'):
    for i, proc in enumerate(install_profile['processors']):
        sides = proc.get('sides', ['client', 'server'])
        if side not in sides:
            continue

        jar_path = resolve_coordinate(proc['jar'], lib_index, work, output_coords)
        classpath_parts = [str(resolve_coordinate(c, lib_index, work, output_coords)) for c in proc['classpath']]
        classpath = os.pathsep.join(classpath_parts)

        main_class = read_main_class(jar_path)
        args = substitute_args(proc['args'], data, side, extra_tokens, lib_index, work, output_coords)

        # ensure parent dirs exist for any output-token path this processor will write to
        for coord in output_coords:
            out_path = coordinate_to_local_path(coord, work)
            out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ['java', '-cp', classpath, main_class] + args
        logger.debug(f'Running processor {i}: {cmd}')

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f'Processor {i} ({proc["jar"]}) failed:\n{result.stdout}\n{result.stderr}')
            raise RuntimeError(f'NeoForge processor {i} ({proc["jar"]}) failed with code {result.returncode}')


async def install_neoforge(mc_ver: str, neoforge_ver: str, side: str = 'client') -> Path:
    """
    Downloads and processes a NeoForge installer, producing the patched client jar.
    Returns the path to the patched jar (also stored under a known name for later retrieval).
    """
    known_name = client_name(neoforge_ver)
    already = get_file_by_known_name(known_name, ChecksumEnum.SHA1) if _known_name_exists(known_name) else None
    if already and already.exists():
        logger.info(f'NeoForge {neoforge_ver} already installed')
        return already

    work = WORKING / 'neoforge_install'
    if work.exists(): rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    installer_path = work / 'installer.jar'
    await neoforge_api.download_installer(neoforge_ver, installer_path)

    with zipfile.ZipFile(installer_path) as zf:
        install_profile = json.loads(zf.read('install_profile.json'))
        version_json = json.loads(zf.read('version.json'))

        for member in zf.infolist():
            if member.filename.startswith('data/') and not member.is_dir():
                target = work / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(member.filename))

    minecraft_jar = get_file_by_known_name(f'client-{mc_ver}.jar', ChecksumEnum.SHA1)

    await download_libraries(version_json, neoforge_ver)
    lib_index = build_coordinate_index(version_json)

    data = install_profile['data']

    # data tokens whose value is a bracketed coordinate come in two flavours: inputs
    # (resolvable now, off version.json's libraries or Maven) and outputs (produced
    # by an earlier processor in this same run, e.g. MAPPINGS/MC_SLIM/MC_SRG/PATCHED).
    # Detect outputs structurally: any token that appears as the value of a
    # write-target flag in some processor's args is being produced, not read -
    # this avoids hardcoding NeoForge's specific intermediate token names.
    OUTPUT_FLAGS = {'--output', '--to', '--slim', '--extra'}

    def _referenced_tokens(arg: str) -> list[str]:
        return _TOKEN_RE.findall(arg)

    output_token_names = set()
    for proc in install_profile['processors']:
        args = proc['args']
        for j, a in enumerate(args):
            if a in OUTPUT_FLAGS and j + 1 < len(args):
                output_token_names.update(_referenced_tokens(args[j + 1]))

    output_coords = set()
    for token in output_token_names:
        if token not in data:
            continue
        raw = data[token][side] if isinstance(data[token], dict) else data[token]
        m = _BRACKET_RE.match(raw)
        if m:
            output_coords.add(m.group(1))

    # Coordinates that must be downloaded before processors run: the processors' own
    # jar/classpath entries, plus any bracketed coordinate referenced directly in a
    # processor's args that isn't a write target (e.g. the neoform mappings zip fed
    # to MCP_DATA as --input).
    proc_coords = {proc['jar'] for proc in install_profile['processors']} | \
                  {cp for proc in install_profile['processors'] for cp in proc['classpath']}

    for proc in install_profile['processors']:
        for a in proc['args']:
            m = _BRACKET_RE.match(a)
            if m and m.group(1) not in output_coords:
                proc_coords.add(m.group(1))

    tool_coords = {c for c in proc_coords if _coord_key(c) not in lib_index and c not in output_coords}

    if tool_coords:
        await download_tools(list(tool_coords))

    extra_tokens = {
        'ROOT': str(work),
        'INSTALLER': str(installer_path),
        'MINECRAFT_JAR': str(minecraft_jar),
        'SIDE': side,
    }
    for token, val in data.items():
        raw = val[side] if isinstance(val, dict) else val
        if raw.startswith('/data/'):
            extra_tokens[token] = str(work / raw.lstrip('/'))

    run_processors(install_profile, lib_index, data, extra_tokens, work, output_coords, side=side)

    def _resolve(token: str) -> Path:
        entry = data[token]
        coord = entry[side] if isinstance(entry, dict) else entry
        return Path(resolve_token_value(coord, data, side, extra_tokens, lib_index, work, output_coords))

    patched = _resolve('PATCHED')
    if not patched.exists():
        raise RuntimeError(f'Expected patched jar at {patched} but it does not exist')

    # PATCHED holds only classes (jarsplitter put resources/assets in MC_EXTRA),
    # so both are needed on the launch classpath.
    extra_jar = _resolve('MC_EXTRA')
    if not extra_jar.exists():
        raise RuntimeError(f'Expected client-extra jar at {extra_jar} but it does not exist')

    await store_file(patched, ChecksumEnum.SHA1, known_name)
    await store_file(extra_jar, ChecksumEnum.SHA1, extra_name(neoforge_ver))

    # version.json is only inside the installer jar, which we're about to delete -
    # launch needs its libraries/arguments/mainClass, so persist it in the store.
    vj_path = work / 'neoforge-version.json'
    vj_path.write_text(json.dumps(version_json))
    await store_file(vj_path, ChecksumEnum.SHA1, version_json_name(neoforge_ver))

    rmtree(work)

    return get_file_by_known_name(known_name, ChecksumEnum.SHA1)


def _known_name_exists(name: str) -> bool:
    try:
        get_file_by_known_name(name, ChecksumEnum.SHA1)
        return True
    except Exception:
        return False


# --- launch side ---

MAVEN_FARM = RENAMED / 'maven'


def get_version_json(neoforge_ver: str) -> dict:
    """The NeoForge version.json persisted at install time."""
    path = get_file_by_known_name(version_json_name(neoforge_ver), ChecksumEnum.SHA1)
    return json.loads(path.read_text())


def build_library_farm(version_json: dict, neoforge_ver: str) -> Path:
    """Hardlink every library into a Maven-layout tree. Two reasons this is required
    rather than just using store paths: NeoForge's JVM args reference jars by
    ${library_directory}/<maven path>, and Java derives automatic module names from
    jar FILENAMES - a content-addressed store path (a bare hash, no .jar) yields no
    usable module name, so module resolution fails.
    Also farms the patched client and client-extra jars under their real names."""
    for lib in version_json['libraries']:
        item = DownloadItem(lib['downloads']['artifact']['sha1'], ChecksumEnum.SHA1,
                            lib['downloads']['artifact']['url'])
        rel = lib['downloads']['artifact'].get('path') or maven_path(lib['name'])
        if not (MAVEN_FARM / rel).exists():
            rename_file(get_file_path(item), f'maven/{rel}')

    for known, rel in _client_farm_paths(version_json, neoforge_ver).items():
        if not (MAVEN_FARM / rel).exists():
            rename_file(get_file_by_known_name(known, ChecksumEnum.SHA1), f'maven/{rel}')

    return MAVEN_FARM


def _client_farm_paths(version_json: dict, neoforge_ver: str) -> dict[str, str]:
    """known store name -> farm-relative path, for the two install-produced jars.
    The filenames matter: -DignoreList matches classpath entries by name, and it
    expects 'client-extra' and '<version_name>.jar'."""
    return {
        client_name(neoforge_ver): f'{version_json["id"]}.jar',
        extra_name(neoforge_ver): 'client-extra.jar',
    }


def get_module_path_entries(version_json: dict) -> set[str]:
    """Relative maven paths of the jars NeoForge puts on the JVM module path (-p).
    These must NOT also appear on the classpath - BootstrapLauncher rejects a module
    that's on both."""
    args = version_json.get('arguments', {}).get('jvm', [])
    entries = set()
    for i, arg in enumerate(args):
        if arg != '-p' or i + 1 >= len(args):
            continue
        for part in args[i + 1].split('${classpath_separator}'):
            part = part.replace('${library_directory}/', '').strip()
            if part:
                entries.add(part)
    return entries


def get_neoforge_str(version_json: dict, neoforge_ver: str) -> str:
    """Classpath entries NeoForge adds: its libraries (minus the ones that belong on
    the module path), plus the patched client and client-extra jars. All paths point
    into the Maven farm, not the store, so jar filenames survive - Java needs them to
    derive automatic module names."""
    module_paths = get_module_path_entries(version_json)

    parts = []
    for lib in version_json['libraries']:
        rel = lib['downloads']['artifact'].get('path') or maven_path(lib['name'])
        if rel in module_paths:
            continue
        parts.append(str(MAVEN_FARM / rel))

    for rel in _client_farm_paths(version_json, neoforge_ver).values():
        parts.append(str(MAVEN_FARM / rel))

    return os.pathsep.join(parts)


def get_neoforge_jvm_args(version_json: dict, library_dir: Path) -> list[str]:
    """NeoForge's arguments.jvm, with its placeholders resolved. These carry the JPMS
    module path and --add-opens/--add-exports flags that vanilla never needs."""
    subs = {
        '${library_directory}': str(library_dir),
        '${classpath_separator}': os.pathsep,
        '${version_name}': version_json['id'],
    }

    args = []
    for arg in version_json.get('arguments', {}).get('jvm', []):
        if not isinstance(arg, str):
            continue  # conditional/ruled args - NeoForge doesn't use these today
        for placeholder, value in subs.items():
            arg = arg.replace(placeholder, value)
        args.append(arg)
    return args


def get_neoforge_game_args(version_json: dict) -> list[str]:
    """NeoForge's extra game arguments (--fml.* and --launchTarget), appended to vanilla's."""
    return [a for a in version_json.get('arguments', {}).get('game', []) if isinstance(a, str)]


if __name__ == "__main__":
    import asyncio
    from lazurich.api.neoforge import get_latest_version_for_mc

    async def main():
        ver = get_latest_version_for_mc('1.21.1')
        path = await install_neoforge('1.21.1', ver)
        print(path)

    asyncio.run(main())