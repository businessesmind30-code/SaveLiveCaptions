import asyncio
import re
from dataclasses import dataclass
from collections.abc import Callable

import uiautomation as auto

from .save import save_txt
from .config import STABLE_THRESHOLD


@dataclass
class CaptionTrack:
    text: str
    observations: int = 0
    saved: bool = False


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


def split_caption_text(text: str) -> list[str]:
    """Split only at displayed punctuation while preserving caption wording."""
    text = normalize_caption_text(text)
    if not text:
        return []

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

    return completed


def align_tracks(
    previous_tracks: list[CaptionTrack], current_sentences: list[str]
) -> list[CaptionTrack]:
    """Carry observations forward for the same displayed caption occurrences."""
    previous_sentences = [track.text for track in previous_tracks]

    if (
        len(current_sentences) >= len(previous_sentences)
        and current_sentences[: len(previous_sentences)] == previous_sentences
    ):
        return previous_tracks + [
            CaptionTrack(text) for text in current_sentences[len(previous_tracks) :]
        ]

    maximum = min(len(previous_tracks), len(current_sentences))
    for size in range(maximum, 0, -1):
        if previous_sentences[-size:] == current_sentences[:size]:
            return previous_tracks[-size:] + [
                CaptionTrack(text) for text in current_sentences[size:]
            ]

    return [CaptionTrack(text) for text in current_sentences]


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


async def hook(
    filename: str,
    exit_event,
    formatter: Callable[[str], str] | None = None,
):
    """Save each displayed caption occurrence after it has stabilized."""
    tracks: list[CaptionTrack] = []

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

        print(f"Start capture... STABLE_THRESHOLD={STABLE_THRESHOLD}")

        while not exit_event.is_set():
            sentences = split_caption_text(captions_scrollviewer.Name)
            tracks = align_tracks(tracks, sentences)

            for track in tracks:
                track.observations += 1
                if track.saved or track.observations < STABLE_THRESHOLD:
                    continue

                caption = track.text
                if formatter is not None:
                    try:
                        caption = formatter(track.text)
                    except Exception as error:
                        print(f"[FORMAT ERROR] Saving raw caption instead: {error}")

                print(f"[SAVE] {caption}")
                await save_txt(filename, caption)
                track.saved = True

            await asyncio.sleep(0.25)

    except Exception as error:
        print(f"Exception caught: {error}")
        return False
    finally:
        print("[EXIT] Done!")
