import pytest
from conftest import VERSION_FILES, load_raw

from lazurich.api.mojang import LibraryRole, OsName, normalize, normalize_manifest

@pytest.mark.parametrize("path", VERSION_FILES, ids=lambda p: p.stem)
def test_every_fixture_normalizes(path):
    profile = normalize(load_raw(path.name))
    assert profile.id == path.stem
    assert profile.main_class
    assert profile.client is not None
    assert profile.asset_index is not None
    assert any(lib.role is LibraryRole.CLASSPATH for lib in profile.libraries)
    assert profile.game_args and profile.jvm_args

def test_manifest():
    manifest = normalize_manifest(load_raw("version_manifest_v2.json"))
    ids = {v.id for v in manifest.versions}
    assert manifest.latest_release in ids
    assert manifest.latest_snapshot in ids

def test_legacy_args_split(load_version):
    profile = load_version("1.12.2")
    raw = load_raw("1.12.2.json")["minecraftArguments"]
    assert [t for a in profile.game_args for t in a.value] == raw.split()
    assert all(not a.rules for a in profile.game_args)

def test_legacy_jvm_args_synthesized(load_version):
    tokens = [t for a in load_version("1.7.10").jvm_args for t in a.value]
    assert "-Djava.library.path=${natives_directory}" in tokens
    assert tokens[-2:] == ["-cp", "${classpath}"]

def test_modern_arg_string_and_list_values(load_version):
    jvm = load_version("1.13").jvm_args
    heapdump = next(a for a in jvm if a.value[0].startswith("-XX:HeapDumpPath"))
    assert len(heapdump.value) == 1  # upstream value was a plain string
    resolution = next(a for a in load_version("1.13").game_args if "--width" in a.value)
    assert resolution.value == ("--width", "${resolution_width}", "--height", "${resolution_height}")
    assert resolution.rules[0].features == (("has_custom_resolution", True),)

def test_old_natives_expand_per_os(load_version):
    natives = [
        lib for lib in load_version("1.7.10").libraries
        if lib.name.startswith("org.lwjgl.lwjgl:lwjgl-platform:2.9.1:")
    ]
    assert {lib.name.rsplit(":", 1)[1] for lib in natives} == {
        "natives-linux", "natives-osx", "natives-windows",
    }
    assert all(lib.role is LibraryRole.NATIVE for lib in natives)
    assert all(lib.extract_exclude == ("META-INF/",) for lib in natives)
    # natives-only entry: no classpath jar
    assert not any(
        lib.name == "org.lwjgl.lwjgl:lwjgl-platform:2.9.1" for lib in load_version("1.7.10").libraries
    )

def test_arch_placeholder_expands(load_version):
    names = {lib.name for lib in load_version("1.7.10").libraries}
    assert "tv.twitch:twitch-external-platform:4.5:natives-windows-32" in names
    assert "tv.twitch:twitch-external-platform:4.5:natives-windows-64" in names

def test_undeclared_classifier_skipped(load_version):
    # twitch-platform maps linux -> natives-linux, but that jar was never published
    names = {lib.name for lib in load_version("1.7.10").libraries}
    assert "tv.twitch:twitch-platform:5.16:natives-linux" not in names

def test_artifact_and_natives_both_kept(load_version):
    libs = [lib for lib in load_version("1.12.2").libraries if lib.name.startswith("com.mojang:text2speech")]
    roles = {lib.role for lib in libs}
    assert roles == {LibraryRole.CLASSPATH, LibraryRole.NATIVE}

def test_modern_natives_are_classpath(load_version):
    libs = load_version("1.19").libraries
    assert not any(lib.role is LibraryRole.NATIVE for lib in libs)
    linux = next(lib for lib in libs if lib.name == "org.lwjgl:lwjgl:3.3.1:natives-linux")
    assert linux.rules[0].os.name is OsName.LINUX

@pytest.mark.parametrize(("version", "major"), [("1.7.10", 8), ("1.16.5", 8), ("1.18.2", 17)])
def test_java_major(load_version, version, major):
    assert load_version(version).java_major == major

def test_java_defaults_to_8():
    raw = load_raw("1.7.10.json")
    del raw["javaVersion"]
    assert normalize(raw).java_major == 8

def test_logging(load_version):
    logging = load_version("1.7.10").logging
    assert logging is not None
    assert logging.argument == "-Dlog4j.configurationFile=${path}"
    assert logging.file.path == "client-1.7.xml"