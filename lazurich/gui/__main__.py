from pathlib import Path

import slint

from lazurich.api.microsoft import get_msa_token, do_full_auth
from lazurich.core.assets import download_version_assets, download_version_manifest
from lazurich.core.instances import fill_instance, create_instance
from lazurich.core.jars import download_version_jar
from lazurich.core.launcher import launch_game
from lazurich.core.models.general import Instance, ModloaderEnum
from lazurich.core.natives import extract_natives, download_natives
from lazurich.core.paths import INSTANCES


class App(slint.load_file(Path(__file__).parent / 'layouts' / 'main.slint').AppWindow):
    @slint.callback
    async def b_launch_game(self):
        await download_version_assets('1.20.1')
        await download_version_manifest('1.20.1')
        await download_natives('1.20.1')
        extract_natives('1.20.1')
        await download_version_jar('1.20.1')

        inst = Instance(name='NOT epic instnace (1.20.1)', version='1.20.1', modloader=ModloaderEnum.VANILLA,
                        modloader_version='')
        instance_id = await create_instance(inst)
        fill_instance(instance_id)

        msa = get_msa_token()
        prof, token = await do_full_auth(msa)
        launch_game('1.20.1', INSTANCES / instance_id / '.minecraft', prof, token)

app = App()
app.run()