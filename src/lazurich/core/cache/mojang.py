from enum import IntFlag

from peewee import IntegerField, CharField, DateTimeField, ForeignKeyField, JSONField, CompositeKey

from lazurich.core.cache.base import BaseModel

class Platform(IntFlag):
    WINDOWS_X86   = 1 << 0
    WINDOWS_X64   = 1 << 1
    WINDOWS_ARM64 = 1 << 2
    LINUX_X86     = 1 << 3
    LINUX_X64     = 1 << 4
    LINUX_ARM64   = 1 << 5
    OSX_X64       = 1 << 6
    OSX_ARM64     = 1 << 7
    ALL = (1 << 8) - 1

class PlatformField(IntegerField):
    def db_value(self, v): return int(v)
    def python_value(self, v): return Platform(v) if v is not None else None

class AssetIndex(BaseModel):
    id = CharField(primary_key=True)
    url = CharField()
    sha1 = CharField()
    size = IntegerField()
    total_size = IntegerField()

class Library(BaseModel):
    KINDS = ("library", "native", "client")

    name = CharField(unique=True)
    kind = CharField(default="library")
    path = CharField()
    url = CharField(null=True)
    sha1 = CharField(null=True)
    size = IntegerField(null=True)
    platforms = PlatformField(default=Platform.ALL)
    extract_exclude = JSONField(null=True)

class Version(BaseModel):
    id = CharField(primary_key=True)
    type = CharField(index=True)
    release_time = DateTimeField(index=True)
    time = DateTimeField()
    meta_url = CharField()
    meta_sha1 = CharField()
    compliance_level = IntegerField(default=0)

    detail_sha1 = CharField(null=True)
    main_class = CharField(null=True)
    java_component = CharField(null=True)
    java_major = IntegerField(null=True)
    asset_index = ForeignKeyField(AssetIndex, null=True)
    inherits_from = ForeignKeyField("self", null=True, backref="children")

    @property
    def fetched(self):
        return self.detail_sha1 == self.meta_sha1

    @property
    def libraries(self):
        return (Library
                .select()
                .join(VersionLibrary)
                .where(VersionLibrary.version == self)
                .order_by(VersionLibrary.position))

class VersionLibrary(BaseModel):
    version = ForeignKeyField(Version, backref="library_links", on_delete="CASCADE")
    library = ForeignKeyField(Library, backref="version_links")
    position = IntegerField()

    class Meta:
        primary_key = CompositeKey("version", "library")

class JavaRuntime(BaseModel):
    component = CharField()
    platforms = PlatformField()
    version_name = CharField()
    released = DateTimeField()
    manifest_url = CharField()
    manifest_sha1 = CharField()
    manifest_size = IntegerField()

    class Meta:
        indexes = ((("component", "platforms"), True),)
