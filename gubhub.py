import discord, pyautogui, asyncio, os
from dotenv import load_dotenv
from discord.ext import commands

#.env 
load_dotenv()

#Globals
TOKEN = os.getenv("TOKEN")
ALLOWED_CHANNEL_ID = os.getenv("ALLOWED_CHANNEL_ID")
ALLOWED_ROLE_NAME = os.getenv("ALLOWED_ROLE_NAME")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Custom check: Verify channel and role
def check_permissions():
    async def predicate(ctx):
        # Check if command is in the allowed channel
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            print("Failed channel verification")
            return False

        # Check if user has the required role
        role = discord.utils.get(ctx.author.roles, name=ALLOWED_ROLE_NAME)
        if role is None:
            await ctx.send(f"You need the `{ALLOWED_ROLE_NAME}` role to use this command.")
            return False

        return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    print(f"Restricted to channel ID: {ALLOWED_CHANNEL_ID}")
    print(f"Restricted to role: {ALLOWED_ROLE_NAME}")

@bot.command(name="key")
@check_permissions()
async def press_key(ctx, key: str):
    """Press a single key on the keyboard. Usage: !key <key>"""
    try:
        pyautogui.press(key)
        await ctx.send(f"Pressed key: `{key}`")
    except Exception as e:
        await ctx.send(f"Error pressing key: {e}")

@bot.command(name="type")
@check_permissions()
async def type_text(ctx, *, text: str):
    """Type a string of text. Usage: !type <text>"""
    try:
        pyautogui.typewrite(text, interval=0.05)
        await ctx.send(f"Typed: `{text}`")
    except Exception as e:
        await ctx.send(f"Error typing text: {e}")

@bot.command(name="hotkey")
@check_permissions()
async def press_hotkey(ctx, *keys):
    """Press a hotkey combination. Usage: !hotkey ctrl c"""
    try:
        pyautogui.hotkey(*keys)
        await ctx.send(f"Pressed hotkey: `{' + '.join(keys)}`")
    except Exception as e:
        await ctx.send(f"Error pressing hotkey: {e}")

@bot.command(name="hold")
@check_permissions()
async def hold_key(ctx, key: str, duration: float = 0.5):
    """Hold a key for a duration. Usage: !hold <key> <seconds>"""
    try:
        pyautogui.keyDown(key)
        await asyncio.sleep(duration)
        pyautogui.keyUp(key)
        await ctx.send(f"Held key `{key}` for {duration} seconds")
    except Exception as e:
        await ctx.send(f"Error holding key: {e}")

@bot.command(name="keys")
@check_permissions()
async def list_keys(ctx):
    """List common available keys."""
    common_keys = f"The List of available keys can be found here: https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys"
    await ctx.send(common_keys)

# Error handler for check failures
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass  # Already handled in the check
    else:
        await ctx.send(f"An error occurred: {error}")

bot.run(TOKEN)

