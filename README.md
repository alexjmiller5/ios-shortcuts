# iOS Shortcuts

## About This Repo

- The folder structure of the shortcuts will mirror the structure of the shortcuts app on iOS
- The shortcuts will be written in [Cherri](https://cherrilang.org/)

## Capabilities

- Toolbox pro global variables could be used to store my Spotify and notion api keys and other duplicate global variables. This might be better than storing them in a file or hardcoding them in shortcuts
- Scriptable has the ability to run shortcuts, and can run JS code directly from shortcuts which could be better than doing logic directly in shortcuts

## Compiling Shortcuts

The shortcuts can be compiled to a `.shortcut` file which can be imported into the Shortcuts app on iOS.

**Basic compilation (no secrets):**
```bash
cherri <file.cherri>
```

**Compilation with secrets and constants:**
```bash
./scripts/compile-shortcut.sh <file1.cherri> [file2.cherri] ...
```

**Using just (recommended):**
```bash
just compile <file.cherri>           # Compile specific file(s)
just compile-dir <directory>         # Compile all .cherri files in a directory
just compile-all                     # Compile all shortcuts in the repo
```

### Secrets

Secrets are stored in 1Password and referenced in `.cherri` files using the `<<secret:NAME>>` syntax:

```cherri
@ClientID = "<<secret:SPOTIFY_CLIENT_ID>>"
"Authorization": "Bearer <<secret:NOTION_INTEGRATION_SECRET>>"
```

The compile script expands these to `op://Personal/NAME/credential` and uses the 1Password CLI (`op inject`) to substitute actual values.

### Constants

Non-sensitive constants are stored in `constants.txt` at the repo root in `KEY=value` format:

```
# constants.txt
SYNAPSE_INTAKER_BASE_URL=https://example.com/api
```

Reference them in `.cherri` files using `<<constant:NAME>>`:

```cherri
jsonRequest("<<constant:SYNAPSE_INTAKER_BASE_URL>>?key=<<secret:API_KEY>>", "POST", { ... })
```

## Enhancements

- **Automatically generating shortcuts for notion databases based on their structure:**
  - Could generate cherri code
  - Could write an app which has complex app intents with conditionals based on database structure which can be used as shortcuts

- **Syncing my custom shortcuts via code and the shortcuts app:**
  - Reverse engineer the shortcuts database in Library/Shortcuts to have code go in and automatically update my shortcuts based on the changes I make to my cherri code
  - Write my shortcuts for a custom app as app intents and put them in shortcuts — the shortcuts won't change but the internal commands from the app intents can change or have conditionals based on information from the app
  - Develop another shortcut which updates the custom shortcuts by clicking it
  - The task I wrote could actually be the details / notes I think that'd be better - AI could summarize it into the title

## TODOs

- [ ] Write all my shortcuts in cherri cause that'll generally save me time editing them and in making new shortcuts
  - Cherri dev links: <https://github.com/electrikmilk/cherri> <https://cherrilang.org/language/variables-constants-globals.html#globals> <https://cherrilang.org/language/standard/scripting.html#ask-for-input> <https://playground.cherrilang.org/>
- [ ] Write my shortcuts to be able to connect to my personal vm for dataprocessing by access a webhook put out by my vm
- [ ] Add all of my shortcuts to this project -- I have a bunch of shortcuts I added after I added the original cherri files for my shortcuts to this project
- [ ] Learn how to use non cherri actions in cherri shortcuts so I can improve my code. Add the docs and explanations for these actions into my cherri Gem
- [ ] Create an ios app which is in contact with my shortcuts server. when all the data is sent immediately and processed in my server, instead of getting a confirmation through the shortcut, the app will send a confirmation through an ios application. It looks like it's not that hard to sideload an application with xcode and I could then also more easily implement my offline shortcuts with data stored in the app. I could create my own shortcut app intent action which which is just called save data offline or something like that
- [ ] Make some kind of notion → raycast or shortcut → raycast compiler just like cherri compiles to shortcuts so that I can automatically get all my shortcuts in raycast and have them be auto generated
- [ ] Send notifications instead of shows for shortcuts for more async -- once i send in my data they can complete and ill get a notif later. Even with shazam when the song gets added or not the shortcut can just send me a notif even if it's online. i don't wann have to click done

## Shortcuts to write / improve / generate

- [ ] People through time database
- [ ] People database
- [ ] Fun things database
- [ ] Bucket list database
- [ ] Fix up yt video database shortcut and make sure it determines all the data by simply just scraping after given the link. Maybe it can send the link to a server which does the actual work then sends a response to the shortcut about how it went
- [ ] Poker game database
- [ ] Movies database -- the info should be populated by apis / ai instead of manually including genres, actors, etc.
- [ ] TV shows database -- the info should be populated by apis / ai instead of Find some kind of api to get genres and actresses and actors and more details about my film and tv databases that will interact with my notion api
- [ ] Fix my quick note shortcut so that it can handle weird characters like "\" -- rn it "Can't convert from text to dictionary" when I try to use it with a note that has a "\" in it
- [x] ~~Fix Spotify shortcut when song can't be recognized— it's a bit garbage rn and could be way better with weird syntaces and there;s probably a better way to find a song on spotify than the way im currently doing it — some other kinda search api from spotify (Find a better way to look up songs with  the Spotify api using the Shazam data to improve my Shazam shortcut (Spanish song with accent didn't work — maybe it's the accent's fault)) -- the core of this problem isntead of searaching up a song on spotify necessarily could be converting the shazam link to a spotify link -- i could look into what other data the shazam action returns and see if it has a spotify link or something like that~~
- [ ] add an offline check to all my shortcuts so that if my phone is offline instead of sending the data directly to notion, it saves it somewhere else for it to be uploaded later. the trickiest part of this is makeing sure the data is uploaded in a timely fashion rather than just sitting there. Brainstroming now, I'm thinking the best psosible option would be to have a file with all the offline data for each shortcut. I'll have automations that run every 30 minutes or so to check if the phone is online, and if it is, it will upload the data from the file to notion. If the phone is offline, it will just keep the data in the file until it can be uploaded. I could also run a background task on my mac to check for the file and upload it to notion if the phone is offline or off since the files will be in the shared iCloud drive filesystem. That could be a bad idea though potentially. It seems like each shortcut will need a companion shortcut which checks each time if there was offline data, and if there was, it includes that in the new data being sent if the phone is now online. Also, that companion shortcut will be the one that's run by the automation, not the original shortcut. It will have to data processing logic to get the data from the file. I'm not sure if each shortcut should have its own file or if they should share a file, and i would need some kinda mega shortcut to be associated with the automation to mega upload all the shortcuts' offline data
- [ ] Creating something in my ios app vm uses ai to mark the categories of tasks
- [ ] rewrite quick note shortcut to put multiple lines into multiple blocks instead of multiple lines in one block
- [ ] add tab group in clipboard question to add task shortcut to add that tab group to the task if yes
- [ ] create a system for my ai notion database post requests where if it can't figure them out it somehow marks them to be fixed in my workspace / tasks with a hyperlink to the item that needs to be manually fixed
- [ ] Make for my shortcuts not just type out what i want the text to do but also you can just speak into the phone and itll send the audio to ai to put it in the database
- [ ] Make one shortcut with plain text and select just the database it goes to instead of having a shortcut for each database and it'll use ai to format the proper request and possibly fill in the properties based on the database structure
- [x] ~~adjust my .env.local file to use the 1password cli to get the secrets instead of storing them in a file -- that way the secrets are more secure and not stored in plaintext on my filesystem~~
- [x] ~~Create a constants engine with the compile script which pulls in constants from a constants file and puts them into the cherri files before compiling -- that way i can have global constants for things like urls and non secrets without having to store them in each cherri file. Then I can also write constant:CONSTANT_NAME and secret:SECRET_NAME to differentiate between constants and secrets~~
