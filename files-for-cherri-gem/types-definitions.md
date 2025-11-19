---
title: Types
layout: default
parent: Documentation
nav_order: 5
---

# Types
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Value Types

### Text

```ruby
@variable = "text"
@text = "text {variable} \n"
```

Text literals support the interpolation of variables and escape characters.

**Standard escaped characters interpolated:**

- `\"` double quote
- `\n` new line
- `\t` tab
- `\\` backslash

For example:

```ruby
@multi = "multi\nline\ntext"
```

Multiline text is also supported, however:

```ruby
@multi = "multi
line
text"
```

### Raw Text

```ruby
@raw = 'i\'m text'
```

Raw text cancels out interpolation, except for escaped single quotes. As a result, they compile much faster than standard text literals.

One caveat to raw text is that it is not allowed in Dictionaries or Arrays. This is because a dictionary or array must be a valid JSON object.

### Number

```ruby
@number = 42
```

### Float

```ruby
@float = 0.5
```

### Expression

Expressions are numeric values or variable references that are separated by any of the following operators:

- `+` Add
- `-` Subtract
- `*` Multiply
- `/` Divide

```ruby
@expression = 54 + (6 * 7)
@number = 42
@number = 54 * number + (6 * 7)
@expression = number + number
```

Only two operands will compile to a **Math** action:

```ruby
@expression = 54 + 6
```

### Boolean

Booleans translate to a number value of `1` for `true` and `0` for `false`.

```ruby
@boolVarTrue = true
@boolVarFalse = false
```

Boolean variables can be used in conditionals.

```ruby
@boolVarTrue = true
if boolVarTrue == true {
    /* ... */
}
```

### Dictionary

You can declare a dictionary using valid JSON syntax.

```ruby
/* Empty dictionaries */
@x: dictionary
@y = {}

@text = "text"
@dictionary = {
    "key1": "value {text}",
    "key2": 5,
    "key3": true,
    "key4": [
        "item1",
        "item 2",
        "item3"
    ]
}
```

You can access a dictionary value by key:

```ruby
@dictionary = {}

// allows for variable references
getValue(dictionary, "key")

// must be a raw string, so no variable references are allowed.
@value = dictionary['key']
```

### Array

An array is a variable that has been or will be populated with multiple iterable values.

The contents of an array value must be valid JSON syntax.

```ruby
/* Empty arrays */
@x: array
@y = []

@int = 42
@array = [5, "test", {"test":5}, "{int}"]

/* Add a value to the array variable */
@array += "another test"
```

