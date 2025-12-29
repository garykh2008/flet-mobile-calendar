import flet as ft
import inspect
import os
import sys
import typing

# Define classes to inspect
CLASSES_TO_INSPECT = [
    ft.Page,
    ft.Container,
    ft.Column,
    ft.Row,
    ft.ListView,
    ft.Stack,
    ft.Text,
    ft.TextField,
    ft.Checkbox,
    ft.Slider,
    ft.Button, 
    ft.IconButton,
    ft.AlertDialog,
    ft.GestureDetector,
    ft.Clipboard,
    ft.FilePicker,
    ft.Alignment,
]

# Add more if found in module
try: CLASSES_TO_INSPECT.append(ft.ElevatedButton)
except: pass
try: CLASSES_TO_INSPECT.append(ft.OutlinedButton)
except: pass
try: CLASSES_TO_INSPECT.append(ft.TextButton)
except: pass

OUTPUT_FILE = "FLET_API_REF.md"

def get_event_class_info(event_type):
    """Inspects an event class and returns its properties."""
    if not isinstance(event_type, type):
        return None
    
    info = {
        "name": event_type.__name__,
        "properties": []
    }
    
    # Inspect properties (including those from __init__ or slots)
    # 1. Check __annotations__ (best for dataclasses or typed classes)
    if hasattr(event_type, "__annotations__"):
        for name, type_hint in event_type.__annotations__.items():
            if not name.startswith("_"):
                info["properties"].append(f"`{name}`: {type_hint}")
    
    # 2. Check dir() for other properties not in annotations
    for name in dir(event_type):
        if name.startswith("_"): continue
        if name in info["properties"]: continue # Skip if already found
        
        # We only care about properties or data fields, not methods
        try:
            attr = getattr(event_type, name)
            if isinstance(attr, property):
                info["properties"].append(f"`{name}` (property)")
            elif not callable(attr): # It's a data attribute
                info["properties"].append(f"`{name}`") # Just add its name for now
        except: pass
            
    return info

def resolve_type_hint(type_hint):
    """
    Attempts to extract the Event class from a type hint like:
    Union[Callable[[], Any], Callable[[DragUpdateEvent], Any], NoneType]
    """
    # This is a heuristic parser for complex type hints
    s = str(type_hint)
    
    # Look for "flet.controls.events.XxxEvent" or similar
    import re
    # Pattern to find class names ending in Event inside the type string
    # This is rough but works for inspection
    matches = re.findall(r"([a-zA-Z0-9_.]*Event)", s)
    
    unique_events = set()
    for m in matches:
        if "ControlEvent" in m and len(matches) > 1:
            continue # Skip generic ControlEvent if specific one exists
        unique_events.add(m)
        
    return list(unique_events)

def get_class_info(cls):
    info = {
        "name": cls.__name__,
        "module": cls.__module__,
        "init_params": [],
        "public_attributes": [], # New field for all public attributes
        "methods": [],
        "events": [],
        "event_details": {} # Map event_name -> list of event class names
    }
    
    # Cache all attribute names from dir(cls) to avoid re-calculating and for property checks
    all_attrs = dir(cls)

    # 1. Init Params & Events extraction
    init_param_names = set()
    try:
        sig = inspect.signature(cls.__init__)
        for name, param in sig.parameters.items():
            if name == 'self': continue
            
            # Store init param
            info["init_params"].append(f"{name}: {param.annotation} = {param.default}")
            init_param_names.add(name) # Mark as init param
            
            # Identify Events
            if name.startswith("on_"):
                info["events"].append(name)
                # Try to resolve event type
                event_types = resolve_type_hint(param.annotation)
                if event_types:
                    info["event_details"][name] = event_types

    except Exception as e:
        info["init_params"].append(f"(Could not inspect __init__: {e})")

    # 2. Public Attributes (excluding init params, methods, and events already listed)
    for name in all_attrs:
        if name.startswith("_"): continue # Skip private/internal
        if name in init_param_names: continue # Skip if already listed as init param
        if name in info["events"]: continue # Skip if already listed as event handler
        
        try:
            attr = getattr(cls, name)
            if callable(attr): # Skip methods for this list
                if name not in info["methods"]:
                    info["methods"].append(name)
            else:
                # This is a public data attribute or property
                info["public_attributes"].append(name)
        except Exception as e:
            # Handle cases where getattr fails (e.g., dynamic properties)
            info["public_attributes"].append(f"{name} (dynamic/error: {e})")

    # Filter common base methods from info["methods"] later in generate_markdown()
            
    return info

