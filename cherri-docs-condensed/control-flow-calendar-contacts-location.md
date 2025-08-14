---
title: Control Flow
layout: default
parent: Documentation
nav_order: 6
---

# Control Flow
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## If/Otherwise

Use the following syntax:

```ruby
@intVar = 5
if intVar > 6 {
    
} else {
    
}
```

If statements are not required to contain the else statement but do require the ending curly brace as in other
languages.

The first operand of the if statement must be a variable. The second can optionally be a variable.

### Conditional Operators

- `==` Is
- `!=` Is Not
- `contains` Contains
- `!contains` Does Not Contain
- `beginsWith` Begins With
- `endsWith` Ends With
- `>` Greater Than
- `>=` Greater or Equal
- `<` Less Than
- `<=` Less or Equal

### Has Value/Does Not

For these conditional operators, you can compare the reference, or if checking for no value, prepend with a `!`.

```ruby
@variable: text
/* Has Any Value */
if variable {
    
}
/* Does not have any value */
if !variable {
    
}
```

### Between

This checks if `intVar` is between `5` and `7`.

```ruby
@intVar = 5
if intVar <> 5 7 {
    
}
```

### Multiple Conditions

You can use multiple conditions by separating each condition with the same logical operator:

- `&&` And
- `||` Or

To be clear, this is a limitation of how this has been implemented in Shortcuts; only "Any" (`||`) or "All" (`&&`) are allowed for logical comparison of conditions.

```ruby
@textVar = "test"
@intVar = 1
if textVar == "test" && intVar == 1 {
    // ...
}

if textVar == "test" || intVar == 1 {
    // ...
}
```

## Loops

### Repeat

Use the following syntax:

```ruby
@items: array
repeat i for 6 {
    @items += "Item {i}"
}
```

The number of times to repeat can also be a variable as long as it evaluates to a number value.

### Repeat With Each

Use the following syntax:

```ruby
@items = list("item 1","item 2","item 3")
for item in items {
    alert(item)
}
```

`list` must be an iterable variable.

### Repeat Globals

The `repeat` and `for` statements create variables as the `RepeatIndex` and `RepeatItem` globals need to be numbered after more than one nested repeat.

The globals `RepeatIndex` and `RepeatItem` are still available, but it is recommended to use the variables these statements create.

## Nesting

`if/else`, `repeat`, `for`, and `menu` can all be nested inside each other and vice versa.

## Automatic nothing actions at the end

The `nothing()` actions are automatically added to the ending block of any statement. This ensures the control flow block does not store any output to reduce memory usage.


---
title: Calendar
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 1
---

# Calendar Actions
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Calendars

### Add Calendar

Create a calendar with `name`.

```
addCalendar(text name)
```

---

### Open Event in Calendar

```
showInCalendar(variable event)
```

---

### Edit Event

Edit a detail of an event. Provide an event, a detail to modify, and a new value for that detail.

```
editEvent(variable event, enum detail, text newValue)
```

#### Event Details

- Start Date
- End Date
- Is All Day
- Location
- Duration
- My Status
- Attendees
- URL
- Title
- Notes
- Attachments

_**Note:** Enum values are case-sensitive._

---

### Get Event Detail

Get a detail of an event.

```
getEventDetail(variable event, enum detail)
```

Details

- Start Date
- End Date
- Is All Day
- Calendar
- Location
- Has Alarms
- Duration
- Is Canceled
- My Status
- Organizer
- Organizer Is Me
- Attendees
- Number of Attendees
- URL
- Title
- Notes
- Attachments
- File Size
- File Extension
- Creation Date
- File Path
- Last Modified Date
- Name

_**Note:** Enum values are case-sensitive._

---

### Remove Events

```
removeEvents(variable events, bool ?includeFutureEvents = false)
```

## Reminders

### Open Reminders List

```
openRemindersList(variable list)
```

---

### Remove Reminders

```
removeReminders(variable reminders)
```

## Alarms

### Get Alarms

Returns all of the alarms on the device.

```
getAlarms()
```

---

### Create Alarm

Create an alarm.

```
createAlarm(text name, text time, bool ?allowsSnooze = true, array ?repeatWeekdays)
```

Weekdays for `repeatWeekdays` are case insensitive.

---

### Turn On Alarm

Turn on an alarm.

```
turnOnAlarm(variable alarm)
```

---

### Turn Off Alarm

Turn off an alarm.

```
turnOffAlarm(variable alarm)
```

---

### Toggle Alarm

Toggle an alarm on or off depending on current state.

```
toggleAlarm(variable alarm)
```

---

### Delete Alarm

Delete an alarm

```
deleteAlarm(variable alarm)
```

## Clock

### Create Timer

Start a timer.

```
startTimer(number magnitude, enum ?unit = "min")
```

#### Available units:

- hr
- min
- sec

_**Note:** Enum values are case-sensitive._

## Dates

### Current Date

Create a date value with the current date.

```
currentDate()
```

---

### Specific Date

Create a date value from `date`.

```
date(text date)
```

**Example Usage**

```ruby
date("October 5, 2022")
```

---

### Get Dates

Get dates from value.

```
getDates(variable input)
```

---

### Add to Date

Add to a date by units of time.

