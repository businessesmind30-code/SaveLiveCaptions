import asyncio
import re

import uiautomation as auto

from .save import save_txt


def normalize_caption_text(text: str) -> str:
    """Keep the displayed text intact apart from collapsing whitespace."""
    return re.sub(r"\s+", " ", text).strip()


def is_sentence_boundary(text: str, index: int, contains_chinese: bool) -> bool:
    """Return whether the character at index completes a caption sentence."""
    char = text[index]

    if char == "，":
        return contains_chinese

    if char not in "。！？；.;!?":
        return False

    # A dot inside a number is a decimal separator, not sentence punctuation.
    if char == ".":
        previous = text[index - 1] if index else ""
        following = text[index + 1] if index + 1 < len(text) else ""
        if previous.isdigit() and following.isdigit():
            return False

    return True


def split_caption_text(text: str) -> tuple[list[str], str]:
    """Split only at displayed punctuation while preserving caption wording."""
    text = normalize_caption_text(text)
    if not text:
        return [], ""

    completed: list[str] = []
    start = 0
    contains_chinese = False

    for index, char in enumerate(text):
        if "\u4e00" <= char <= "\u9fff":
            contains_chinese = True

        if not is_sentence_boundary(text, index, contains_chinese):
            continue

        end = index + 1
        while end < len(text) and text[end] in "，。！？；.;!?":
            # Do not treat the decimal point in e.g. 3.14 as punctuation.
            if (
                text[end] == "."
                and end > 0
                and end + 1 < len(text)
                and text[end - 1].isdigit()
                and text[end + 1].isdigit()
            ):
                break
            end += 1

        sentence = text[start:end].strip()
        if sentence:
            completed.append(sentence)
        start = end
        contains_chinese = False

    return completed, text[start:].strip()


def overlap_length(previous: list[str], current: list[str]) -> int:
    """Find the exact shared boundary between successive caption snapshots."""
    maximum = min(len(previous), len(current))
    for size in range(maximum, 0, -1):
        if previous[-size:] == current[:size]:
            return size
    return 0


def lc_detect() -> bool:
    try:
        auto.SetGlobalSearchTimeout(0.5)
        desktop = auto.GetRootControl()
        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow",
            timeout=0.2,
        )
        if captions_window.Exists(0):
            print("Live Captions Found")
            return True

        print("Live Captions Not Found")
        return False
    except Exception as error:
        print(f"Live Captions Not Found: {str(error)[:50]}...")
        return False


async def hook(filename, exit_event):
    """Write captions as displayed, with only whitespace and sentence splitting."""
    previous_completed: list[str] = []
    trailing_text = ""

    try:
        if not lc_detect():
            return False

        desktop = auto.GetRootControl()
        captions_window = desktop.Control(
            searchDepth=1,
            ClassName="LiveCaptionsDesktopWindow",
        )
        await asyncio.sleep(1)
        captions_scrollviewer = captions_window.Control(
            searchDepth=5,
            AutomationId="CaptionsScrollViewer",
            ClassName="ScrollViewer",
        )

        print("Start capture...")

        while not exit_event.is_set():
            current_text = captions_scrollviewer.Name
            completed, trailing_text = split_caption_text(current_text)

            overlap = overlap_length(previous_completed, completed)
            for sentence in completed[overlap:]:
                print(f"[SAVE] {sentence}")
                await save_txt(filename, sentence)

            previous_completed = completed
            await asyncio.sleep(0.25)

    except Exception as error:
        print(f"Exception caught: {error}")
        return False
    finally:
        # The only unfinished caption is saved once when capture ends.
        if trailing_text:
            print(f"[SAVE ON EXIT] {trailing_text}")
            await save_txt(filename, trailing_text)
        print("[EXIT] Done!")
