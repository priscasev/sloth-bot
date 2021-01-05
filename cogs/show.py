import discord
from discord.ext import commands
from mysqldb import the_database
from extra.useful_variables import rules
import os
import subprocess
import sys

allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('MOD_ROLE_ID'))]


class Show(commands.Cog):
    '''
    Commands involving showing some information related to the server.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Show cog is ready!')

    # Shows how many members there are in the server
    @commands.command()
    async def members(self, ctx):
        '''
        Shows how many members there are in the server (including bots).
        '''
        await ctx.message.delete()
        all_users = ctx.guild.members
        await ctx.send(f'{len(all_users)} members!')


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def about(self, ctx) -> None:
        """ Shows some information about the bot itself. """

        embed = discord.Embed(
            title=f"__About ({self.client.user})__",
            description=f"The {self.client.user} bot is an all-in-one bot designed specially for `The Language Sloth` server. " \
            + "It has many different commands and features to best satisfy our needs in this server, and it's continuously being improved.",
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            url='https://thelanguagesloth.com/bots/sloth/'
        )

        lines = subprocess.getstatusoutput('find . -name "*.py" -not -path "./venv*" | xargs wc -l')
        lines = lines[1].split()[-2] if lines else 0

        embed.add_field(
            name="__Lines__",
            value=f"```apache\n{lines} lines of code. (Python)```",
            inline=True)
        embed.add_field(
            name="__Commands__",
            value=f"```apache\n{len([_ for _ in self.client.walk_commands()])} commands.```",
            inline=True)
        embed.add_field(
            name="__Categories__",
            value=f"```apache\n{len(self.client.cogs)} categories.```",
            inline=True)
        embed.add_field(name="__Operating System__",
            value=f'```apache\nThe bot is running and being hosted on a "{sys.platform}" machine.```',
            inline=True)

        embed.set_author(name='DNK#6725', url='https://discord.gg/languages', 
            icon_url='https://cdn.discordapp.com/attachments/719020754858934294/720289112040669284/DNK_icon.png')
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)



    # Shows the specific rule
    @commands.command()
    async def rule(self, ctx, numb: int = None):
        '''
        Shows a specific server rule.
        :param numb: The number of the rule to show.
        '''
        await ctx.message.delete()
        if numb is None:
            return await ctx.send('**Invalid parameter!**')

        if numb > len(rules) or numb <= 0:
            return await ctx.send(f'**Inform a rule from `1-{len(rules)}` rules!**')

        rule_index = list(rules)[numb - 1]
        embed = discord.Embed(title=f'Rule - {numb}# {rule_index}', description=rules[rule_index],
                              colour=discord.Colour.dark_green())
        embed.set_footer(text=ctx.author.guild.name)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(*allowed_roles)
    async def rules(self, ctx):
        '''
        (MOD) Sends an embedded message containing all rules in it.
        '''
        await ctx.message.delete()
        embed = discord.Embed(title="Discord’s Terms of Service and Community Guidelines",
                              description="Rules Of The Server", url='https://discordapp.com/guidelines',
                              colour=1406210,
                              timestamp=ctx.message.created_at)
        i = 1
        for rule, rule_value in rules.items():
            embed.add_field(name=f"{i} - {rule}", value=rule_value, inline=False)        
            i += 1

        embed.add_field(name="<:zzSloth:686237376510689327>", value="Have fun!", inline=True)
        embed.add_field(name="<:zzSloth:686237376510689327>", value="Check our lessons!", inline=True)
        embed.set_footer(text='Cosmos',
                         icon_url='https://cdn.discordapp.com/avatars/423829836537135108/da15dea5017edf5567e531fc6b97f935.jpg?size=2048')
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        embed.set_author(name='The Language Sloth', url='https://discordapp.com',
                         icon_url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        await ctx.send(
            content="Hello, **The Language Sloth** is a public Discord server for people all across the globe to meet ,learn languages and exchange cultures. here are our rules of conduct.",
            embed=embed)


    @commands.command(aliases=['ss'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def server_status(self, ctx) -> None:
        """ Shows some server statuses. """

        member = ctx.author

        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT 
            STR_TO_DATE(complete_date, '%d/%m/%Y') AS Months,
            SUM(m_joined) - SUM(m_left) AS 'Total Joins',
            members AS 'First Member Record of the Month',
            MAX(members) AS 'Last Member Record of the Month'
            FROM DataBumps
            GROUP BY YEAR(Months), MONTH(Months)
            """)

        months = await mycursor.fetchall()
        await mycursor.close()

        embed = discord.Embed(
            title="__Server's Monthly Statuses__",
            description="**N**: Month counting;\n"\
            +"**Date**: Months respective to the data;\n"\
            +"**Joins**: New members;\n"\
            +"**First**: Total members in the first day of the month;\n"\
            +"**Last**: Total members in the last day of the month.",
            color=member.color,
            timestamp=ctx.message.created_at,
            url="http://thelanguagesloth.com"
        )

        temp_text1 = f"{'N':>2} | {'Date':<4} | {'Joins':^5} | {'First':>5} | {'Last':>5}"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text1}```",
            inline=False
        )

        temp_text2 = ''
        # the_months = {1: '',2: '',3: '',4: '',5: '',6: '',7: '',8: '',9: '',10: '',11: '',12: ''}
        for i, month in enumerate(months):
            the_month = month[0].strftime('%b')
            temp_text2 += f"{i+1:>2} | {the_month:<4} | {month[1]:^5} | {month[2]:>5} | {month[3]:>5}\n"

        embed.add_field(
            name=f"{'='*35}",
            value=f"```apache\n{temp_text2}```",
            inline=False
        )

        embed.set_author(name=member, icon_url=member.avatar_url)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Show(client))
