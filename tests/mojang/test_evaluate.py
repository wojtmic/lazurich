import pytest

from lazurich.api.mojang import Arch, Environment, OsName, evaluate

LINUX = Environment(OsName.LINUX, Arch.X86_64, "6.8.0")
MACOS = Environment(OsName.OSX, Arch.ARM64, "14.5")
WIN10 = Environment(OsName.WINDOWS, Arch.X86_64, "10.0")

def classifiers(resolved):
    return {d.path.rsplit("/", 1)[1] for d in resolved.classpath if d.path and "natives" in d.path}

def native_names(resolved):
    return {lib.name for lib in resolved.natives}

def test_modern_natives_follow_os(load_version):
    profile = load_version("1.19")
    linux = classifiers(evaluate(profile, LINUX))
    assert "lwjgl-3.3.1-natives-linux.jar" in linux
    assert not any("windows" in c or "macos" in c for c in linux)
    assert "lwjgl-3.3.1-natives-windows.jar" in classifiers(evaluate(profile, WIN10))

def test_client_jar_is_last_on_classpath(load_version):
    profile = load_version("1.19")
    assert evaluate(profile, LINUX).classpath[-1] == profile.client

def test_os_gated_jvm_args(load_version):
    profile = load_version("1.19")
    assert "-XstartOnFirstThread" in evaluate(profile, MACOS).jvm_args
    assert "-XstartOnFirstThread" not in evaluate(profile, LINUX).jvm_args

def test_os_version_regex(load_version):
    profile = load_version("1.19")
    assert "-Dos.name=Windows 10" in evaluate(profile, WIN10).jvm_args
    win7 = Environment(OsName.WINDOWS, Arch.X86_64, "6.1")
    assert "-Dos.name=Windows 10" not in evaluate(profile, win7).jvm_args

def test_arch_gated_jvm_args(load_version):
    profile = load_version("1.19")
    assert "-Xss1M" not in evaluate(profile, WIN10).jvm_args
    assert "-Xss1M" in evaluate(profile, Environment(OsName.WINDOWS, Arch.X86, "10.0")).jvm_args

@pytest.mark.parametrize(("features", "present"), [(frozenset(), False), (frozenset({"has_custom_resolution"}), True)])
def test_feature_gated_game_args(load_version, features, present):
    env = Environment(OsName.LINUX, Arch.X86_64, features=features)
    assert ("--width" in evaluate(load_version("1.19"), env).game_args) is present

def test_old_natives_follow_os(load_version):
    profile = load_version("1.7.10")
    assert "org.lwjgl.lwjgl:lwjgl-platform:2.9.1:natives-linux" in native_names(evaluate(profile, LINUX))
    assert "org.lwjgl.lwjgl:lwjgl-platform:2.9.1:natives-linux" not in native_names(evaluate(profile, WIN10))

def test_old_natives_pick_bitness(load_version):
    names = native_names(evaluate(load_version("1.7.10"), WIN10))
    assert "tv.twitch:twitch-external-platform:4.5:natives-windows-64" in names
    assert "tv.twitch:twitch-external-platform:4.5:natives-windows-32" not in names

def test_upstream_disallow_survives_restriction(load_version):
    # twitch-platform upstream: allow, then disallow linux
    names = native_names(evaluate(load_version("1.7.10"), LINUX))
    assert not any(n.startswith("tv.twitch:") for n in names)

def test_old_natives_not_on_classpath(load_version):
    resolved = evaluate(load_version("1.7.10"), LINUX)
    assert not any(d.path and "natives" in d.path for d in resolved.classpath)