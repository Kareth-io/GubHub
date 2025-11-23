import discord, pyautogui, asyncio, os
from dotenv import load_dotenv
from discord.ext import commands

#.env 
load_dotenv()

#Globals
TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID"))
ALLOWED_ROLE_NAME = os.getenv("ALLOWED_ROLE_NAME")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


#Permission Validation, runs before all commands
@bot.before_invoke
async def check_permissions(ctx):
    # Check if command is in the allowed channel
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        raise commands.CommandInvokeError("Error: User wrong channel")

    # Check if user has the required role
    role = discord.utils.get(ctx.author.roles, name=ALLOWED_ROLE_NAME)
    if role is None:
        await ctx.send(f"You need the `{ALLOWED_ROLE_NAME}` role to use this command.")
        raise commands.CommandInvokeError("Error: User missing role")

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    print(f"Restricted to channel ID: {ALLOWED_CHANNEL_ID}")
    print(f"Restricted to role: {ALLOWED_ROLE_NAME}")
    for cog in ["keyboard", "mouse"]:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"Cog:{cog} loaded successfully!")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")

# Error handler for check failures
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        # This block will handle CommandInvokeError and print to console
        print(f"CommandInvokeError in command '{ctx.command.name}':")
        print(f"Original exception: {error.original}")
        # You can also print the full traceback for more details:
        # import traceback
        # traceback.print_exception(type(error.original), error.original, error.original.__traceback__)
    else:
        # For other types of errors, you might want to send a message to Discord
        await ctx.send(f"An unexpected error occurred: {error}")

bot.run(TOKEN)

