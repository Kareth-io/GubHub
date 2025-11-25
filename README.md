# GubHub

A silly little tool meant to allow users in a discord server to remotely control a Windows PC running this script


## Documentation

[Command Reference](https://docs.kareth.io/books/gubhub/page/command-reference)


## Configuration

To run this project, you will need to add the following environment variables to your .env file

### Discord
`TOKEN` - Discord Bot Token

`ALLOWED_CHANNEL_ID` - The channel ID in discord the bot reads commands from

`ALLOWED_ROLE_NAME` - The discord role that the bot will respond to


### FireFox
`FIREFOX_PROFILE` - The location on the bots filesystem that contains the intended firefox profile. These can normally be found in `C:\Users\USERNAME\AppData\Roaming\Mozilla\Firefox\Profiles`

### OBS
Used to record and save replay buffers of the users screen. This will require some manual configuration of the bot's local OBS client:

* Setup the OBS Scenes to actually capture what you want
* You will need to enable avdanced options in Settings > Output and then enable the replay buffer
* You will have to enable and configure the OBS websocket server

`OBS_HOST` - The host running OBS. Generally this is localhost.

`OBS_PORT` - The port the OBS websocket server listens on. Default is `4455`

`OBS_PASSWORD` - The password for the OBS websocket server. 

### GoogleDrive (Optional)
If these are enabled this will allow the bot to ship any replays from OBS to a specified google drive. 

Will require Google oauth2 client credentials: https://developers.google.com/identity/protocols/oauth2

`GOOGLE_CRED_FILE` - Aformentioned client credentials in json format on the bots local filesystem. 

`GOOGLE_FOLDER_ID` - The Folder ID in the google drive for the account from the credential file. You can get the folder ID from the URL in google drive.
