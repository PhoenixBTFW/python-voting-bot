from discord.ext import commands
import discord
from datetime import datetime, timedelta
import json

class Proposition(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="propose", description="proposes a new rule or role assignment.", guild_ids = [1250568621017661542])
    async def propose(self, ctx: discord.ApplicationContext, proposition: str, description: str, duration_time: str):
        try:
            if not ctx.author.guild_permissions.manage_messages:
                raise commands.MissingPermissions(["manage_messages"])
            
            # load the json and convert hours/days/minutes into seconds
            with open("votes.json", "r") as f:
                filej = json.load(f)
            if duration_time[-1] == "h":
                duration = int(duration_time.strip("h")) * 3600
            elif duration_time[-1] == "d":
                duration = int(duration_time.strip("d")) * 86400
            elif duration_time[-1] == "m":
                duration = int(duration_time.strip("m")) * 60
            else:
                duration = int(duration_time)

            # responds with the proposition, will change to look nicer later
            await ctx.respond(f"""NEW PROPOSITION!
            {proposition}
            {description}
            voting duration: {duration_time}
            expires on: {(datetime.now() + timedelta(seconds=duration))}""")
            
            # get the expiration time, this is used to delete the proposition and edit it when time is up
            expiration = (datetime.now() + timedelta(seconds=duration)).timestamp()


            # get the bots message ID, this way i can store it inside the json
            async for message in ctx.channel.history(limit=50):
                if message.author == ctx.bot.user:
                    msg = message.id
                    break

            # stores the proposition into the json, adding 1 to the index of the last element
            try:
                proposition = {
                    "index": filej[-1]["index"]+1,
                    "proposition": proposition,
                    "description": description,
                    "duration": duration,
                    "expiration": expiration,
                    "channel_id": ctx.channel.id,
                    "message_id": msg,
                    "vote": [0, 0],
                    "voted": ()
                }
            # if there is no elements it'll raise an index error, catch it and set the index to 1 by default
            except IndexError:
                proposition = {
                    "index": 1,
                    "proposition": proposition,
                    "description": description,
                    "duration": duration,
                    "expiration": expiration,
                    "channel_id": ctx.channel.id,
                    "message_id": msg,
                    "vote": [0, 0],
                    "voted": ()
                }

            # add the new proposition
            filej.append(proposition)
            with open("votes.json", "w") as f:
                json.dump(filej, f, indent = 4)

        except commands.MissingPermissions:
            await ctx.respond("You do not have permission to run this command.", ephemeral = True)

    @discord.slash_command(name = "view", description = "View all active propositions", guild_ids = [1250568621017661542])
    async def view(self, ctx: discord.ApplicationContext):
        with open("./votes.json", "r") as f:
            filej = json.load(f)

        for i in range(len(filej)):
            await ctx.respond(f"""CURRENT ACTIVE PROPOSITIONS:
proposition index {filej[i]["index"]}:
{filej[i]["proposition"]}
{filej[i]["description"]}
{int(filej[i]["duration"]/60)}m
""")
            

    @discord.slash_command(name = "vote", description = "Vote on an active proposition", guild_ids = [1250568621017661542])
    async def vote(self, ctx: discord.ApplicationContext, proposition_index: int, vote: discord.Option(str, "Choose a vote", choices = ["yes", "no"])):
        match vote:
            case "yes":
                idx = 0
            case "no":
                idx = 1
        
        with open("./votes.json", "r") as f:
            filej = json.load(f)
            
        if ctx.author.id in filej[proposition_index-1]['voted']:
            await ctx.respond("You have already voted on this proposition")
        else:
            filej[proposition_index-1]['voted'].append(ctx.author.id)
            filej[proposition_index-1]["vote"][idx] += 1

        with open("./votes.json", "w") as f:
            json.dump(filej, f, indent = 4)


def setup(bot):
    bot.add_cog(Proposition(bot))