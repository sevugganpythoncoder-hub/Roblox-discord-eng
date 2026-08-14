import os
import discord
from discord.ext import commands
import aiohttp

TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
PREFIX = "!"
ROBLOX_GROUP_ID = "Your GROUP Roblox ID HERE"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

@bot.command(name="lookup")
async def lookup(ctx, username: str):
    async with aiohttp.ClientSession() as session:
        url_id = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        
        async with session.post(url_id, json=payload) as resp:
            data = await resp.json()
            if not data.get("data"):
                return await ctx.send(f"User `{username}` not found on Roblox.")
            
            user_id = data["data"][0]["id"]
            display_name = data["data"][0]["displayName"]

        url_profile = f"https://users.roblox.com/v1/users/{user_id}"
        async with session.get(url_profile) as resp:
            profile_data = await resp.json()

        url_thumb = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=false"
        async with session.get(url_thumb) as resp:
            thumb_data = await resp.json()
            thumb_url = thumb_data["data"][0]["imageUrl"] if thumb_data.get("data") else ""

        embed = discord.Embed(title=f"Roblox Profile: {username}", color=discord.Color.blue())
        embed.add_field(name="Display Name", value=display_name, inline=True)
        embed.add_field(name="User ID", value=user_id, inline=True)
        embed.add_field(name="Banned", value=profile_data.get("isBanned", False), inline=True)
        embed.add_field(name="Account Age", value=f"{profile_data.get('created', '')[:10]}", inline=False)
        if thumb_url:
            embed.set_thumbnail(url=thumb_url)
            
        await ctx.send(embed=embed)

@bot.command(name="checkrank")
async def checkrank(ctx, username: str):
    async with aiohttp.ClientSession() as session:
        url_id = "https://users.roblox.com/v1/usernames/users"
        async with session.post(url_id, json={"usernames": [username]}) as resp:
            data = await resp.json()
            if not data.get("data"):
                return await ctx.send(f"User `{username}` not found.")
            user_id = data["data"][0]["id"]

        url_group = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
        async with session.get(url_group) as resp:
            group_data = await resp.json()
            
            user_rank = "Guest (Not in Group)"
            role_id = 0
            
            if "data" in group_data:
                for entry in group_data["data"]:
                    if entry["group"]["id"] == ROBLOX_GROUP_ID:
                        user_rank = entry["role"]["name"]
                        role_id = entry["role"]["rank"]
                        break

        embed = discord.Embed(title=f"Group Rank Check: {username}", color=discord.Color.green())
        embed.add_field(name="Group ID", value=ROBLOX_GROUP_ID, inline=False)
        embed.add_field(name="Rank Name", value=user_rank, inline=True)
        embed.add_field(name="Rank Level", value=role_id, inline=True)
        
        await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
