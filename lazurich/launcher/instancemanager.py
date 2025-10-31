import os
import re
import json
import shutil

INSTANCES_DIR = os.path.expanduser('~/.local/share/lazurich/instances')

os.makedirs(INSTANCES_DIR, exist_ok=True)

def create_instance(name: str, ver: str):
    safename = re.sub(r'[^\w\-]', '', name)
    instance_path = os.path.join(INSTANCES_DIR, safename)

    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(os.path.join(instance_path, '.minecraft'), exist_ok=True)
    os.makedirs(os.path.join(instance_path, 'logs'), exist_ok=True)

    with open(os.path.join(instance_path, 'instance.json'), 'w') as f:
        f.write(json.dumps({
            'name': name,
            'desc': 'My amazing instance!',
            'author': os.getlogin(),
            'banner': 'none',
            'icon': 'none',

            'ver': ver,
            'loader': 'none',
            'loaderver': 'none',

            'mods': [],
            'shaders': [],
            'textures': [],

            'path': instance_path,
            'id': safename
        }))

    with open(os.path.join(instance_path, 'log4j2.xml'), 'w') as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
    <Appenders>
        <Console name="SysOut" target="SYSTEM_OUT">
            <PatternLayout pattern="[%d{{HH:mm:ss}}] [%t/%level] (%c{{1}}): %msg%n" />
        </Console>

        <RollingFile name="LogFile" 
                     fileName="{os.path.join(instance_path, 'logs')}/latest.log" 
                     filePattern="{os.path.join(instance_path, 'logs')}/%d{{yyyy-MM-dd}}-%i.log.gz">
            
            <PatternLayout pattern="[%d{{HH:mm:ss}}] [%t/%level] (%c{{1}}): %msg%n" />
            
            <Policies>
                <SizeBasedTriggeringPolicy size="250 MB" />
                </Policies>
            
            <DefaultRolloverStrategy max="10" />

        </RollingFile>
    </Appenders>

    <Loggers>
        <Root level="info">
            <AppenderRef ref="SysOut" />
            <AppenderRef ref="LogFile" />
        </Root>
    </Loggers>
</Configuration>""")

def get_instances():
    instances = os.listdir(INSTANCES_DIR)
    returns = []
    for instance in instances:
        ipath = os.path.join(INSTANCES_DIR, instance)
        if not os.path.isdir(ipath): continue

        with open(os.path.join(ipath, 'instance.json')) as f: returns.append(json.loads(f.read()))

    return returns

def get_instance(id: str):
    with open(os.path.join(INSTANCES_DIR, id, 'instance.json'), 'r') as f:
        return json.loads(f.read())

def delete_instance(id: str):
    shutil.rmtree(os.path.join(INSTANCES_DIR, id))

if __name__ == "__main__":
    create_instance('Epic Instance', '1.21.1')
