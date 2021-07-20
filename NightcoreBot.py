import subprocess
from subprocess import PIPE
import asyncio
import discord
import requests
import async_soundcloud_dl
import os

BOT_TOKEN = ""

dl_num = 0
if os.path.exists(os.getcwd().replace("\\", "/") + "/files/music") == False:
    os.makedirs(os.getcwd().replace("\\", "/") + "/files/music")

async def nightcore_encode_ffmpeg(mp3, pitch = 1, speed = 1):
    loop = asyncio.get_event_loop()

    filename = os.path.splitext(os.path.basename(mp3))[0]
    dirname = os.path.dirname(mp3)
    proc = subprocess.Popen(
        rf'{ffmpeg_path} -i "{mp3}" -filter:a "atempo={speed},asetrate=44100*{pitch}" "{dirname + "/" + filename + "-Nightcore" + ".mp3"}" -y',
        shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    
    print("Waiting Encoding...")
    try:
        await loop.run_in_executor(None, proc.communicate, "timeout=15")
    except Exception:
        proc.kill()
        return "Error"
    return dirname + "/" + filename + "-Nightcore" + ".mp3"

async def youtube_dl_mp3(url):
    loop = asyncio.get_event_loop()

    global dl_num
    dl_num += 1
    filename = os.getcwd().replace("\\", "/") + f"/files/music/audio-{dl_num}.mp3"
    proc = subprocess.Popen(
        rf'youtube-dl --extract-audio --audio-format mp3 --audio-quality 0 -o "{filename}" --ffmpeg-location "{ffmpeg_path}" "{url}"',
        shell=True, stdout=PIPE, stderr=PIPE, encoding="utf-8")
    try:
        a, b = await loop.run_in_executor(None, proc.communicate, "timeout=30")
        print(a, b)
    except Exception:
        proc.kill()
        return "Error"
    return filename

client = discord.Client()

@client.event
async def on_ready():
    print("Discord Logged in " + client.user.name)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == "a":
        await message.channel.send("Nice")
    #if message.content == "enc":
    #    mp3_text = await nightcore_encode_ffmpeg("a")
    #    await message.channel.send(mp3_text)
    #if message.content == "soundl":
    #    url = "https://soundcloud.com/asteriskbtlg/os-asterisk-makina-remix-from-asterisk-works-3"
    #    dl_filename = await async_soundcloud_dl.dl(url)
    #    await message.channel.send(dl_filename)
    if "-nightcore" in message.content or "-nc" in message.content:
        args = sort_args(message.content)
        if len(args) < 1:
            if len(message.attachments) < 1:
                await message.channel.send("Usage: `-nc (Soundcloud URL / Youtube URL) (Pitch) (Speed)`")
                await message.channel.send("Usage: `-nc (Pitch) (Speed) with MP3 FILE`")
                return
        after_delete_send = await message.channel.send("Downloading mp3...")
        #If youtube
        if "youtube.com" in message.content or "youtu.be" in message.content:
            try:
                dl_filename = await youtube_dl_mp3(args[1])
            except Exception as e:
                print("Download Error -> " + str(e))
                await message.channel.send("Invaild URL")
                return
        #If soundcloud
        elif "soundcloud.com" in message.content:
            try:
                dl_filename = await async_soundcloud_dl.dl(args[1])
            except Exception as e:
                print("Download Error -> " + str(e))
                await message.channel.send("Invaild URL")
                return
        #If file
        elif len(message.attachments) >= 1:
            print(message.attachments[0])
            dl_filename = os.getcwd().replace("\\", "/") +  "/files/music/" + message.attachments[0].filename
            uploaded_url = message.attachments[0].url
            mp3_data = requests.get(uploaded_url).content

            with open(dl_filename ,mode='wb') as f: # wb でバイト型を書き込める
                f.write(mp3_data)
            args.append(args[2])
            args[2] = args[1]
        else:
            await message.channel.send("Usage: `-nc (Soundcloud URL / Youtube URL) (Pitch) (Speed)`")
            await message.channel.send("Usage: `-nc (Pitch) (Speed) with MP3 FILE`")
            return
        await after_delete_send.delete()
        print("Download File -> " + dl_filename)
        filename = os.path.splitext(os.path.basename(dl_filename))[0]
        #If no encode
        if len(args) < 3:
            await message.channel.send(f"`{filename}`", file=discord.File(dl_filename))
            return
        #If arg 3 is not set
        if len(args) < 4:
            args.append("1")
        after_delete_send = await message.channel.send("Encoding Nightcore...")
        encoded_filename = await nightcore_encode_ffmpeg(dl_filename, args[2], args[3])
        await after_delete_send.delete()
        if encoded_filename == "Error":
            await message.channel.send("Error")
            return
        os.remove(dl_filename)
        print(filename)
        print(encoded_filename)
        print(args[2], args[3])
        await message.channel.send(f"`{filename}`\nPitch -> `{args[2]}` | Speed -> `{args[3]}`", file=discord.File(encoded_filename))
        os.remove(encoded_filename)

def sort_args(text) -> list:
    if " " in text:
        return text.split(" ")
    if "　" in text:
        return text.split("　")
    result = []
    return result

client.run(BOT_TOKEN)