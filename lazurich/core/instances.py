from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.paths import INSTANCES, INSTANCE
from lazurich.core.exceptions import AlreadyExistsException, UserException
from hashlib import sha1
from random import randint
import aiofiles
import re2
import json
from pathlib import Path

async def read_manifest() -> list[Instance]:
    path = INSTANCE
    if not path.exists(): return []

    async with aiofiles.open(INSTANCE, mode='r') as f:
        content = await f.read()

    instances = []

    for i in content.loads()['instances']['list']:
        instances.append(Instance(**i))

    return instances

async def sanitize_dirname(raw_string: str):
    clean = re2.sub(r'[^\w\s-]', '', raw_string)
    clean = re2.sub(r'[-\s]+', '_', clean).strip('-_')
    return clean[:255] or sha1(raw_string.encode('utf-8')).hexdigest()

async def create_instance(instance: Instance):
    if instance in read_manifest(): raise AlreadyExistsException(f'Instance {instance.name} already exists!')
    
    path = INSTANCES / await sanitize_dirname(instance.name)

    if path.exists(): instance.path = f'{await sanitize_dirname(instance.name)}-{randint(10000, 99999)}'
    else: instance.path = sanitize_dirname(instance.name)
