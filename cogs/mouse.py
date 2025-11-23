import pyautogui
from discord.ext import commands

class MouseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mouse")
    async def move_mouse(self, ctx, directions: str, amount: int):
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

    @commands.command(name="click")
    async def click(self, ctx, btn: str = "left"):
        """Clicks the mouse, optionally can do middle, or right click. Usage: !click middle"""
        try:
            pyautogui.click(button=btn)
            await ctx.send(f"{btn} mouse button clicked")
        except Exception as e:
            await ctx.send(f"Error clicking mouse: {e}")

    @commands.command(name="scroll")
    async def scroll(self, ctx, direction: str, amount: int):
        """Scrolls a specified direction. Usage: !scroll up 10"""
        try:
            if direction == "down":
                amount=-amount
            increment=30

            pyautogui.scroll(amount * increment)
            await ctx.send(f"Mouse scrolled")
        except Exception as e:
            await ctx.send(f"Error scrolling mouse: {e}")


async def setup(bot):
    await bot.add_cog(MouseCommands(bot))
