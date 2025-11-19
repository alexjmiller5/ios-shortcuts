---
title: Actions
layout: default
parent: Documentation
has_children: true
nav_order: 2
---

# Actions

Actions in Cherri are intended to be easier to use, as in some cases, single actions have been split up into multiple
actions to reduce the number of arguments and complexity. Some arguments are optional, and some are required.

Actions can be used just like you would call a function in another language

```
alert("Hello!")
```

## Standard Actions

Standard actions are always available and do not need to be imported. Below are categories of standard Shortcut actions currently supported.

[Please report incomplete or non-working actions](https://github.com/electrikmilk/cherri/issues)

## Can I contribute actions, even non-standard actions?

Yes, it's not very hard!

[Learn more about contributing actions](/compiler/actions)

---

title: Custom Actions
layout: default
parent: Documentation
nav_order: 12
---

# Custom Actions

{: .no_toc }

Custom actions are an abstraction on top of Shortcuts that allows you to run Cherri code separately from your main code, even multiple times, recurse within it, and maybe output a value.

You can define custom actions that can be called later in a Shortcut, in the same way as standard actions.

This allows you to not have to repeat yourself and cut down on the total actions in your Shortcut if you have actions doing the same thing in multiple places.

This uses an abstraction that is injected at the top of your Shortcut, [but don't worry, the first comment is preserved](#prioritization-of-instructional-or-contact-comments).

## Table of contents

{: .no_toc .text-delta }

1. TOC
{:toc}

## Definition

### Defining a custom action

Define your action, then reference the action to run the contents of the custom action, isolated from the rest of your Shortcut:

```
action add(number op1, number op2) {
  const result = op1 + op2
  output("{result}")
}

add(2,2)
```

Keep in mind, if a custom action is used, the compiler will inject some actions at the top of your Shortcut to support this feature.

### Defining arguments

You can define arguments for your custom action that you provide later when referencing it.

```
action myAction(text message) {
    // ...
}
```

Read the [types](types) reference for all types you can use for arguments.

When calling your custom action, keep in mind that the arguments you use will be type-checked against your type definitions for each of your arguments.

### Optional

Future release
{: .label .label-purple }

Add a `?` before the argument name to mark it as optional, meaning it is not required to be filled in. Otherwise, the compiler will complain if the argument is not filled in when the custom action is called.

```
action myAction(text ?message) {
    // ...
}
```

### Literal

Future release
{: .label .label-purple }

Add a `!` after the type of the argument name to mark it as requiring a literal value, for parameters that do not accept a variable value.

```
action myAction(text! message) {
    // ...
}
```

### Default Value

Future release
{: .label .label-purple }

You can optionally use an assignment operator to set a default value for the argument. The compiler will warn against using the default value for this argument, as that will make for a smaller shortcut.

```
action myAction(text message = "Hello, World!") {
    // ...
}
```

## Action Behavior

### Returning a Value

This is not required, but if you would like to return a value from your custom action to a call of your custom action, assign the reference to your custom action to a variable just like you would a standard action.

Then, inside the body of your custom action, use the `output()` action to return a result.

```
action myCustomAction() {
  output("Hello!")
}

@result = myCustomAction()
```

### Output Type

You can define an output type for your custom action so that an error can be thrown if the output is used where that type is not expected.

```
action sum(number op1, number op2): number {
    // ...
}
```

### Output Type Coersion

Future release
{: .label .label-purple }

In a future release, type coercion will be done at the action call level, where the output of the action will be put in a type casting action, such as a text or number action, and then assigned to the variable for the return variable but only if there is one.

### Recursion

It is possible to call other custom actions within the body of a custom action. You can then use this for recursion, running the same custom action with an eventual breakpoint.

{: .warning }
Misuse of recursion can cause a Shortcut to infinitely loop.

```ruby
action fibonacci(number n): number {
    if n <= 1 {
        output("{n}")
    } else {
        const minusOne = n - 1
        const minusTwo = n - 2
        const fib1 = fibonacci(minusOne)
        const fib2 = fibonacci(minusTwo)
        const added = fib1 + fib2
        output("{added}")
    }
}

const output = fibonacci(7)
show("{output}") // 13
```

## Prioritization of Instructional or Contact Comments

Note that when the compiler reaches your first explicit comment action, if you are using a custom action, it will push that action to the top of the Shortcut instead of adding it after the injected custom actions abstraction has been added at the top.

This is primarily to still be able to add an instructional or contact comment at the top of a Shortcut while also using the custom actions abstraction.

```ruby
#include 'stdlib'

comment('Contact me: brandon@cherrilang.org')

runJS("console.log('Hello, World!')")
```

## How do they work?

The contents of these actions run separately from your main code inside your Shortcut by using the **Run Shortcut** action and passing a **Dictionary** action containing data that will be detected by the injected Cherri code that contains each of the defined actions that are used in the Cherri code below it.

This is a part of the language that does not translate 1-1, but for the functionality it provides, it can be a powerful tool.

### Action Definition

The semantics of this may change over time, but it roughly translates to this in Cherri:

```ruby
if ShortcutInput {
    const inputType = typeOf(ShortcutInput)
    if inputType == "Dictionary" {
        const input = getDictionary(ShortcutInput)
        const identifier = getValue(input, "cherri_functions")
        const valid = number(identifier)
        if valid == true {
            const function_name = getValue(input, "function")
            const function = "{function_name}"
            const args = getValue(input, "arguments")
            if function == "add" {
                const arg1 = getListItem(args, 0)
                const arg2 = getListItem(args, 1)
                const op1 = number(arg1)
                const op2 = number(arg2)
                const result = op1 + op2
                output("{result}")
            }
            output(nil)
        }
    }
}
```

The compiler will generate this syntax and inject it into the top of the resulting Shortcut.

It validates that the input we're receiving is a Cherri function call, then filters it down to which action is being called, then we have actions based on the action's definition that coerce the provided argument values from the input into their defined value types, then the injected custom action body is run.

At the end, just in case no output was defined in the custom action body that was called, we output nothing at the end of the action call list.

### Action Calls

Then, when you reference the action described `add(number, number)`

```ruby
action add(number op1, number op2) {
  const result = op1 + op2
  output("{result}")
}

add(2,2)
```

It will create tokens in the compiler for a **Dictionary** and a **Run Shortcut** action equivalent to this:

```ruby
const addCherriCall = {
    "cherri_functions": 1,
    "function": "add",
    "arguments": [2, 2]
}

runSelf(addCherriCall)
```

---

title: Raw Action
layout: default
parent: Documentation
nav_order: 13
---

# Raw Action

You can write a raw definition of an action not defined inside Cherri, in Cherri.

## Defining an action

Provide a string of the action `WFWorkflowActionIdentifier`. Then, optionally provide a dictionary for the `WFWorkflowActionParameters`.

```ruby
rawAction("is.workflow.actions.alert", {
     "WFAlertActionMessage": "Hello, world!",
     "WFAlertActionCancelButtonShown": false
})
```

This defines an alert action with the message `Hello World!`. This action is already defined in Cherri using the `alert()` action. Still, this example demonstrates a simple way actions not implemented in Cherri can be used.

However, there is an alternative called [action definitons](/language/define-actions) in a future release, which creates reusable action definitions.

## Variable Values

Future Release
{: .label .label-purple }

To use a variable value for a parameter that only accepts a variable value, prepend an inline variable reference's brackets in a string value with the character `$`.

```
action saveFile(variable file) {
    rawAction("is.workflow.actions.documentpicker.save", {
         "WFInput": "${file}"
     })
}
```

Again, just like with the `alert()` action, there is already a `saveFile()` action; this is only an example.

Only a single variable is allowed; if this is not detected, the compiler treats the value as a string with inline variable references.

---

title: Copy/Paste Actions
layout: default
parent: Documentation
nav_order: 10
---

# Copy/Paste Actions

{: .warning }
Strong caution against the misuse of this syntax, such as long chains of pastables pasting other pastables.

Cherri has a built-in preprocessing mechanism called "pastables" for copy-pasting commonly used sets of actions, including variables and any other valid Cherri code.

## Setup code to copy

Use a `copy` statement to create a "Pasteable":

```
copy identifier {
    alert("Hello!")
}
```

## Paste

Use a `paste` statement to paste the contents of the pasteable on that line before the file is parsed.

{: .note }
For efficiency, you cannot use `paste` before declaring the `copy` it's using.

```ruby
copy carbon {
    alert("Hello!")
}

paste carbon

alert("Goodbye")

paste carbon
```

In the example above, the resulting Shortcut will have an `alert("Hello")` pasted wherever `paste carbon` is used.

## Difference from custom actions and includes

These work differently from [custom actions](/language/custom-actions) in that they reduce the number of actions as custom actions add a lot of actions. If you don't _need_ to use the abstraction of custom actions (you don't need to use arguments) to reuse the same actions if it's not necessary for what you need to reuse.

However, depending on how much code is in the pastable and how many times you need to paste it, it may produce fewer actions to use custom actions instead.

This also allows you to "include" code without needing a separate file. You could include a file with a bunch of pastables to selectively include code from that file.
