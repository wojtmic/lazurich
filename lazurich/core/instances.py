from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.paths import INSTANCES, INSTANCE
from lazurich.core.exceptions import AlreadyExistsException
from lazurich.core.utils import gen_id

from dataclasses import asdict
import aiofiles
import tomllib
import tomli_w

async def read_manifest() -> list[Instance]:
    if not INSTANCE.exists(): return []

    async with aiofiles.open(INSTANCE, mode='rb') as f:
        content = await f.read()

    data = tomllib.loads(content.decode())
    return [Instance(**i) for i in data.get('instances', [])]

async def write_manifest(instances: list[Instance]):
    data = {'instances': [asdict(i) for i in instances]}

    async with aiofiles.open(INSTANCE, mode='wb') as f:
        await f.write(tomli_w.dumps(data).encode())

async def create_instance(instance: Instance):
    instances = await read_manifest()
    if instance in instances:
        raise AlreadyExistsException(f'Instance {instance.name} already exists!')

    instance_id = gen_id()
    (INSTANCES / instance_id).mkdir(parents=True, exist_ok=True)
    instances.append(instance)
    await write_manifest(instances)