```
addSeconds(text date, number magnitude)
addMinutes(text date, number magnitude)
addHours(text date, number magnitude)
addDays(text date, number magnitude)
addWeeks(text date, number magnitude)
addMonths(text date, number magnitude)
addYears(text date, number magnitude)
```

---

### Subtract from Date

Subtract from the date by units of time.

```
subtractSeconds(text date, number magnitude)
subtractMinutes(text date, number magnitude)
subtractHours(text date, number magnitude)
subtractDays(text date, number magnitude)
subtractWeeks(text date, number magnitude)
subtractMonths(text date, number magnitude)
subtractYears(text date, number magnitude)
```

---

### Get Starting Time

Get various starting units of date.

```
getStartMinute(text date)
getStartHour(text date)
getStartWeek(text date)
getStartMonth(text date)
getStartYear(text date)
```

---

### Format Date

```
formatDate(variable date, enum ?dateFormat = "Short")
```

#### Date Formats

- None
- Short
- Medium
- Long
- Relative
- RFC 2822
- ISO 8601
- Custom

_**Note:** Enum values are case-sensitive._

---

### Format Time

```
formatTime(variable time, enum ?timeFormat = "Short")
```

#### Time Formats

- None
- Short
- Medium
- Long
- Relative

_**Note:** Enum values are case-sensitive._

---

### Format Timestamp

```
formatTimestamp(variable date, enum ?dateFormat = "Short", enum ?timeFormat = "Short")
```

---
title: Contacts
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 2
---

# Contacts Actions
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

## Contacts

### Contact Details

- First Name
- Middle Name
- Last Name
- Birthday
- Prefix
- Suffix
- Nickname
- Phonetic First Name
- Phonetic Last Name
- Phonetic Middle Name
- Company
- Job Title
- Department
- File Extension
- Creation Date
- File Path
- Last Modified Date
- Name
- Random

---

### Add New Contact

Create a new contact.

```
newContact(text firstName, text lastName, text phoneNumber, text emailAddress, text company, text notes, boolean ?prompt = false)
```

---

### Edit Contact

Update `detail` of `contact` to `value`.

```
updateContact(variable contact, enum detail, text value)
```

---

### Remove Contact Detail

Remove `detail` from `contact`.

```
removeContactDetail(variable contact, enum detail)
```

---

### Filter Contacts

Filter `contacts` by `property` and sort by `sortOrder`, and limit to `limit` number of contacts.

```
filterContacts(variable contacts, enum ?sortByProperty, enum ?sortOrder = "A to Z", integer ?limit)
```

#### Sort Orders

- A to Z
- Z to A

---

### Get Detail of Contacts

Get `property` from `contact`.

```
getContactDetail(variable contact, enum property)
```

---

### Select Contact

Prompt the user to select a contact(s).

```
selectContact(boolean ?multiple = false)
```

## Phone

### Call

Call a `contact`.

```
call(variable contact)
```

---

### FaceTime Call

Facetime `type` call `contact`.

```
facetimeCall(variable contact, enum ?type = "Video")
```

#### FaceTime call types

- Video
- Audio

---

### Phone Number

Create a phone number value of `number`. No limit on `number` arguments.

```
phoneNumber(text ...number)
```

---

### Select Phone Number

Prompt the user to select a phone number.

```
selectPhoneNumber()
```

## Email

### Email Address

Create an email address value of `email`. No limit on `email` arguments.

```
emailAddress(text ...email)
```

---

### Select Email Address

Prompt the user to select an email address.

```
selectEmailAddress()
```

---
title: Location
layout: default
grand_parent: Documentation
parent: Actions
nav_order: 4
---

# Location Actions
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

### Get Current Location

Get the users current location.

```
 getCurrentLocation()
 ```

---

### Get Location Detail

Get `detail` of `location`.

```
getLocationDetail(variable location, enum detail)
```

#### Location Details

- Name
- URL
- Label
- Phone Number
- Region
- ZIP Code
- State
- City
- Street
- Altitude
- Longitude
- Latitude

## Addresses

### Get Addresses

Get addresses from `input`.

```
getAddresses(variable input)
```

---

### Street Address

Create a location value from a specific street address.

```
streetAddress(text addressLine2, text addressLine2, text city, text state, text country, integer zipCode)
```

## Maps

### Open in Maps

Open `location` in the default maps app.

```
openInMaps(variable location)
```

## Routing

### Get Halfway Point

Get the halfway point between `firstLocation` and `secondLocation`.

```
getHalfwayPoint(variable firstLocation, variable secondLocation)
```

## Weather

### Get Current Weather

Get current weather conditions, optionally at a specific location.

```
getCurrentWeather(variable ?location = "Current Location")
```

---

### Get Weather Forecast

Get the weather forecast of `type`, optionally for a `location`.

```
getWeatherForecast(enum ?type = "Daily", variable ?location = "Current Location")
```

#### Forecast Types

- Daily
- Hourly

---

### Get Weather Detail

Get `detail` of `weather`.

```
getWeatherDetail(variable weather, enum detail)
```

#### Weather details

- Name
- Air Pollutants
- Air Quality Category
- Air Quality Index
- Sunset Time
- Sunrise Time
- UV Index
- Wind Direction
- Wind Speed
- Precipitation Chance
- Precipitation Amount
- Pressure
- Humidity
- Dewpoint
- Visibility
- Condition
- Feels Like
- Low
- High
- Temperature
- Location
- Date