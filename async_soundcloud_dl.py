import asyncio
from sclib.asyncio import SoundcloudAPI, Track
import os

async def dl(url) -> str:
    api = SoundcloudAPI()
    track = await api.resolve(url)

    assert type(track) is Track

    replace_linux_path = os.getcwd().replace("\\", "/")
    filename = f'{replace_linux_path}/files/music/{track.artist} - {track.title}.mp3'

    try:
        with open(filename, 'wb+') as fp:
            await track.write_mp3_to(fp)
    except Exception as e:
        filename = f'{replace_linux_path}/files/music/audio.mp3'
        with open(filename, 'wb+') as fp:
            await track.write_mp3_to(fp)

    return filename

#loop = asyncio.get_event_loop()
#loop.run_until_complete(dl("https://soundcloud.com/asteriskbtlg/os-asterisk-makina-remix-from-asterisk-works-3"))