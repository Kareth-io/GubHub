import discord
from discord.ext import commands
import obsws_python as obs
import subprocess
import asyncio
import os
import time
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path

class OBSControl(commands.Cog):
    """A Discord cog to control OBS Studio via websocket"""
    
    def __init__(self, bot, obs_host="localhost", obs_port=4455, obs_password="", 
                 google_credentials__file=None, google_token_file="token.pickle" google_folder_id=None):
        self.bot = bot
        self.obs_host = obs_host
        self.obs_port = obs_port
        self.obs_password = obs_password
        self.obs_client = None
        self.obs_process = None
        self.google_folder_id = google_folder_id
        self.google_credentials_file = google_credentials_file
        self.google_token_file = google_token_file
        self.drive_service = None
        
        # Initialize Google Drive service if credentials provided
        if self.google_creds_file:
            self._init_google_drive()
        
    def _init_google_drive(self):
        """Initialize Google Drive API service using user OAuth2"""
        try:
            creds = None
            
            # The token.pickle file stores the user's access and refresh tokens
            if os.path.exists(self.google_token_file):
                with open(self.google_token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("Refreshing Google Drive credentials...")
                    creds.refresh(Request())
                else:
                    print("Starting Google Drive OAuth flow...")
                    print("A browser window will open for you to authorize the application.")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.google_credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.google_token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print("Google Drive credentials saved!")
            
            self.drive_service = build('drive', 'v3', credentials=creds)
            print("Google Drive service initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Google Drive: {e}")
            self.drive_service = None
    
    def _upload_to_drive(self, file_path: str) -> Optional[str]:
        """Upload a file to Google Drive and return the file ID"""
        if not self.drive_service:
            print("Google Drive service not initialized")
            return None
        
        try:
            file_name = os.path.basename(file_path)
            file_metadata = {
                'name': file_name,
            }
            
            # Add to specific folder if folder_id is provided
            if self.google_folder_id:
                file_metadata['parents'] = [self.google_folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            print(f"File uploaded successfully: {file.get('webViewLink')}")
            return file.get('id')
            
        except Exception as e:
            print(f"Failed to upload to Google Drive: {e}")
            return None

    def _get_latest_replay_file(self):
        """Get the most recently created replay file from OBS output directory"""
        try:
            # Get the replay buffer file path from OBS
            output_settings = self.obs_client.get_record_directory()
            output_dir = output_settings.record_directory
            
            # Look for video files in the output directory
            video_extensions = ['.mp4', '.mkv', '.flv', '.mov']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(Path(output_dir).glob(f'*{ext}'))
            
            if not video_files:
                return None
            
            # Get the most recently modified file
            latest_file = max(video_files, key=lambda x: x.stat().st_mtime)
            
            # Wait a moment to ensure file is fully written
            time.sleep(1)
            
            return str(latest_file)
            
        except Exception as e:
            print(f"Error finding replay file: {e}")
            return None
        
    def connect_obs(self):
        """Connect to OBS websocket - should be run in executor"""
        try:
            self.obs_client = obs.ReqClient(
                host=self.obs_host,
                port=self.obs_port,
                password=self.obs_password,
                timeout=5
            )
            return True
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            return False
    
    async def async_connect_obs(self):
        """Async wrapper for connecting to OBS"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.connect_obs)
    
    def disconnect_obs(self):
        """Disconnect from OBS websocket"""
        if self.obs_client:
            try:
                self.obs_client.base_client.ws.close()
            except:
                pass
            self.obs_client = None
    
    @commands.command(name="obs_start")
    async def start_obs(self, ctx):
        """Start OBS Studio application"""
        
        try:
            # Common OBS installation paths on Windows
            obs_paths = [
                r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe"
            ]
            obs_exe = None
            for path in obs_paths:
                import os
                if os.path.exists(path):
                    obs_exe = path
                    break
            
            if obs_exe:
                self.obs_process = subprocess.Popen([obs_exe, "--minimize-to-tray"], cwd=os.path.dirname(obs_exe))
            else:
                await ctx.send("ERROR: OBS executable not found in common installation paths.")
                return
                    
            
            # Wait for OBS to start
            await asyncio.sleep(3)
            
            # Try to connect (async)
            if await self.async_connect_obs():
                await ctx.send("OBS started and connected successfully!")
            else:
                await ctx.send("OBS started but couldn't connect. Make sure obs-websocket is enabled.")
                
        except Exception as e:
            await ctx.send(f"ERROR: Failed to start OBS: {str(e)}")
    
    @commands.command(name="obs_configure_replay")
    async def configure_replay(self, ctx, duration: int):
        """Configure replay buffer duration"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS. Please start OBS first.")
                return
        
        try:
            # Run blocking OBS call in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.obs_client.set_profile_parameter(
                    "AdvOut",
                    "RecRBTime",
                    str(duration)
                )
            )
            
            await ctx.send(f"Replay buffer duration set to {duration} seconds!")
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to configure replay buffer: {str(e)}")
    
    @commands.command(name="obs_start_replay")
    async def start_replay(self, ctx):
        """Start the replay buffer"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS. Please start OBS first.")
                return
        
        try:
            # Run blocking OBS call in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.obs_client.start_replay_buffer)
            
            await ctx.send("Replay buffer started!")
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to start replay buffer: {str(e)}")
    
    @commands.command(name="obs_save_replay", aliases=["clip"])
    async def save_replay(self, ctx):
        """Save the current replay buffer, upload to Google Drive, and delete locally"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS. Please start OBS first.")
                return
        
        try:
            # Save the replay buffer (run in executor)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.obs_client.save_replay_buffer)
            
            # Give OBS time to save the file
            await asyncio.sleep(2)
            
            # Find the saved replay file (run in executor)
            replay_file = await loop.run_in_executor(None, self._get_latest_replay_file)
            
            if not replay_file:
                await ctx.send("Replay buffer saved, but couldn't find the file for upload.")
                return
            
            file_name = os.path.basename(replay_file)
            file_size_mb = os.path.getsize(replay_file) / (1024 * 1024)
            
            # Upload to Google Drive if configured
            if self.drive_service:
                upload_msg = await ctx.send(f"Uploading `{file_name}` ({file_size_mb:.2f} MB) to Google Drive...")
                
                # Run upload in executor to avoid blocking
                file_id = await loop.run_in_executor(None, self._upload_to_drive, replay_file)
                
                if file_id:
                    # Delete the local file after successful upload
                    try:
                        os.remove(replay_file)
                        await upload_msg.edit(content=f"Replay saved and uploaded to Google Drive!\nLocal file deleted: `{file_name}`")
                    except Exception as e:
                        await upload_msg.edit(content=f"Replay uploaded to Google Drive!\nFailed to delete local file: {str(e)}")
                else:
                    await upload_msg.edit(content=f"Replay saved locally as `{file_name}`\nFailed to upload to Google Drive")
            else:
                await ctx.send(f"Replay buffer saved as `{file_name}`!\nGoogle Drive upload not configured.")
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to save replay buffer: {str(e)}")
    
    @commands.command(name="obs_stop_replay")
    async def stop_replay(self, ctx):
        """Stop the replay buffer"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS. Please start OBS first.")
                return
        
        try:
            # Run blocking OBS call in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.obs_client.stop_replay_buffer)
            
            await ctx.send("Replay buffer stopped!")
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to stop replay buffer: {str(e)}")
    
    @commands.command(name="obs_stop")
    async def stop_obs(self, ctx):
        """Stop OBS Studio application"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS.")
                return
        
        try:
            # Stop OBS via websocket (run in executor)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.obs_client.base_client.ws.send('{"requestType": "Quit", "requestId": "stop_obs"}')
            )
            
            self.disconnect_obs()
            
            if self.obs_process:
                self.obs_process.terminate()
                self.obs_process = None
            
            await ctx.send("OBS stopped successfully!")
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to stop OBS: {str(e)}")
    
    @commands.command(name="obs_status")
    async def status(self, ctx):
        """Check OBS connection status"""
        
        if not self.obs_client:
            if not await self.async_connect_obs():
                await ctx.send("ERROR: Not connected to OBS.")
                return
        
        try:
            # Run blocking OBS calls in executor
            loop = asyncio.get_event_loop()
            version = await loop.run_in_executor(None, self.obs_client.get_version)
            stats = await loop.run_in_executor(None, self.obs_client.get_stats)
            
            embed = discord.Embed(title="OBS Status", color=discord.Color.green())
            embed.add_field(name="OBS Version", value=version.obs_version, inline=True)
            embed.add_field(name="WebSocket Version", value=version.obs_web_socket_version, inline=True)
            embed.add_field(name="FPS", value=f"{stats.active_fps:.2f}", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"ERROR: Failed to get OBS status: {str(e)}")

# Setup function to add the cog to the bot
async def setup(bot):
    # Configure these parameters based on your OBS websocket settings
    await bot.add_cog(OBSControl(
        bot,
        obs_host=os.getenv("OBS_HOST", "localhost"),
        obs_port=int(os.getenv("OBS_PORT", 4455)),
        obs_password=os.getenv("OBS_PASSWORD"),  # Set your OBS websocket password here
        google_credentials_file=os.getenv("GOOGLE_CRED_FILE"),# Path to Google service account JSON
        google_token_file="token.pickle"
        google_folder_id=os.getenv("GOOGLE_FOLDER_ID")  # Optional: specific Google Drive folder ID to upload to
    ))
