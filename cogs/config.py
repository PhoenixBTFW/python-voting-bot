import discord
from discord.ext import commands
import json

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = "addrole", description = "Add a role to weigh more in votes", guild_ids = [1250568621017661542])
    async def addrole(self, ctx: discord.ApplicationContext, roleid: str, weight: int):
        with open("botconfig.json", "r") as f:
            filej = json.load(f)

        if any(entry["roleID"] == roleid for entry in filej):
            await ctx.respond("This role already has a weight, use the config role to change it.", ephemeral=True)
            return
        
        if not ctx.guild.get_role(int(roleid)):
            await ctx.respond("Incorrect role ID, role not found.", ephemeral=True)
            return

        newrole = {
            "roleID": roleid,
            "weight": weight
        }
        filej.append(newrole)

        with open("botconfig.json", "w") as f:
            json.dump(filej, f, indent=4)
        await ctx.respond(f"Successfully added role <@&{roleid}> with weight `{weight}`", ephemeral=True)
    
    
    @discord.slash_command(name = "roleweight", description = "modify the weight to one of the roles", guild_ids = [1250568621017661542])
    async def roleweight(self, ctx: discord.ApplicationContext, roleid: str, new_weight: int):
        found = False
        with open("botconfig.json", "r") as f:
            filej = json.load(f)
        
        for i in range(len(filej)):
            if roleid == filej[i]["roleID"]:
                filej[i]["weight"] = new_weight
                found = True
                break
            else:
                pass
            
        if found:
            with open("botconfig.json", "w") as f:
                json.dump(filej, f, indent=4)
            await ctx.respond(f"role <@&{int(roleid)}> weight changed to {new_weight}", ephemeral = True)
        else:
            await ctx.respond("no such role in the configuration, use `/addrole` to add a new role weight", ephemeral = True)
    
    @discord.slash_command(name = "deleterole", description = "delete a role's weight from the configuration", guild_ids = [1250568621017661542])
    async def deleterole(self, ctx: discord.ApplicationContext, roleid: str):
        with open("botconfig.json", "r") as f:
            filej = json.load(f)

        otherRoles = []
        for i in range(len(filej)):
            if roleid != filej[i]["roleID"]:
                otherRoles.append(filej[i])
        
        if len(otherRoles) != len(filej):
            await ctx.respond("successfully removed the role", ephemeral = True)
            with open("botconfig.json", "w") as f:
                json.dump(otherRoles, f, indent = 4)
        else:
            await ctx.respond("role doesn't exist in the configuration", ephemeral = True)

def setup(bot):
    bot.add_cog(Config(bot))