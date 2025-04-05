import discord
from discord.ext import commands
import os
import asyncio
import json
from datetime import datetime


async def remove_expired_votes():
    while True:
        try:
            with open("votes.json", "r") as f:
                filej = json.load(f)

            now = datetime.now().timestamp()

            active_votes = []
            for i in range(len(filej)):
                exp = filej[i]["expiration"]
                if exp > now:
                    active_votes.append(filej[i])
                else:
                    async def edit():
                        channel = demo.get_channel(filej[i]["channel_id"])
                        msg = await channel.fetch_message(filej[i]["message_id"])
                        await msg.edit(content = f"deleted proposition {filej[i]['proposition']} with votes {filej[i]['vote'][0]} Yes / {filej[i]['vote'][1]} No")
                    await edit()

            if len(active_votes) != len(filej):
                with open("votes.json", "w") as f:
                    json.dump(active_votes, f, indent=4)
                print("deleted something")
        except Exception as e:
            print(e)

        await asyncio.sleep(10)

demo = discord.Bot(owner_id=1084280725794197604)

@demo.event
async def on_ready():
    print(f"logged into {demo.user.name}#{demo.user.discriminator}")
    asyncio.create_task(remove_expired_votes())

with open("config.json") as f:
    filej = json.load(f)
    token = filej["token"]
try:
    for file in os.listdir("./cogs"):
        try:
            if file.endswith(".py"):
                if file == ("extensions.py"):
                    continue
                demo.load_extension("cogs." + file[:-3])
                print(f"loaded extension {file}")
        except Exception as e:
            print(e)
except:
    pass

@demo.slash_command(name="reload", description="Reloads all currently loaded cogs.", guild_ids=[1250568621017661542])
async def reload_cogs(interaction: discord.Interaction):
    if interaction.user.id != demo.owner_id:
        print(f"user {interaction.user.name} ({interaction.user.id}) Tried to run the reload command")
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    loaded_cogs = list(demo.cogs.keys())
    
    for cog in loaded_cogs:
        try:
            demo.reload_extension(f"cogs.{cog.lower()}")
            print(f"reloaded {cog}")
            await interaction.respond(f"successfully reloaded {cog}", ephemeral=True)
        except Exception as e:
            print(e)

demo.run(token)