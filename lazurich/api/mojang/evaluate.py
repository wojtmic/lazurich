import platform
import re
from dataclasses import dataclass

from lazurich.api.mojang.data import Action, Arch, Arg, Download, Library, LibraryRole, OsName, Profile, Rule

SYSTEMS = {"Windows": OsName.WINDOWS, "Darwin": OsName.OSX, "Linux": OsName.LINUX}
MACHINES = {
    "x86_64": Arch.X86_64, "amd64": Arch.X86_64,
    "arm64": Arch.ARM64, "aarch64": Arch.ARM64,
    "i386": Arch.X86, "i686": Arch.X86, "x86": Arch.X86,
}

@dataclass(frozen=True, slots=True)
class Environment:
    os: OsName
    arch: Arch
    os_version: str = ""
    features: frozenset[str] = frozenset()

    @classmethod
    def current(cls, features: frozenset[str] = frozenset()) -> "Environment":
        return cls(
            os=SYSTEMS.get(platform.system(), OsName.UNKNOWN),
            arch=MACHINES.get(platform.machine().lower(), Arch.UNKNOWN),
            os_version=platform.release(),
            features=features,
        )

@dataclass(frozen=True, slots=True)
class Resolved:
    classpath: tuple[Download, ...]  # client jar last
    natives: tuple[Library, ...]
    jvm_args: tuple[str, ...]
    game_args: tuple[str, ...]

def rules_allow(rules: tuple[Rule, ...], env: Environment) -> bool:
    if not rules:
        return True
    allowed = False
    for rule in rules:
        if matches(rule, env):
            allowed = rule.action is Action.ALLOW
    return allowed

def matches(rule: Rule, env: Environment) -> bool:
    if rule.os is not None:
        if rule.os.name is not None and rule.os.name is not env.os:
            return False
        if rule.os.arch is not None and rule.os.arch is not env.arch:
            return False
        if rule.os.version is not None and not re.search(rule.os.version, env.os_version):
            return False
    return all((name in env.features) is wanted for name, wanted in rule.features)

def flatten(args: tuple[Arg, ...], env: Environment) -> tuple[str, ...]:
    return tuple(token for arg in args if rules_allow(arg.rules, env) for token in arg.value)

def evaluate(profile: Profile, env: Environment) -> Resolved:
    active = [lib for lib in profile.libraries if rules_allow(lib.rules, env)]
    classpath = [lib.download for lib in active if lib.role is LibraryRole.CLASSPATH and lib.download]
    if profile.client is not None:
        classpath.append(profile.client)
    return Resolved(
        classpath=tuple(classpath),
        natives=tuple(lib for lib in active if lib.role is LibraryRole.NATIVE),
        jvm_args=flatten(profile.jvm_args, env),
        game_args=flatten(profile.game_args, env),
    )