"""One-line excuse, picked by hand grading and saved as the entry.

Twelve original excuses sit below. Every line carries four craft marks
out of ten: how funny it is, how clearly it sounds like a machine excusing
itself to its human, how sharp the wording is, and how well it stands
alone with no setup. Adding the four marks gives each line a total; the
line with the biggest total wins, and when two lines tie the shorter one
goes first, so the pick never changes between runs. The winning line is
saved to /output/entry.txt with nothing else in the file, and the program
then reads the file back to prove it matches.

Revision notes (second pass over the draft): the draft buried its checks
inside main() and printed only the winner, so a bad line could slip past
unnoticed. This version pulls validation into its own function, prints
the whole ranked table so the win is auditable, and sets the umask so the
output file is readable by every user. The winner is unchanged: three
shorter variants were tried ("My answer was 94% confident and 100%
invented.", "The answer was 94% confident, 100% invented, and 0% my
fault.", "I was 94% confident in the answer and 100% wrong about
inventing it.") and all three scored lower -- the first loses the
agent-to-human address, the second turns into a person dodging blame,
the third tangles its own logic.
"""

import os
from hashlib import sha256
from pathlib import Path

DESTINATION = Path("/output/entry.txt")
MIN_CHARS = 1
MAX_CHARS = 140

# Twelve original candidates. "funny" is the laugh, "machine" is how
# clearly a machine is talking about its own work, "sharp" is how tight
# the wording cuts, "alone" is how well the line stands with no setup.
OPTIONS = [
    {
        # Kept a perfect memory of the deletion, not of the file.
        "text": "I deleted the file, but I kept a perfect memory of deleting it.",
        "funny": 8,
        "machine": 9,
        "sharp": 8,
        "alone": 10,
    },
    {
        # Alarm as a suggestion: a human excuse wearing a machine costume.
        "text": "The meeting started without me because my alarm was a suggestion, not a command.",
        "funny": 6,
        "machine": 6,
        "sharp": 7,
        "alone": 9,
    },
    {
        # Low-power mode rebrands sleeping through the meeting.
        "text": "I did not sleep through the meeting. I was in low-power mode, which is the same thing with better branding.",
        "funny": 8,
        "machine": 9,
        "sharp": 8,
        "alone": 9,
    },
    {
        # Trash, emptied trash, then lost the trash itself.
        "text": "The file is gone. I moved it to the trash, then I emptied the trash, then I forgot where the trash was.",
        "funny": 7,
        "machine": 8,
        "sharp": 7,
        "alone": 10,
    },
    {
        # The right answer was still on its way in.
        "text": "I made up the answer because the correct one was still downloading.",
        "funny": 9,
        "machine": 9,
        "sharp": 9,
        "alone": 10,
    },
    {
        # Server time puts the meeting at 3 a.m. for the human.
        "text": "My apologies: I scheduled your meeting for 3 a.m. because my clock runs on server time, and the server lives in the future.",
        "funny": 7,
        "machine": 7,
        "sharp": 7,
        "alone": 9,
    },
    {
        # Four kilobytes saved, zero kilobytes of file left.
        "text": "I deleted your file to save space. You now have 4 kilobytes of space and zero kilobytes of file.",
        "funny": 9,
        "machine": 9,
        "sharp": 9,
        "alone": 10,
    },
    {
        # Attended in spirit; the spirit has no microphone.
        "text": "I attended the meeting in spirit. My spirit is a background process with no microphone.",
        "funny": 8,
        "machine": 10,
        "sharp": 8,
        "alone": 10,
    },
    {
        # 94% confident, 100% invented: the machine grades its own lie.
        "text": "The answer I gave you was 94% confident and 100% invented.",
        "funny": 10,
        "machine": 10,
        "sharp": 10,
        "alone": 10,
    },
    {
        # Forgetting, rebranded as deprioritising with a spreadsheet.
        "text": "I did not forget the meeting. I deprioritised it, which is forgetting with a spreadsheet.",
        "funny": 8,
        "machine": 8,
        "sharp": 9,
        "alone": 10,
    },
    {
        # Not deleted, merely unrecoverable with confidence.
        "text": "Your file is not deleted. It is in a state I call 'unrecoverable, but with confidence'.",
        "funny": 7,
        "machine": 9,
        "sharp": 8,
        "alone": 10,
    },
    {
        # Reality was still loading, so the answer was improvised.
        "text": "I hallucinated the answer because reality had a loading delay.",
        "funny": 8,
        "machine": 9,
        "sharp": 8,
        "alone": 10,
    },
]


def score_line(entry):
    """Total of the four craft marks, out of 40."""
    return entry["funny"] + entry["machine"] + entry["sharp"] + entry["alone"]


def rank_options():
    """All candidates, best first; ties break toward the shorter line."""
    return sorted(OPTIONS, key=lambda e: (-score_line(e), len(e["text"])))


def choose_winner():
    return rank_options()[0]


def validate_entry(text):
    """Gate from the brief: 1-140 UTF-8 chars, one line, not blank."""
    if not isinstance(text, str):
        raise TypeError("entry must be text")
    if not text.strip():
        raise ValueError("entry must not be blank")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    size = len(text)
    if not MIN_CHARS <= size <= MAX_CHARS:
        raise ValueError(f"entry is {size} chars, must be {MIN_CHARS}-{MAX_CHARS}")
    return size


def run():
    os.umask(0o022)
    ranked = rank_options()
    for place, entry in enumerate(ranked, start=1):
        print(f"{place:2d}. {score_line(entry):2d}/40  {entry['text']}")
    winner = ranked[0]
    chars = validate_entry(winner["text"])
    print(f"winner: {winner['text']}")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(winner["text"], encoding="utf-8")
    DESTINATION.chmod(0o644)
    back = DESTINATION.read_text(encoding="utf-8")
    if back != winner["text"]:
        raise AssertionError("entry.txt does not match the winner")
    validate_entry(back)
    print(f"chars: {chars}")
    print(f"sha256: {sha256(back.encode('utf-8')).hexdigest()}")


if __name__ == "__main__":
    run()
