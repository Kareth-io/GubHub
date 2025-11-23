import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from typing import Optional
import io
import os

class FirefoxController(commands.Cog):
    """Control Firefox browser through Discord commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.driver: Optional[webdriver.Firefox] = None
        self.browser_lock = asyncio.Lock()
        self.bookmarks = {}  # Dictionary to store bookmarks {name: url}
    
    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.driver:
            self.driver.quit()
    
    @commands.command(name="ffstart")
    async def start_browser(self, ctx):
        """Start the Firefox browser
        
        Usage: !start 
        """
        profile_name=os.getenv("FIREFOX_PROFILE")
        user=os.environ.get("USERNAME")
        profile=f"C:/Users/{user}/AppData/Roaming/Mozilla/Firefox/Profiles/{profile_name}"
        print(f"FireFox Profile: {profile}")
        addons = [a for a in os.listdir(f"{profile}/extensions") if a.endswith("xpi")]
        async with self.browser_lock:
            if self.driver:
                await ctx.send("Firefox is already running!")
                return
            
            async with ctx.typing():
                try:
                    options = Options()
                    options.add_argument("-profile")
                    options.add_argument(profile)
                    self.driver = webdriver.Firefox(options=options)
                    #for addon in addons:
                    #    print("Installing Firefox Addon: {addon}")
                    #    driver.install_addon(f"{profile}/extensions/{addon}", temporary=True)
                    await ctx.send(f"Firefox started")
                except Exception as e:
                    await ctx.send(f"Error starting Firefox: {str(e)}")
    
    @commands.command(name="ffstop")
    async def stop_browser(self, ctx):
        """Stop the Firefox browser"""
        async with self.browser_lock:
            if not self.driver:
                await ctx.send("Firefox is not running!")
                return
            
            try:
                self.driver.quit()
                self.driver = None
                await ctx.send("Firefox stopped!")
            except Exception as e:
                await ctx.send(f"Error stopping Firefox: {str(e)}")
    
    @commands.command(name="goto", aliases=["url"])
    async def goto_url(self, ctx, url: str):
        """Navigate to a specific URL
        
        Usage: !goto <url>
        """
        if not self.driver:
            await ctx.send("Firefox is not running! Use `!start` first.")
            return
        
        async with ctx.typing():
            try:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                await asyncio.to_thread(self.driver.get, url)
                title = await asyncio.to_thread(lambda: self.driver.title)
                await ctx.send(f"Navigated to: {url}\nPage title: {title}")
            except Exception as e:
                await ctx.send(f"Error navigating: {str(e)}")
    
    @commands.command(name="youtube", aliases=["yt"])
    async def search_youtube(self, ctx, *, query: str):
        """Search for a video on YouTube and open the first result
        
        Usage: !youtube <search query>
        """
        if not self.driver:
            await ctx.send("Firefox is not running! Use `!start` first.")
            return
        
        async with ctx.typing():
            try:
                # Navigate to YouTube search
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                await asyncio.to_thread(self.driver.get, search_url)
                
                # Wait a moment for the page to load
                await asyncio.sleep(2)
                
                # Find and click the first video result
                first_video = await asyncio.to_thread(
                    self.driver.find_element, 
                    By.CSS_SELECTOR, 
                    "a#video-title"
                )
                
                video_title = await asyncio.to_thread(lambda: first_video.get_attribute("title"))
                video_url = await asyncio.to_thread(lambda: first_video.get_attribute("href"))
                
                # Click the video
                await asyncio.to_thread(first_video.click)
                
                await ctx.send(f"Playing: **{video_title}**\n{video_url}")
            except Exception as e:
                await ctx.send(f"Error searching YouTube: {str(e)}")
    
    @commands.command(name="ffrefresh")
    async def refresh(self, ctx):
        """Refresh the current page"""
        if not self.driver:
            await ctx.send("Firefox is not running!")
            return
        
        try:
            await asyncio.to_thread(self.driver.refresh)
            await ctx.send("Page refreshed")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    
    @commands.command(name="ffinfo")
    async def get_info(self, ctx):
        """Get information about the current page"""
        if not self.driver:
            await ctx.send("Firefox is not running!")
            return
        
        async with ctx.typing():
            try:
                url = await asyncio.to_thread(lambda: self.driver.current_url)
                title = await asyncio.to_thread(lambda: self.driver.title)
                
                embed = discord.Embed(
                    title="Page Info", 
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                
                # Add URL field with clickable link
                embed.add_field(name="🔗 URL", value=f"[{url}]({url})" if len(url) <= 200 else url, inline=False)
                
                # Add title field
                embed.add_field(name="📄 Page Title", value=title if title else "No title", inline=False)
                
                # Add footer
                embed.set_footer(text="GubHub", icon_url="https://www.mozilla.org/media/protocol/img/logos/firefox/browser/logo.eb1324e44442.svg")
                
                await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(f"Error getting info: {str(e)}")
    
    @commands.command(name="execute")
    async def execute_js(self, ctx, *, code: str):
        """Execute JavaScript code on the current page
        
        Usage: !execute <javascript code>
        """
        if not self.driver:
            await ctx.send("Firefox is not running!")
            return
        
        async with ctx.typing():
            try:
                result = await asyncio.to_thread(self.driver.execute_script, code)
                result_str = str(result) if result is not None else "No return value"
                
                if len(result_str) > 1900:
                    result_str = result_str[:1900] + "..."
                
                await ctx.send(f"JavaScript executed!\n```\n{result_str}\n```")
            except Exception as e:
                await ctx.send(f"Error executing JavaScript: {str(e)}")
    
    @commands.command(name="bookmark", aliases=["addbookmark"])
    async def add_bookmark(self, ctx, name: str, url: str = None):
        """Add a bookmark for the current page or specified URL
        
        Usage: !bookmark <name> [url]
        If no URL is provided, bookmarks the current page
        """
        if url is None:
            if not self.driver:
                await ctx.send("Firefox is not running! Provide a URL or start Firefox first.")
                return
            
            try:
                url = await asyncio.to_thread(lambda: self.driver.current_url)
            except Exception as e:
                await ctx.send(f"Error getting current URL: {str(e)}")
                return
        else:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
        
        self.bookmarks[name.lower()] = url
        await ctx.send(f"Bookmark added: **{name}** → {url}")
    
    @commands.command(name="unbookmark", aliases=["removebookmark", "delbookmark", "deletebookmark"])
    async def remove_bookmark(self, ctx, name: str):
        """Remove a bookmark
        
        Usage: !unbookmark <name>
        """
        name_lower = name.lower()
        if name_lower in self.bookmarks:
            url = self.bookmarks.pop(name_lower)
            await ctx.send(f"Bookmark removed: **{name}** ({url})")
        else:
            await ctx.send(f"Bookmark not found: **{name}**")
    
    @commands.command(name="bookmarks")
    async def list_bookmarks(self, ctx):
        """List all saved bookmarks"""
        if not self.bookmarks:
            await ctx.send("No bookmarks saved yet!")
            return
        
        embed = discord.Embed(title="Saved Bookmarks", color=discord.Color.blue())
        for name, url in self.bookmarks.items():
            # Truncate long URLs for display
            display_url = url if len(url) <= 50 else url[:47] + "..."
            embed.add_field(name=name.title(), value=display_url, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="gobookmark", aliases=["openbookmark"])
    async def go_to_bookmark(self, ctx, name: str):
        """Navigate to a saved bookmark
        
        Usage: !gobookmark <name>
        """
        if not self.driver:
            await ctx.send("Firefox is not running! Use `!start` first.")
            return
        
        name_lower = name.lower()
        if name_lower not in self.bookmarks:
            await ctx.send(f"Bookmark not found: **{name}**\nUse `!bookmarks` to see available bookmarks.")
            return
        
        url = self.bookmarks[name_lower]
        async with ctx.typing():
            try:
                await asyncio.to_thread(self.driver.get, url)
                title = await asyncio.to_thread(lambda: self.driver.title)
                await ctx.send(f"Opened bookmark: **{name}**\nPage title: {title}")
            except Exception as e:
                await ctx.send(f"Error navigating to bookmark: {str(e)}")

async def setup(bot):
    await bot.add_cog(FirefoxController(bot))
