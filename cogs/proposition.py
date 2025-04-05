from discord.ext import commands
import discord
from datetime import datetime, timedelta
import json

class Proposition(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.expiration = None

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

            # get the expiration time, this is used to delete the proposition and edit it when time is up
            self.expiration = (datetime.now() + timedelta(seconds=duration)).timestamp()


            # responds with the proposition, will change to look nicer later
            await ctx.respond(f"""NEW PROPOSITION!
    {proposition}
    {description}
    voting duration: {duration_time}
    expires on: <t:{int(self.expiration)}:R>""")
            

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
                    "expiration": self.expiration,
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
                    "expiration": self.expiration,
                    "channel_id": ctx.channel.id,
                    "message_id": msg,
                    "vote": [0, 0],
                    "voted": ()
                }

            # add the new proposition
            filej.append(proposition)
            with open("votes.json", "w") as f:
                json.dump(filej, f, indent = 4)

        # message when no perms
        except commands.MissingPermissions:
            await ctx.respond("You do not have permission to run this command.", ephemeral = True)

    @discord.slash_command(name = "view", description = "View all active propositions", guild_ids = [1250568621017661542])
    async def view(self, ctx: discord.ApplicationContext):
        with open("./votes.json", "r") as f:
            filej = json.load(f)
        if len(filej) != 0:
            for i in range(len(filej)):
                await ctx.respond(f"""CURRENT ACTIVE PROPOSITIONS:
    proposition index: {filej[i]["index"]}
    {filej[i]["proposition"]}
    {filej[i]["description"]}
    <t:{int(filej[i]["expiration"])}:R>
    """)
        else:
            await ctx.respond("No active proposals at the moment", ephemeral = True)


    @discord.slash_command(name = "vote", description = "Vote on an active proposition")
    async def vote(self, ctx: discord.ApplicationContext, proposition_index: int, vote: discord.Option(str, "Choose a vote", choices = ["yes", "no"])):
        match vote:
            case "yes":
                idx = 0
            case "no":
                idx = 1
        
        with open("./votes.json", "r") as f:
            filej = json.load(f)
            
        # check if the userID is in the tuple for people who voted already
        # try to catch if there is no one who voted
        try:
            if ctx.author.id in filej[proposition_index-1]['voted']:
                await ctx.respond("You have already voted on this proposition")
            else:
                with open("botconfig.json", "r") as f:
                    filed = json.load(f)

                for i in range(len(filej)):
                    # try to catch something, i actually just don't remember
                    try:
                        # checks if the user has one of the weighted roles
                        if ctx.author.get_role(int(filed[i]["roleID"])) is not None:
                            filej[proposition_index-1]['voted'].append(ctx.author.id)
                            filej[proposition_index-1]['vote'][idx] += int(filed[i]['weight'])
                            await ctx.respond(f"Successfully added your vote for `{int(filed[i]['weight'])}`", ephemeral = True)
                            # break the loop if he does
                            break
                        # if the user doesn't have a weighted role, their vote will be 1
                        else:
                            filej[proposition_index-1]['voted'].append(ctx.author.id)
                            filej[proposition_index-1]["vote"][idx] += 1
                            await ctx.respond("Successfully added your vote for `1`", ephemeral = True)
                    # exception for the try i don't remember
                    except Exception:
                        break
        # exception if no one voted
        except IndexError:
            await ctx.respond("No proposition with such index", ephemeral = True)
        # adds it to the json as the people who voted already
        with open("./votes.json", "w") as f:
            json.dump(filej, f, indent = 4)

    
    @discord.slash_command(name = "clear", description = "clear all proposals", guild_ids = [1250568621017661542])
    async def clear(self, ctx: discord.ApplicationContext):
        empty = []
        with open("votes.json", "w") as f:
            json.dump(empty, f, indent = 4)
        await ctx.respond("cleared all active proposals", ephemeral = True)
        
def setup(bot):
    bot.add_cog(Proposition(bot))