def generate_markdown():
    # Cache for event class details to avoid duplicates
    event_class_cache = {} 

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Flet 1.0 (Beta) API Reference\n\n")
        f.write(f"Generated from local environment: {sys.version}\n")
        f.write(f"Flet Version: {ft.version}\n\n")
        
        # Add common Flet modules for event class lookup
        flet_modules_for_events = [
            ft,
            ft.controls.events,
            ft.controls.page,
            ft.controls.scrollable_control,
            ft.controls.control_event,
            ft.controls.services.file_picker # Corrected path for FilePickerUploadEvent
        ]

        for cls in CLASSES_TO_INSPECT:
            try:
                info = get_class_info(cls)
                f.write(f"## {info['name']}\n")
                f.write(f"**Module:** `{info['module']}`\n\n")
                
                f.write("### Constructor Parameters\n") # Renamed for clarity
                f.write("```python\n")
                f.write(f"{info['name']}(\n")
                for param in info['init_params']:
                    f.write(f"    {param},\n")
                f.write(")\n")
                f.write("```\n\n")

                f.write("### Public Attributes\n") # New section
                if info["public_attributes"]:
                    f.write(", ".join([f"`{a}`" for a in info["public_attributes"]]))
                else:
                    f.write("None")
                f.write("\n\n")
                
                f.write("### Events\n")
                if info["events"]:
                    for e in info["events"]:
                        f.write(f"* `{e}`")
                        if e in info["event_details"]:
                            types = info["event_details"][e]
                            f.write(f" -> {', '.join(types)}")
                            # Try to inspect these event classes
                            for t_str in types:
                                short_name = t_str.split('.')[-1]
                                if short_name not in event_class_cache:
                                    found_cls = None
                                    for mod in flet_modules_for_events:
                                        if hasattr(mod, short_name):
                                            found_cls = getattr(mod, short_name)
                                            break
                                    
                                    if found_cls:
                                        event_class_cache[short_name] = get_event_class_info(found_cls)
                                    else:
                                        event_class_cache[short_name] = {"name": short_name, "properties": [f"(Class definition not found: {t_str})"]}
                        f.write("\n")
                else:
                    f.write("None\n")
                f.write("\n")

                f.write("### Key Methods\n")
                common = ['update', 'clean', 'build', 'did_mount', 'will_unmount', 'expand', 'invoke_method', 'get_attr', 'set_attr']
                methods = [m for m in info["methods"] if m not in common and not m.startswith('get_') and not m.startswith('set_')] # Filter get/set pairs too
                if methods:
                    f.write(", ".join([f"`{m}`" for m in methods]))
                else:
                    f.write("None (Standard lifecycle methods or property accessors only)")
                f.write("\n\n")
                
                f.write("---\n\n")
                
            except Exception as e:
                f.write(f"## {info['name']} (Error)\n")
                f.write(f"Failed to inspect {info['name']}: {e}\n\n")

        # Append Event Class Details
        f.write("# Event Object Details\n\n")
        # Sort events for consistent output
        sorted_event_classes = sorted(event_class_cache.keys())
        for cls_name in sorted_event_classes:
            details = event_class_cache[cls_name]
            f.write(f"## {cls_name}\n")
            if details and details["properties"]: # Event classes only have attributes
                for p in details["properties"]:
                    f.write(f"* {p}\n")
            else:
                f.write("* (No specific properties found or class details)\n")
            f.write("\n")

if __name__ == "__main__":
    generate_markdown()
    print(f"API Reference generated: {OUTPUT_FILE}")