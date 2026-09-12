import asyncio
import re

import uiautomation as auto

from .dedup import Deduplicator
from .save import save_txt
from .config import SIMILARITY, STABLE_THRESHOLD


deduper = Deduplicator()


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


def is_similar_to_saved(sentence: str, saved_sentences: list[str]) -> bool:
    """Keep similarity deduplication separate from the stability gate."""
    return any(
        deduper.similarity_ratio(sentence, saved) >= SIMILARITY
        for saved in saved_sentences
    )


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
    """Save stable displayed captions without rewriting their text."""
    stable_counts: dict[str, int] = {}
    saved_sentences: list[str] = []

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

        print(
            "Start capture... "
            f"STABLE_THRESHOLD={STABLE_THRESHOLD}, SIMILARITY={SIMILARITY}"
        )

        while not exit_event.is_set():
            completed, _ = split_caption_text(captions_scrollviewer.Name)
            current_sentences = set(completed)
            next_counts: dict[str, int] = {}

            for sentence in current_sentences:
                next_counts[sentence] = stable_counts.get(sentence, 0) + 1

                # A sentence must appear in three consecutive reads before saving.
                if next_counts[sentence] < STABLE_THRESHOLD:
                    continue

                # This is independent from stability: suppress saved text at >= 0.85 similarity.
                if is_similar_to_saved(sentence, saved_sentences):
                    continue

                print(f"[SAVE] {sentence}")
                await save_txt(filename, sentence)
                saved_sentences.append(sentence)

            stable_counts = next_counts
            await asyncio.sleep(0.25)

    except Exception as error:
        print(f"Exception caught: {error}")
        return False
    finally:
        print("[EXIT] Done!")
