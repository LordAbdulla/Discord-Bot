import os
import aiofiles
import discord
from discord.ext import commands, tasks
import json
from discord.embeds import Embed
from discord.ext.commands import has_permissions
import typing
from discord.errors import Forbidden
from discord.ext.commands.bot import Bot
import asyncio
from itertools import cycle
from discord.user import User
import random



def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


intents = discord.Intents().all()
client = commands.Bot(command_prefix=get_prefix, intents=intents)


client.remove_command("help")
status = cycle(
    ['Watching YouTube', 'Watching You', 'Having Fun', '.help', 'PUBG MOBILE'])


@tasks.loop(seconds=500)
async def status_swap():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_ready():
    print('{0.user} Is Online!'.format(client))

    status_swap.start()


  


@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(message.guild.id)] = '.'
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@client.event
async def on_member_join(member):
  for guild_id in client.welcome_channels:
    if guild_id == member.guild.id:
      channel_id, message = client.welcome_channels[guild_id]
      await client.get_guild(guild_id).get_channel(channel_id).send(f"{message} {member.mention}")
  


  


 


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes.pop(str(guild.id))
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)
    await update_data(users, member)
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)


async def update_data(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1


async def add_experience(users, user, exp):
    users[f'{user.id}']['experience'] += exp


async def level_up(users, user, message):
    with open('levels.json', 'r') as g:
        levels = json.load(g)
    experience = users[f'{user.id}']['experience']
    lvl_start = users[f'{user.id}']['level']
    lvl_end = int(experience**(1 / 4))
    if lvl_start < lvl_end:
        await message.channel.send(
            f'{user.mention} has leveled up!!! **LEVEL** - {lvl_end}')
        users[f'{user.id}']['level'] = lvl_end


@client.command()
async def level(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author()
    id = ctx.member.id
    with open('users.json', 'r') as f:
        users = json.load(f)
    lvl = users[str(id)]['level']
    await ctx.send(f'{member.mention} is on **LEVEL {lvl}**')


@client.event
async def on_message(message):
    if message.author.bot == False:
        with open('users.json', 'r') as f:
            users = json.load(f)
        await update_data(users, message.author)
        await add_experience(users, message.author, 5)
        await level_up(users, message.author, message)
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    await client.process_commands(message)


@client.command(aliases=['cp'])
async def prefix(ctx, prefixset=None):
    if (not ctx.author.guild_permissions.manage_channels):
        await ctx.send('Sorry, you dont have this permission .')
        return
    if (prefixset == None):
        prefixset = '.'
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefixset
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    await ctx.send(f' the prefix has been changed to | {prefixset} | ')


@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.kick(reason=reason)
    embed = discord.Embed(title=f'User {member} has been kick')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)




@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url
    await member.ban(reason=reason)
    embed = discord.Embed(title=f'User {member} has been banned')
    embed.set_author(name=f"requested by {username_1}", icon_url=avatar_1)
    await ctx.send(embed=embed)

@client.command(aliases=["whois"])
async def userinfo(ctx, member: discord.Member = None):
    if not member:  # if member is no mentioned
        member = ctx.message.author  # set member as the author
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=discord.Colour.purple(), timestamp=ctx.message.created_at,
                          title=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name="Roles:", value="".join([role.mention for role in roles]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    print(member.top_role.mention)
    await ctx.send(embed=embed)

@client.command()
@has_permissions(administrator=True)
async def unban(ctx, *, member):
    username_1 = ctx.message.author.name
    avatar_1 = ctx.message.author.avatar_url

    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name,
                                               member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title=f'Unbanned {user.mention}')
            embed.set_author(name=f"requested by {username_1}",
                             icon_url=avatar_1)
            await ctx.send(embed=embed)
            return


@client.command(aliases=['cl'])
async def clear(ctx, amount=10):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send('Sorry, you dont have this permission .')
        return
    amount = amount + 1
    if amount > 101:
        await ctx.send('cannot delete more than 100 messages .')
    else:
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title=f" Messages deleted",
                              description=" Messages has been deleted",
                              color=discord.Color.blue())
        await ctx.send(embed=embed)


@client.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole,
                                          speak=False,
                                          send_messages=False,
                                          read_message_history=True,
                                          read_messages=False)
    embed = discord.Embed(title="muted",
                          description=f"{member.mention} was muted ",
                          colour=discord.Colour.light_gray())
    embed.add_field(name="reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(
        f" you have been muted from: **{guild.name}** | reason: **{reason}** ."
    )


