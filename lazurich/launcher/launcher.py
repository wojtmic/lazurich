import subprocess
from lazurich.api.piston import get_for_version
from lazurich.launcher.instancemanager import get_instance
from lazurich.api.microsoft import login, get_credentials
import os
import platform
import zipfile

PLATFORM = platform.system().replace('Darwin', 'osx').lower()

JAR_STORAGE   = os.path.expanduser('~/.local/share/lazurich/jars')
ASSET_STORAGE = os.path.expanduser('~/.local/share/lazurich/assets')
LIB_STORAGE   = os.path.expanduser('~/.local/share/lazurich/libs')
NATIVE_STORAGE= os.path.expanduser('~/.local/share/lazurich/natives')

def extract_natives(version: str):
    manifest = get_for_version(version)
    libs = manifest['libraries']

    # Clear/create natives directory
    os.makedirs(NATIVE_STORAGE, exist_ok=True)

    for lib in libs:
        # Check rules (same logic as your classpath)
        if 'rules' in lib:
            if lib['rules'][0]['action'] == 'allow' and not lib['rules'][0]['os']['name'] == PLATFORM:
                continue

        # Check if this is a native library by looking for 'natives' in the URL
        if 'downloads' not in lib or 'artifact' not in lib['downloads']:
            continue

        artifact_url = lib['downloads']['artifact']['url']

        # Skip if it doesn't contain 'natives'
        if 'natives' not in artifact_url:
            continue

        # Get the native JAR filename and path
        native_jar_name = artifact_url.split('/')[-1]
        native_jar_path = os.path.join(LIB_STORAGE, native_jar_name)

        # Extract native files from the JAR
        if os.path.exists(native_jar_path):
            with zipfile.ZipFile(native_jar_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    # Extract only .so, .dll, or .dylib files
                    if file.endswith(('.so', '.dll', '.dylib')):
                        filename = os.path.basename(file)

                        # Extract file
                        source = zip_ref.open(file)
                        target_path = os.path.join(NATIVE_STORAGE, filename)

                        with open(target_path, 'wb') as target:
                            target.write(source.read())

def build_classpath_string(version: str):
    manifest = get_for_version(version)
    libs = manifest['libraries']

    usedLibs = []

    for lib in libs:
        if 'rules' in lib:
            if lib['rules'][0]['action'] == 'allow' and not lib['rules'][0]['os']['name'] == platform: continue
        usedLibs.append(lib)

    cp_string = ''
    for lib in usedLibs:
        lib_path = os.path.join(LIB_STORAGE, lib['downloads']['artifact']['url'].split('/')[-1])
        cp_string += f'{lib_path}:'

    cp_string += os.path.join(JAR_STORAGE, f'{version}-client.jar')
    return cp_string

def launch_game(version: str, gamedir: str, uuid: str, username: str, token: str):
    manifest = get_for_version(version)
    cpstring = build_classpath_string(version)
    assetVersion = manifest['assetIndex']['id']

    subprocess.run(
        [
            'java', '-Xmx8G', '-Xms512M',
            f'-Djava.library.path={NATIVE_STORAGE}',
            f'-Dlog4j.configurationFile={os.path.join(gamedir, 'log4j2.xml')}',
            '-cp', cpstring,
            manifest['mainClass'],
            '--username', username,
            '--version', version,
            '--gameDir', os.path.join(gamedir, '.minecraft'),
            '--assetsDir', ASSET_STORAGE,
            '--assetIndex', assetVersion,
            '--uuid', uuid,
            '--accessToken', token,
            '--userType', 'mojang',
            '--versionType', 'release'
        ]
    )

def launch_instance(name: str):
    instance = get_instance(name)
    version = instance['ver']
    gamepath = instance['path']

    ms_login = login()
    credentials = get_credentials(ms_login[0])

    launch_game(version, gamepath, credentials['uuid'], credentials['name'], credentials['token'])

if __name__ == '__main__':
    launch_instance('EpicInstance')
