import pyautogui, asyncio
from discord.ext import commands

class KeyboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="key")
    async def press_key(self, ctx, key: str):
        """Press a single key on the keyboard. Usage: !key <key>"""
        try:
            pyautogui.press(key)
            await ctx.send(f"Pressed key: `{key}`")
        except Exception as e:
            await ctx.send(f"Error pressing key: {e}")

    @commands.command(name="type")
    async def type_text(self, ctx, *, text: str):
        """Type a string of text. Usage: !type <text>"""
        try:
            pyautogui.typewrite(text, interval=0.05)
            await ctx.send(f"Typed: `{text}`")
        except Exception as e:
            await ctx.send(f"Error typing text: {e}")

    @commands.command(name="hotkey")
    async def press_hotkey(self, ctx, *keys):
        """Press a hotkey combination. Usage: !hotkey ctrl c"""
        try:
            pyautogui.hotkey(*keys)
            await ctx.send(f"Pressed hotkey: `{' + '.join(keys)}`")
        except Exception as e:
            await ctx.send(f"Error pressing hotkey: {e}")

    @commands.command(name="hold")
    async def hold_key(self, ctx, key: str, duration: float = 0.5):
        """Hold a key for a duration. Usage: !hold <key> <seconds>"""
        try:
            pyautogui.keyDown(key)
            await asyncio.sleep(duration)
            pyautogui.keyUp(key)
            await ctx.send(f"Held key `{key}` for {duration} seconds")
        except Exception as e:
            await ctx.send(f"Error holding key: {e}")

    @commands.command(name="keys")
    async def list_keys(self, ctx):
        """List common available keys."""
        common_keys = f"The List of available keys can be found here: https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys"
        await ctx.send(common_keys)


async def setup(bot):
    await bot.add_cog(KeyboardCommands(bot))