@client.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await member.send(f" you have unmutedd from: - {ctx.guild.name}")
    embed = discord.Embed(title="unmute",
                          description=f" unmuted-{member.mention}",
                          colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)


@client.command()
async def tempmute(ctx, member: discord.Member, time: int, d, *, reason=None):
    guild = ctx.guild

    for role in guild.roles:
        if role.name == "Muted":
            await member.add_roles(role)

            embed = discord.Embed(
                title="muted!",
                description=f"{member.mention} has been tempmuted ",
                colour=discord.Colour.light_gray())
            embed.add_field(name="reason:", value=reason, inline=False)
            embed.add_field(name="time left for the mute:",
                            value=f"{time}{d}",
                            inline=False)
            await ctx.send(embed=embed)

            if d == "s":
                await asyncio.sleep(time)

            if d == "m":
                await asyncio.sleep(time * 60)

            if d == "h":
                await asyncio.sleep(time * 60 * 60)

            if d == "d":
                await asyncio.sleep(time * 60 * 60 * 24)

            await member.remove_roles(role)

            embed = discord.Embed(title="unmute (temp) ",
                                  description=f"unmuted -{member.mention} ",
                                  colour=discord.Colour.light_gray())
            await ctx.send(embed=embed)

            return


@client.command()
async def say(ctx, saymsg=None):
    if saymsg == None:
        return await ctx.send(' you must tell me a thing to say .')
    await ctx.send(saymsg)


@client.command()
async def help(ctx):
    helpEmbed = discord.Embed(title="[    **HELP MENUE**    ]",
                              color=discord.Colour.light_gray())
    helpEmbed.add_field(
        name="[**MODERATION**]",
        value=
        "BAN \n MUTE \n KICK \n CLEAR \n PREFIX \n TEMPMUTE \n SLOWDOWN \n UNBAN \n UNMUTE \n UNBAN \n create_role "
    )
    helpEmbed.add_field(name="[**FUN**]    ", value="SAY \n GCREATE \n LEVEL \n USERINFO")
    await ctx.send(embed=helpEmbed)






@client.command()
async def slowmode(ctx, time: int):
    if (not ctx.author.guild_permissions.manage_messages):
        await ctx.send(' Sorry, you dont have permission . ')
        return
    try:
        if time == 0:
            embed = discord.Embed(title="SlowMode",
                                  description="Status : Off",
                                  color=discord.Color.blue())
            await ctx.send(embed=embed)
            await ctx.channel.edit(slowmode_delay=0)
        elif time > 21600:
            embed = discord.Embed(
                title="SlowMode",
                description=" you cannot set the SlowMode time above 6 hours",
                color=discord.Color.blue())
            return
        else:
            await ctx.channel.edit(slowmode_delay=time)
            embed = discord.Embed(title="SlowMode",
                                  description=f"Status : {time} seconds",
                                  color=discord.Color.blue())
            await ctx.send(embed=embed)
    except Exception:
        await print('Oops .')


@client.command()
async def gcreate(ctx, time=None, *, prize=None):
    if time == None:
        return await ctx.send('please include time .')
    elif prize == None:
        return await ctx.send(' please include a prize .')
    embed = discord.Embed(
        title='**New GiveAway**',
        description=f'{ctx.author.mention} is gifting **{prize}**')
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    gawtime = int(time[0]) * time_convert[time[-1]]
    embed.set_footer(text=f'Giveaway ends in {time}')
    gaw_msg = await ctx.send(embed=embed)
    await gaw_msg.add_reaction("<3")
    await asyncio.sleep(gawtime)
    new_gaw_msg = await ctx.channel.fetch_message(gaw_msg.id)
    users = await new_gaw_msg.reactions[0].users().flatten()
    users.pop(users.index(client.users))
    winner = random.choice(users)
    await ctx.send(
        f" **WINNER!!!** {winner.mention} has won the giveaway , and got **{prize}**"
    )


@client.command(aliases=['make_role'])
@commands.has_permissions(manage_roles=True)
async def create_role(ctx, *, name):
    guild = ctx.guild
    await guild.create_role(name=name)
    await ctx.send(f'Role `{name}` has been created')


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")


@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")


@tempmute.error
async def tempmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(" please mention a member .")
    else:
        await ctx.send(" member not found . ")



client.run(os.getenv('token'))
