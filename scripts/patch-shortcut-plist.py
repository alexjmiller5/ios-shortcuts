#!/usr/bin/env python3
"""Post-compile plist fixes for things Cherri (v2.3) cannot express.

Patch 1 — file-typed form values: a Form-body item whose key is "file" and
whose value is a single-variable text token gets converted to WFItemType 5
(File) with a WFTokenAttachmentParameterState value — the structure Shortcuts
requires to actually attach the file (a text token uploads nothing).
Used by Scan QR-code's multipart upload to api.qrserver.com.
# ponytail: keyed on form key == "file"; generalize to a marker if a second
# file-upload shortcut ever needs a different key name.
"""
import plistlib
import sys

path = sys.argv[1]
with open(path, "rb") as f:
    pl = plistlib.load(f)

changed = False
for action in pl.get("WFWorkflowActions", []):
    if action.get("WFWorkflowActionIdentifier") != "is.workflow.actions.downloadurl":
        continue
    form = action.get("WFWorkflowActionParameters", {}).get("WFFormValues", {})
    for item in form.get("Value", {}).get("WFDictionaryFieldValueItems", []):
        if item.get("WFKey", {}).get("Value", {}).get("string") != "file":
            continue
        token = item.get("WFValue", {}).get("Value", {})
        attachments = token.get("attachmentsByRange", {})
        if len(attachments) != 1 or token.get("string") != "￼":
            continue  # not a single-variable token; leave it alone
        item["WFItemType"] = 5
        item["WFValue"] = {
            "WFSerializationType": "WFTokenAttachmentParameterState",
            "Value": {
                "WFSerializationType": "WFTextTokenAttachment",
                "Value": next(iter(attachments.values())),
            },
        }
        changed = True

if changed:
    with open(path, "wb") as f:
        plistlib.dump(pl, f, fmt=plistlib.FMT_BINARY)
    print(f"🩹 Patched file form value in {path}")
