# iOS Shortcuts

## About This Repo

- The folder structure of the shortcuts will mirror the structure of the shortcuts app on iOS
- The shortcuts will be written in [Cherri](https://cherrilang.org/)

## Capabilities

- Toolbox pro global variables could be used to store my Spotify and notion api keys and other duplicate global variables. This might be better than storing them in a file or hardcoding them in shortcuts
- Scriptable has the ability to run shortcuts, and can run JS code directly from shortcuts which could be better than doing logic directly in shortcuts

## Compiling shortcuts

- The shortcuts can be compiled to a `.shortcut` file which can be imported into the Shortcuts app on iOS
- Use the `cherri` command line tool to compile the shortcuts:

  ```bash
  cherri <cherri_file_name>
  ```

- If the shortcuts have secrets make sure to put the variables in a `.env.local` file and run `./cherri-compiler-with-secrets.sh <cherri_file_name>` to compile the shortcuts with the secrets included. The `.env.local` file should contain the secrets in the format `VARIABLE_NAME=secret_value`.

## Enhancements

- **Automatically generating shortcuts for notion databases based on their structure:**
  - Could generate cherri code
  - Could write an app which has complex app intents with conditionals based on database structure which can be used as shortcuts

- **Syncing my custom shortcuts via code and the shortcuts app:**
  - Reverse engineer the shortcuts database in Library/Shortcuts to have code go in and automatically update my shortcuts based on the changes I make to my cherri code
  - Write my shortcuts for a custom app as app intents and put them in shortcuts — the shortcuts won’t change but the internal commands from the app intents can change or have conditionals based on information from the app
  - Develop another shortcut which updates the custom shortcuts by clicking it

## TODOs

- [ ] Write all my shortcuts in cherri cause that’ll generally save me time editing them and in making new shortcuts
  - Cherri dev links: <https://github.com/electrikmilk/cherri> <https://cherrilang.org/language/variables-constants-globals.html#globals> <https://cherrilang.org/language/standard/scripting.html#ask-for-input> <https://playground.cherrilang.org/>
- [ ] Write my shortcuts to be able to connect to my personal vm for dataprocessing by access a webhook put out by my vm
- [ ] Add all of my shortcuts to this project -- I have a bunch of shortcuts I added after I added the original cherri files for my shortcuts to this project

## Shortcuts to write / improve / generate

- [ ] People through time database
- [ ] People database
- [ ] Fun things database
- [ ] Bucket list database
- [ ] Fix up yt video database shortcut and make sure it determines all the data by simply just scraping after given the link. Maybe it can send the link to a server which does the actual work then sends a response to the shortcut about how it went
- [ ] Poker game database
- [ ] Movies database -- the info should be populated by apis / ai instead of manually including genres, actors, etc.
- [ ] TV shows database -- the info should be populated by apis / ai instead of
- [ ] Fix my quick note shortcut so that it can handle weird characters like "\" -- rn it "Can't convert from text to dictionary" when I try to use it with a note that has a "\" in it
- [ ] Fix Spotify shortcut when song can’t be recognized— it’s a bit garbage rn and could be way better with weird syntaces and there;s probably a better way to find a song on spotify than the way im currently doing it — some other kinda search api from spotify (Find a better way to look up songs with  the Spotify api using the Shazam data to improve my Shazam shortcut (Spanish song with accent didn’t work — maybe it’s the accent’s fault)) -- the core of this problem isntead of searaching up a song on spotify necessarily could be converting the shazam link to a spotify link -- i could look into what other data the shazam action returns and see if it has a spotify link or something like that
- [ ] add an offline check to all my shortcuts so that if my phone is offline instead of sending the data directly to notion, it saves it somewhere else for it to be uploaded later. the trickiest part of this is makeing sure the data is uploaded in a timely fashion rather than just sitting there. Brainstroming now, I'm thinking the best psosible option would be to have a file with all the offline data for each shortcut. I'll have automations that run every 30 minutes or so to check if the phone is online, and if it is, it will upload the data from the file to notion. If the phone is offline, it will just keep the data in the file until it can be uploaded. I could also run a background task on my mac to check for the file and upload it to notion if the phone is offline or off since the files will be in the shared iCloud drive filesystem. That could be a bad idea though potentially. It seems like each shortcut will need a companion shortcut which checks each time if there was offline data, and if there was, it includes that in the new data being sent if the phone is now online. Also, that companion shortcut will be the one that's run by the automation, not the original shortcut. It will have to data processing logic to get the data from the file. I'm not sure if each shortcut should have its own file or if they should share a file, and i would need some kinda mega shortcut to be associated with the automation to mega upload all the shortcuts' offline data
