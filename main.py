import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
from model import session, User, WordsCount

mybot = commands.Bot(command_prefix=".", intents=discord.Intents.all())



# ----------------------------------------------------------
                    # on ready event
# ----------------------------------------------------------
@mybot.event
async def on_ready():
    print("Bot is ready")
    try:
        synced = await mybot.tree.sync()
        print(f"Synced {len(synced)} command!")
    except Exception as e:
        print(e)

# ----------------------------------------------------------
                    # new member join event
# ----------------------------------------------------------
@mybot.event
async def on_member_join(member: discord.Member):
    try:
        welcome_channel = mybot.get_channel(1225861521670930443)
        message = f"{member.display_name} welcome to the server"
        await welcome_channel.send(message)
    except Exception as e:
        print(e)


# ----------------------------------------------------------
                    # on message event
# ----------------------------------------------------------
@mybot.event
async def on_message(message: discord.Message):
    try:
        if message.author.bot or message.content.startswith("@"):
            return
        print(message.content)
        user = session.query(User).get(message.author.id)
        server = session.query(User).get(message.guild.id)
        if server is None:
            server = User(id=message.guild.id, username=message.guild.name)
            session.add(server)
            session.commit()
        if user is None:
            print("creating new user")
            user = User(id=message.author.id, username=message.author.name)
            session.add(user)
            session.commit()
        words = message.content.split(" ")
        for word in words:
            user_words = session.query(WordsCount).filter_by(word=word, user_id=user.id).first()
            server_words = session.query(WordsCount).filter_by(word=word, user_id=server.id).first()
            if user_words is None:
                user_words = WordsCount(user_id=user.id, word=word, count=1)
                session.add(user_words)
                session.commit()
            if server_words is None:
                server_words = WordsCount(user_id=server.id, word=word, count=1)
                session.add(server_words)
                session.commit()
            else:
                user_words.count += 1
                server_words.count += 1
        session.commit()
        print(f"{message.author} send {message.content} toatl words: {len(words)}")
    except Exception as e:
        print(e)


# ----------------------------------------------------------
                    # get roles command
# ----------------------------------------------------------
@mybot.tree.command(name="get-roles", description="get roles of server members")
@app_commands.describe(user="enter a user")
async def get_roles(interaction: discord.Interaction, user: discord.Member | None):
    try:
        if user is None:
            user = interaction.user
        user_roles = user.roles
        value = ""
        for role in user_roles:
            value += f"\u2022 {role.name}\n"
        embeded_msg = discord.Embed(title=f"Roles", description=value, color=discord.Color.blue())
        embeded_msg.set_author(name=user.display_name, icon_url=user.display_avatar)
        await interaction.response.send_message(embed=embeded_msg)
    except Exception as e:
        await interaction.response.send_message("Bot was unable to send message")


# ----------------------------------------------------------
                    # Role select command
# ----------------------------------------------------------
        
# -------------| ui select |---------------------------------
class Roles(discord.ui.Select):
    def __init__(self, roles, user_roles):
        options = [
            discord.SelectOption(label=role.name, value=role.id, default=(role in user_roles)) for role in roles
        ]
        self.initail_roles = user_roles
        super().__init__(placeholder="Select roles...", options=options, max_values=len(roles))

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_roles = [interaction.guild.get_role(int(value)) for value in self.values]
            for role in self.initail_roles:
                if role not in selected_roles:
                    await interaction.user.remove_roles(role)
            await interaction.user.add_roles(*selected_roles)
            await interaction.response.send_message(f"Added roles: {', '.join(role.name for role in selected_roles)}", ephemeral=True, delete_after=5.0)
            await self.view.onSubmit()
        except discord.errors.Forbidden as e:
            await interaction.response.send_message("Bot does not have role manage access or you are trying to add a higher priority role.", delete_after=5.0)
            await self.view.onSubmit(interaction)
        except Exception as e:
            await interaction.response.send_message("Server error", delete_after=5.0)

# ------------------| ui View |--------------------------
class SelectRoleView(discord.ui.View):
    def __init__(self, roles, user_roles):
        super().__init__(timeout=180)
        self.add_item(Roles(roles, user_roles))
    
    async def onSubmit(self):
        self.stop()

# -----------------| role handler function |-----------------------------
@mybot.tree.command(name="change-roles", description="Change you role")
async def get_all_roles(interaction: discord.Interaction):
    try:
        server_created_roles = []
        user_roles = interaction.user.roles
        user_roles = [role for role in user_roles if role.name != "@everyone"]
        roles = interaction.guild.roles
        for role in roles:
            if role.is_bot_managed() or role.name == "@everyone":
                continue
            server_created_roles.append(role)
        view = SelectRoleView(server_created_roles, user_roles)
        await interaction.response.send_message(view=view, ephemeral=True, delete_after=10.0)
        await view.wait()
    except discord.errors.Forbidden:
        await interaction.response.send_message("Bot does not have enough permissions", delete_after=5.0)
    except Exception as e:
        await interaction.response.send_message("Server error", delete_after=5.0)


# ----------------------------------------------------------
                    # simple greet command
# ----------------------------------------------------------
@mybot.tree.command(name="greet")
async def greet(interaction: discord.Interaction):
    try:
        await interaction.response.send_message(f"Hello {interaction.user}, how are you?")
    except discord.errors.Forbidden:
        await interaction.response.send_message("Bot does not have enough permissions", delete_after=5.0)
    except Exception as e:
        await interaction.response.send_message("Server error", delete_after=5.0)



# ----------------------------------------------------------
                    # word-status command
# ----------------------------------------------------------
@mybot.tree.command(name="word-status", description="Get the 10 most used words in server")
async def word_status(interaction: discord.Interaction):
    try:
        distinct_words = session.query(WordsCount).filter_by(user_id=interaction.guild.id).order_by(WordsCount.count.desc()).limit(10)
        report = ""
        for word in distinct_words:
            report += f"{word.word}: {word.count}\n"
        if not report:
            report = "No messages found"
        embeded_msg = discord.Embed(title="Most used words in server", description=report, color=discord.Color.green())
        embeded_msg.set_author(name=f"{interaction.guild.name}", icon_url=interaction.guild.icon)
        await interaction.response.send_message(embed=embeded_msg)
    except discord.errors.Forbidden:
        await interaction.response.send_message("Bot does not have enough permissions", delete_after=5.0)
    except Exception as e:
        await interaction.response.send_message("Server error", delete_after=5.0)


# ----------------------------------------------------------
                    # user-status command
# ----------------------------------------------------------
@mybot.tree.command(name="user-status", description="Get the 10 most used words by the user")
async def user_status(interaction: discord.Interaction, user: discord.Member | None):
    try:
        if user is None:
            user = interaction.user
        distinct_words = session.query(WordsCount).filter_by(user_id=user.id).order_by(WordsCount.count.desc()).limit(10)
        report = ""
        for word in distinct_words:
            report += f"{word.word}: {word.count}\n"
        if not report:
            report = "No messages found"
        embeded_msg = discord.Embed(title=f"Most used words by {user.display_name}", description=report, color=discord.Color.green())
        embeded_msg.set_author(name=user.display_name, icon_url=user.display_avatar)
        await interaction.response.send_message(embed=embeded_msg)
    except discord.errors.Forbidden:
        await interaction.response.send_message("Bot does not have enough permissions", delete_after=5.0)
    except Exception as e:
        await interaction.response.send_message("Server error", delete_after=5.0)


mybot.run(os.environ.get("KEY"))