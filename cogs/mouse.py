import pyautogui, os, aiohttp
from discord.ext import commands
from pathlib import Path

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

    @commands.command(name="locate")
    async def locate_image(self, ctx):
        """
        Usage: !locate (attach an image to the message)
        The bot will download the image, search for it on your screen, and move the mouse to it.
        """
        
        # Check if message has attachments
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to your message!")
            return
        
        attachment = ctx.message.attachments[0]
        
        # Check if attachment is an image
        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            await ctx.send("Please attach a valid image file (PNG, JPG, JPEG, GIF, or BMP)")
            return
        
        await ctx.send("Downloading image and searching screen...")
        
        # Download the image
        image_path = self.bot.image_dir / attachment.filename
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(image_path, 'wb') as f:
                            f.write(await resp.read())
                    else:
                        await ctx.send("ERROR: Failed to download image")
                        return
            
            # Try to locate the image on screen
            location = pyautogui.locateOnScreen(str(image_path), confidence=0.5)
            
            if location is not None:
                # Get center point of the found image
                center_x, center_y = pyautogui.center(location)
                
                # Move mouse to the location
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                
                await ctx.send(f"Image found at coordinates: ({center_x}, {center_y})\nMouse moved to location.")
            else:
                await ctx.send("ERROR: Image not found on screen. Make sure the image is visible on screen")

        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
        
        finally:
            # Clean up downloaded image
            if image_path.exists():
                os.remove(image_path)

async def setup(bot):
    await bot.add_cog(MouseCommands(bot))