You can use the [`for`](control-flow#repeat-with-each) statement to iterate over the values contained in the array variable.

```ruby
@items = ["Item 1","Item 2"]
for item in items {
    /* ... */
}
```

You can easily append to an array using the `+=` syntax.

```ruby
@x: array
@x += 5
```

This adds the output of the **Number** action with a value of 5 to the array variable `x`.

So `x` now contains 1 item with a number value of `5`.

Items in an array or added to an array cannot be removed. If you need a new array of items, iterate the array using `for`  and add only specific items using a conditional to a new array.

### Variable

A variable is a type of value that can be accepted for a custom action or defined action argument. For custom actions, this means not coercing the value to any type. For defined actions, it means the value should always be handled as a variable when compiling the value for actions that have a parameter that does not accept only a variable value.

### Action Result

Actions have output types. View the [actions](/language/actions) documentation to check the output type of an action, or use the `--action=` argument in the CLI.

```ruby
@urls = url("https://apple.com","https://google.com")
@list = list("Item 1","Item 2","Item 3")
@email = emailAddress("test@test.org")
@phone = phoneNumber("(555) 555-5555")
@date = date("October 5, 2022")
@location = getCurrentLocation()
```

### Enumerations

Some actions have arguments with the type `enum`, accompanied by a set of allowed values. This type only accepts specific string values.

Future release
{: .label .label-purple }

In the next release, enumerations have been implemented as proper types with values defined in code, so enumerations can have identifiers and be defined easily in code for standard actions and user-defined actions.  

To define enumerations for use as a type for [custom actions](/language/custom-actions) and [action definitions](/language/define-actions), use the following syntax:

```
enum Color {
    'Red',
    'Green',
    'Blue'
}

#define action 'com.example.app.action' myCustomAction(Color color)

myCustomAction("Purple") // throws an error
```

It accepts raw string comma-separated values.

Various formats are accepted:

```
enum Colors
{
    'Red',
    'Green',
    'Blue'
}

enum Colors {
    'Red', 'Green', 'Blue'
}

enum Colors {'Red','Green','Blue'}
```

### Empty

You can declare a variable with no value

```ruby
@empty
```

Or more explicitly, set the value as `nil`

```ruby
@empty = nil
```

You can use `nil` just about anywhere to cancel out an optional value.

However, if, due to the value being optional, it has a default, it will be set to its default, not empty.

```ruby
@var = getFile(nil)

if var == nil {

}

repeat i for nil {

}

for item in nil {

}
```

`nil` can skip an argument that is optional to set an argument after it.

```
@media = nil
setMetadata(media, nil, "Title")
```

`nil` is also faster to compile than empty text `""`, array, etc.

## Type Declaration

You can declare a variable with a type but no initial value.

This is particularly useful for creating a variable and then appending to it, then using it with an action that expects that type of value.

Setting a variable's value type explicitly also compiles faster than having to infer the types from empty values like `""`, `[]`, or `{}`.

```ruby
@t: text
@num: number
@list: array
@obj: dictionary
@boolean: bool
@reference: var
@real: float

@builder: text
for item in list {
    @builder += "{item}"
}

/* This would have thrown an error if `@builder` was not of type text. */
show(builder)
```

The following types may be used:

- `text` (default: `""`)
- `number` (default: `0`)
- `bool` (default: `false`)
- `dictionary` (default: `{}`)
- `array` (default: `[]`)
- `var` (variable reference)
- `float` (future release)

## Type Coercion

You can do the following type coercions. See [value types](types#value-types) and [content item types](#content-item-types) for available value types you can coerce to.

### Text

```ruby
@var = 5
@textVar = var.text
```

To coerce another value to text, simply reference it as an inline variable just as you would in Shortcuts.

```ruby
@var = 5
@textVar = "{var}"
```

Or you can use...

```ruby
@var = 5
@textVar = getText(var)
```

### Number

```ruby
@var = "5"
@textVar = var.number
@inlineVar = "{var.number}"
```

```ruby
@textVar = "5"
@numVar = getNumbers(textVar)
```

The `number()` action should only coerce another value to a number, as an integer produces the same output.

```ruby
@textVar = "5"
@numVar = number(textVar)
```

### Dictionary

```ruby
@var
@textVar = getDictionary(var)
```

## Content Item Types

There is a concept of data types in Shortcuts known as a "content item".

These are defined in Shortcuts, for example `WFAppStoreAppContentItem`.

In Cherri, they are shortened into singular names.

These types can be used for coercion, input, and output types.

| Type 	| Content Item Type 	|
|:-------------|:------------------|
| app 	| WFAppStoreAppContentItem 	|
| article 	| WFArticleContentItem 	|
| contact 	| WFContactContentItem 	|
| date 	| WFDateContentItem 	|
| email 	| WFEmailAddressContentItem 	|
| folder 	| WFFolderContentItem 	|
| file 	| WFGenericFileContentItem 	|
| image 	| WFImageContentItem 	|
| itunes 	| WFiTunesProductContentItem 	|
| location 	| WFLocationContentItem 	|
| maplink 	| WFDCMapsLinkContentItem 	|
| media 	| WFAVAssetContentItem 	|
| pdf 	| WFPDFContentItem 	|
| phonenumber 	| WFPhoneNumberContentItem 	|
| richtext 	| WFRichTextContentItem 	|
| webpage 	| WFSafariWebPageContentItem 	|
| text 	| WFStringContentItem 	|

---
title: Definitions
layout: default
parent: Documentation
nav_order: 2
---

# Definitions
{: .no_toc }

Define aspects of your Shortcut, such as the color and glyph of the icon, and how it responds
to no input, what types it accepts as input and outputs, etc.

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Icon

Define the look of your Shortcut using one of the supported colors and glyphs.

### Color

```javascript
#define color red
```

- <span class="color" style="background-color: #ef6065"></span> `red`
- <span class="color" style="background-color: #fd7f60"></span> `darkorange`
- <span class="color" style="background-color: #f39e44"></span> `orange`
- <span class="color" style="background-color: #e7c21c"></span> `yellow`
- <span class="color" style="background-color: #3ac054"></span> `green`
- <span class="color" style="background-color: #00C8A8"></span> `teal`
- <span class="color" style="background-color: #00c2d6"></span> `lightblue`
- <span class="color" style="background-color: #00abef"></span> `blue`
- <span class="color" style="background-color: #3e5db8"></span> `darkblue`
- <span class="color" style="background-color: #7f51b5"></span> `violet`
- <span class="color" style="background-color: #ac6bd7"></span> `purple`
- <span class="color" style="background-color: #e978c6"></span> `pink`
- <span class="color" style="background-color: #9b8e89"></span> `taupe`
- <span class="color" style="background-color: #929e93"></span> `gray`
- <span class="color" style="background-color: #85909a"></span> `darkgray`

### Glyph

```javascript
#define glyph apple
```

You can find all of the identifiers for each Shortcut glyph at [glyphs.cherrilang.org](https://glyphs.cherrilang.org/).

## Input & Output Types

You define input and output types for your Shortcut with [content item types](/language/types.html#content-item-types).

Inputs will default to all types. Outputs will default to no types. This is done to be consistent with the Shortcuts
file format.

```ruby
#define inputs image, text
#define outputs app, file

alert(ShortcutInput)
```

Commas must separate these values.

## No Input

This defines how your Shortcut responds to no input.

### Stop and Respond

```ruby
#define noinput stopwith "Response"

alert(ShortcutInput)
```

### Get Clipboard Contents

```ruby
#define noinput getclipboard

alert(ShortcutInput)
```

### Ask for a [content item type](/language/types.html#content-item-types)

```ruby
#define noinput askfor text

alert(ShortcutInput)
```

## From (Workflows)

This defines where your Shortcut appears.

```ruby
#define from menubar, sleepmode, onscreen

alert(ShortcutInput)
```

Commas must separate these values.

### Workflows

- `menubar` - Menubar
- `quickactions` - Quick Actions
- `sharesheet` - Share Sheet
- `notifications` - Notifications Center Widget
- `sleepmode` - Sleep Mode
- `watch` - Show on Apple Watch
- `onscreen` - Receive On-Screen Content

## Quick Action Types

To define quick action types, first add `quickactions` to a [`from`](#from-workflows) definition (See above).

Then this defines which quick actions your Shortcut should be available in. Click on the info circle to view the result.

```ruby
#define from quickactions
#define quickactions finder, services
```

Commas must separate these values.

### Quick Actions

- `finder` - Defines it as a Quick Action in Finder.
- `services` - Defines it as an item in the Services menu.

## macOS only or non-macOS

Define the `mac` definition with a value of `true` if your Shortcut is mainly meant to be a Mac shortcut, or false if it's primarily meant to be used on iOS.

This will make it so an error is thrown if you use an action that is not supported on macOS or vice versa for non-macOS platforms.

```
#define mac true
```

## Name

This will be used as the name of the resulting Shortcut file. 

```
#define name My Shortcut
```

Cherri will ignore the file's name and use the definition instead to create `My Shortcut.` shortcut.

## Version

Defines the minimum version of iOS your Shortcut supports. Warnings will be printed if you use actions that are not supported in the targeted version.

```
#define version 18.4
```
