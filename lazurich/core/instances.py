from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.paths import INSTANCES, INSTANCE
from lazurich.core.exceptions import AlreadyExistsException
from lazurich.core.utils import gen_id

from dataclasses import asdict
import aiofiles
import tomllib
import tomli_w

async def read_manifest() -> dict[str, Instance]:
    if not INSTANCE.exists(): return {}

    async with aiofiles.open(INSTANCE, mode='rb') as f:
        content = await f.read()

    data = tomllib.loads(content.decode())
    raw: dict = data.get('instances', {})

    return {k: Instance(**v) for k, v in raw.items()}

async def write_manifest(instances: dict[str, Instance]):
    data = {'instances': {k: asdict(v) for k, v in instances.items()}}

    if not INSTANCE.parent.exists(): INSTANCE.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(INSTANCE, mode='wb') as f:
        await f.write(tomli_w.dumps(data).encode())

async def create_instance(instance: Instance):
    instances = await read_manifest()

    instance_id = gen_id()
    (INSTANCES / instance_id).mkdir(parents=True, exist_ok=True)

    instances[instance_id] = instance
    await write_manifest(instances)
    return instance_id

def fill_instance(id: str):
    p = (INSTANCES / id)
    (p / '.minecraft').mkdir(exist_ok=True)
    (p / 'logs').mkdir(exist_ok=True)

if __name__ == "__main__":
    inst = Instance(
        name='epic instnace',
        version='26.1.2',
        modloader=ModloaderEnum.VANILLA,
        modloader_version=''
    )
    import asyncio
    id = asyncio.run(create_instance(inst))
    fill_instance(id)
