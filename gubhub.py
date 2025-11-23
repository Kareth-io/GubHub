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


# Keyboard Commands #
@bot.command(name="key")
async def press_key(ctx, key: str):
    """Press a single key on the keyboard. Usage: !key <key>"""
    try:
        pyautogui.press(key)
        await ctx.send(f"Pressed key: `{key}`")
    except Exception as e:
        await ctx.send(f"Error pressing key: {e}")

@bot.command(name="type")
async def type_text(ctx, *, text: str):
    """Type a string of text. Usage: !type <text>"""
    try:
        pyautogui.typewrite(text, interval=0.05)
        await ctx.send(f"Typed: `{text}`")
    except Exception as e:
        await ctx.send(f"Error typing text: {e}")

@bot.command(name="hotkey")
async def press_hotkey(ctx, *keys):
    """Press a hotkey combination. Usage: !hotkey ctrl c"""
    try:
        pyautogui.hotkey(*keys)
        await ctx.send(f"Pressed hotkey: `{' + '.join(keys)}`")
    except Exception as e:
        await ctx.send(f"Error pressing hotkey: {e}")

@bot.command(name="hold")
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
async def list_keys(ctx):
    """List common available keys."""
    common_keys = f"The List of available keys can be found here: https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys"
    await ctx.send(common_keys)

# Mouse Commands #
@bot.command(name="mouse")
async def move_mouse(ctx, directions: str, amount: int):
    """Moves the mouse a magical amount of space. Usage: !mouse downleft 10"""
    try:
        increment=30 #How many pixels we move per "amount"
        xOffset=0
        yOffset=0

        if "up" in directions.lower():
            yOffset += (amount * -increment)
        if "down" in directions.lower():
            yOffset += (amount * increment)
        if "right" in directions.lower():
            xOffset += (amount * increment)
        if "left" in directions.lower():
            xOffset += (amount * -increment)
       
        pyautogui.move(xOffset, yOffset, 1)
        await ctx.send("Mouse moved")
    except Exception as e:
        await ctx.send(f"Error moving mouse: {e}")

@bot.command(name="click")
async def click(ctx, btn: str = "left"):
    """Clicks the mouse, optionally can do middle, or right click. Usage: !click middle"""
    try:
        pyautogui.click(button=btn)
        await ctx.send(f"{btn} mouse button clicked")
    except Exception as e:
        await ctx.send(f"Error clicking mouse: {e}")

@bot.command(name="scroll")
async def scroll(ctx, direction: str, amount: int):
    """Scrolls a specified direction. Usage: !scroll up 10"""
    try:
        if direction == "down":
            amount=-amount
        increment=30

        pyautogui.scroll(amount * increment)
        await ctx.send(f"Mouse scrolled")
    except Exception as e:
        await ctx.send(f"Error scrolling mouse: {e}")

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

