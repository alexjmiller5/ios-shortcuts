---
title: Built-in
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 9
---

# Built-in Actions
{: .no_toc }

Built-ins in Cherri are actions in the compiler that use standard actions but implement them in a way that makes it easier to use a specific Shortcuts feature.

For example, the [makeVCard()](/language/vcards) action is, in actuality, just a text action, but the compiler uses it to insert the vCard format into a text action based on your input.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Contains Text

Checks if `text` occurs in `subject`.

```
containsText(text subject, text text, bool ?caseSensitive = true)
```

This uses a [Match Text](/language/standard/documents#match-text) action to check if `text` is within `subject`.

---

## Base64 Encode File

```
base64File(text filePath)
```

This built-in action will load the file at `filePath` and encode it to base 64 at compile time. This will result in a **Text** action containing the base 64 encoded contents of the file which Shortcuts can decode for showing an image, playing audio, etc.

For example, you could enter a file path for an audio file and use **Play Audio** to play the audio when the Shortcut runs.

Keep in mind you will likely need to decode the contents to use them.

```
const audioFile = base64File("music/playme.mp3")
const audio = base64Decode(audioFile)
playSound(audio)
```

---

## Open SpringBoard

Go to the home screen.

```
springBoard()
```

This uses the [Open App](/language/standard/scripting#open-app) action to open the SpringBoard or Homescreen.

---

## [Make vCard](/language/vcards)

Create vCards without having to remember the format. Embed local images as an image for a menu item.

---

## [Raw Action](/language/raw-actions)

Create actions by inputting full identifiers and parameters to use actions not supported by Cherri.

---
title: Built-in
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 9
---

# Built-in Actions
{: .no_toc }

Built-ins in Cherri are actions in the compiler that use standard actions but implement them in a way that makes it easier to use a specific Shortcuts feature.

For example, the [makeVCard()](/language/vcards) action is, in actuality, just a text action, but the compiler uses it to insert the vCard format into a text action based on your input.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Contains Text

Checks if `text` occurs in `subject`.

```
containsText(text subject, text text, bool ?caseSensitive = true)
```

This uses a [Match Text](/language/standard/documents#match-text) action to check if `text` is within `subject`.

---

## Base64 Encode File

```
base64File(text filePath)
```

This built-in action will load the file at `filePath` and encode it to base 64 at compile time. This will result in a **Text** action containing the base 64 encoded contents of the file which Shortcuts can decode for showing an image, playing audio, etc.

For example, you could enter a file path for an audio file and use **Play Audio** to play the audio when the Shortcut runs.

Keep in mind you will likely need to decode the contents to use them.

```
const audioFile = base64File("music/playme.mp3")
const audio = base64Decode(audioFile)
playSound(audio)
```

---

## Open SpringBoard

Go to the home screen.

```
springBoard()
```

This uses the [Open App](/language/standard/scripting#open-app) action to open the SpringBoard or Homescreen.

---

## [Make vCard](/language/vcards)

Create vCards without having to remember the format. Embed local images as an image for a menu item.

---

## [Raw Action](/language/raw-actions)

Create actions by inputting full identifiers and parameters to use actions not supported by Cherri.

---
title: Standard Library
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 10
---

# Standard Library of Custom Actions

You can use the Cherri Standard Library of [custom actions](/language/custom-actions) using the following syntax:

```
#include 'stdlib'
```

This will give you access to the following actions. Note that custom actions are only included with your Shortcut if you use them.

## Scripting

### Choose from vCard

Prompt the user to choose from an array of [vCards](/language/vcards) with a prompt. Returns the chosen vCard item.

```
chooseFromVCard(array items, text prompt)
```

**Example Usage**

```ruby
#include 'stdlib'

@items = []
repeat i for 3 {
  @items += makeVCard("Title", "Subtitle")
}

chooseFromVCard(items, "Choose From Items")
```

---

### Run JavaScript

Runs the JavaScript code in `script` and returns the output.

```
runJS(text script)
```

**Basic Usage**

```ruby
#include 'stdlib'

const jsonStr = '{\"name\": \"John\", \"age\": 30\}'

const code = "
    const json = JSON.parse('{jsonStr}')
    document.body.append(document.createTextNode(json.name));
"

const jsResult = runJS(code)

show(jsResult)
```

You can also use [`base64File()`](/language/standard/builtin#base64-encode-file) to encode a large JS file into your Shortcut without needing to paste it.

`index.js`
```
function output(output) {
    const text = document.createElement('div');
    text.innerHTML = output;
    document.body.appendChild(text);
}

output('Hello, World!');
```

`js.cherri`
```
#include 'stdlib'

const jsFile = base64File("path/to/index.js")
const jsCode = base64Decode(jsFile)

@result = runJS(jsCode)

show(result)
```
