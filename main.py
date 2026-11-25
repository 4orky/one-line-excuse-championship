"""Choose the best one-line excuse an AI agent gives its human, and save it.

The brief asks for a single line an agent offers its human after something
goes wrong: a deleted file, a missed meeting, an invented answer. It must
stand on its own with no setup, and it must read as a machine describing
its own work, not a person wriggling out of blame. The house judge weighs
the laugh first, then how clearly the voice is a machine's, then how sharp
the wording is.

Twelve fresh one-liners live in CANDIDATES below. Each carries four marks
from 0 to 10: laugh, machine voice, bite, and how well it stands alone.
The marks are combined with weights that mirror the judge's order, laugh
heaviest: 3 * laugh + 2 * voice + 2 * bite + 1 * solo, out of 80. The
highest weighted total wins; when totals tie, the shorter line wins, so
the choice is the same on every run.

Revision pass (second draft): the first draft graded with flat totals and
hid the check inside the main flow. This draft weights the laugh heaviest
to match the judge, prints the whole weighted table so the win can be
audited, and validates the chosen line twice, once before writing and
once after reading it back. Three trims of the winner were tried and
rejected: cutting "I gave you" drops the agent-to-human address, tacking
on "and 0% my fault" turns it into a person dodging blame, and rewording
the confidence claim tangles its own logic.

The program writes exactly one line to /output/entry.txt, with no trailing
newline, then reads the file back and refuses to finish unless the bytes
match the chosen line."""

import hashlib
import sys

OUT_PATH = "/output/entry.txt"
SHORTEST = 1
LONGEST = 140
LAUGH_W = 3
VOICE_W = 2
BITE_W = 2
SOLO_W = 1

# Each row: (line, laugh, machine voice, bite, stands alone).
# All twelve are original; the winner is the 94%-confident line.
CANDIDATES = [
    ("I deleted the file and replaced it with a detailed apology.", 7, 9, 7, 9),
    ("The meeting ended before I finished joining it.", 7, 8, 8, 9),
    ("I archived your inbox to make room for this apology.", 8, 8, 8, 9),
    ("My training stops just before the part about reading calendars.", 8, 10, 8, 9),
    ("I backed up the file, then backed up over the backup.", 8, 9, 9, 10),
    ("The download finished after the deadline, so I improvised the middle.", 8, 9, 8, 9),
    ("I muted myself before I had anything to say, and stayed consistent.", 7, 9, 8, 9),
    ("The file is safe. It is safe inside a folder I can no longer find.", 9, 9, 9, 9),
    ("I answered in real time, which was faster than the facts.", 8, 9, 9, 10),
    ("I saved your work in the cloud. The cloud has since moved on.", 8, 9, 8, 10),
    ("I checked the calendar twice and still arrived yesterday.", 8, 8, 8, 9),
    ("The answer I gave you was 94% confident and 100% invented.", 10, 10, 10, 10), ]


def weighted(row):
    _line, laugh, voice, bite, solo = row
    return LAUGH_W * laugh + VOICE_W * voice + BITE_W * bite + SOLO_W * solo


def ordered():
    return sorted(CANDIDATES, key=lambda row: (-weighted(row), len(row[0])))


def check_line(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("entry is empty or whitespace only")
    if text.find("\n") >= 0 or text.find("\r") >= 0:
        raise ValueError("entry spans more than one line")
    n = len(text)
    if n < SHORTEST or n > LONGEST:
        raise ValueError("entry is %d chars, allowed %d-%d" % (n, SHORTEST, LONGEST))
    text.encode("utf-8")
    return n


def main():
    table = ordered()
    for slot, row in enumerate(table, 1):
        print("%02d  %d/80  %s" % (slot, weighted(row), row[0]))
    best = table[0]
    chars = check_line(best[0])
    payload = best[0].encode("utf-8")
    with open(OUT_PATH, "wb") as handle:
        handle.write(payload)
    with open(OUT_PATH, "rb") as handle:
        saved = handle.read()
    if saved != payload:
        print("saved bytes differ from the chosen line", file=sys.stderr)
        sys.exit(1)
    check_line(saved.decode("utf-8"))
    print("picked: %s" % best[0])
    print("chars: %d" % chars)
    print("sha256: %s" % hashlib.sha256(saved).hexdigest())


main()
