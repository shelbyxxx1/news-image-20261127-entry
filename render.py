"""Draw the fixed Friday edition without network access or generated timestamps."""

import argparse
from collections import Counter
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SIZE = 1024
SCALE = 2
MARGIN = 22
PAPER = "#f6f1e5"
INK = "#191919"
BURGUNDY = "#7f1d1d"
GREEN = "#14532d"
SEA = "#5b7186"
MUTED = "#645f55"
RULE = "#b5ad9d"
LIGHT = "#e8e1d2"
WHITE = "#ffffff"

STORY_TABLE = (
    (1, "MIDDLE EAST", "War & security"),
    (2, "MIDDLE EAST", "War & security"),
    (3, "MIDDLE EAST", "War & security"),
    (4, "MIDDLE EAST", "War & security"),
    (5, "MIDDLE EAST", "War & security"),
    (6, "MIDDLE EAST", "Politics"),
    (7, "AMERICAS", "Disaster"),
    (8, "AMERICAS", "Culture"),
    (9, "AMERICAS", "Politics"),
    (10, "AMERICAS", "Markets & business"),
    (11, "AMERICAS", "Culture"),
    (12, "AMERICAS", "Disaster"),
    (13, "AMERICAS", "Culture"),
    (14, "EUROPE", "Politics"),
    (15, "EUROPE", "Justice"),
    (16, "EUROPE", "Disaster"),
    (17, "EUROPE", "War & security"),
    (18, "EUROPE", "Politics"),
    (19, "EUROPE", "Tech"),
    (20, "EUROPE", "Politics"),
    (21, "EUROPE", "Justice"),
    (22, "SPORT", "Sport"),
    (23, "ASIA", "Disaster"),
    (24, "AFRICA", "Disaster"),
    (25, "ASIA", "Disaster"),
    (26, "ASIA", "Justice"),
    (27, "ASIA", "Justice"),
    (28, "ASIA", "War & security"),
    (29, "ASIA", "War & security"),
    (30, "ASIA", "Politics"),
    (31, "OCEANIA", "Politics"),
    (32, "OCEANIA", "Climate"),
    (33, "WORLD", "Markets & business"),
    (34, "EUROPE", "Markets & business"),
    (35, "SPORT", "Sport"),
    (36, "WORLD", "Culture"),
)

REGIONS = (
    "MIDDLE EAST", "AMERICAS", "EUROPE", "ASIA", "AFRICA", "OCEANIA", "WORLD", "SPORT"
)
FIELDS = (
    "War & security", "Disaster", "Politics", "Justice", "Markets & business",
    "Culture", "Sport", "Tech", "Climate",
)

CARDS = (
    (2, "AMERICAS", "DISASTER", "Thanksgiving storms leave 900,000 in the dark",
     "Severe storms snarl US holiday travel and cancel hundreds of flights; 80 million on the move.",
     "storm"),
    (3, "SPORT", "CHESS", "Gukesh–Sindarov: marathon draw in Game 3",
     "Nothing separates the two after three games of the World Championship match.", "chess"),
    (4, "MIDDLE EAST", "WAR", "Hamas weighs reply after 10 killed in Gaza",
     "Israel kills 10 in Gaza; 16 schoolchildren have died there this month.", "gaza"),
    (5, "EUROPE", "POLITICS", "UK migration falls to lowest since 1997",
     "Net migration drops to its lowest level since 1997, outside the pandemic years.", "uk"),
    (6, "EUROPE", "JUSTICE", "Depardieu to stand trial over 2018 rape claim",
     "A court rules the actor must face trial over an alleged rape of an actress.", "court"),
    (7, "EUROPE", "DISASTER", "Tanker capsizes off Ibiza, one dead",
     "A diesel tanker carrying up to 7,000 tonnes goes down; one crew member is killed.", "tanker"),
    (8, "ASIA", "DISASTER", "Bangkok refinery blast injures nine",
     "An explosion at an oil refinery leaves three people in critical condition.", "refinery"),
    (9, "AFRICA", "HEALTH", "Ebola in Congo passes 12,000 cases",
     "Unrest forces responders to leave as the epidemic grows.", "clinic"),
)

BRIEFS = (
    "10 AMERICAS — Elon Musk says every child in the US will get two SpaceX shares.",
    "11 CULTURE — A US pastor who wants women's right to vote overturned.",
    "12 AMERICAS — The US grounds flights to Washington's DCA airport as storms bite.",
    "13 CULTURE — A fireball steals the show at a Thanksgiving drone display in Indiana.",
    "14 EUROPE — Net migration to the UK falls to its lowest since 1997, outside the pandemic.",
    "15 EUROPE — Gérard Depardieu to stand trial over an alleged rape in 2018, a court rules.",
    "16 EUROPE — A diesel tanker carrying up to 7,000 tonnes capsizes off Ibiza, killing one.",
    "17 EUROPE — Zelensky questions the 'strange' Trump–Putin friendship in a BBC interview.",
    "18 EUROPE — France's political mainstream risks a presidential vote debacle, with no clear candidate.",
    "19 EUROPE — Belgium opens Europe's largest satellite factory, able to build 500 a year.",
    "20 EUROPE — Spain heads to a snap vote on Sunday as Sánchez faces a conservative challenge.",
    "21 EUROPE — A German boat dealer is suspected of supplying Channel smuggling gangs, the BBC finds.",
    "22 SPORT — World Chess Championship: Gukesh and Sindarov draw a marathon Game 3.",
    "23 ASIA — A Bangkok oil refinery blast injures nine, three critically.",
    "24 AFRICA — Ebola in Congo passes 12,000 cases as unrest drives responders away.",
    "25 ASIA — Nepal begins declaring 4,000 missing landslide victims dead.",
    "26 ASIA — India's Supreme Court: a judicial member must sit to confirm a PMLA attachment.",
    "27 ASIA — India's top court quashes the early release of ex-MP Anand Mohan in Bihar.",
    "28 ASIA — China's drones are reshaping Asia's militaries.",
    "29 ASIA — Kim Jong Un vows permanent nuclear armament and accuses the US of raising threats.",
    "30 ASIA — Myanmar refuses to comply with parts of the ICJ genocide ruling.",
    "31 OCEANIA — New Zealand's final election count gives the coalition a slim 67–131 majority.",
    "32 OCEANIA — Australia braces for a severe bushfire season; Sydney battles a fire-ant outbreak.",
    "33 WORLD — Black Friday: a third of retailers deepen discounts, but half of tracked goods cost the same or less at other times.",
    "34 EUROPE — Norse Atlantic suspends all flights as it faces possible collapse.",
    "35 SPORT — Geordie Barrett will captain the All Blacks for the first time against England.",
    "36 WORLD — A Canadian astronaut welcomes a baby girl from the space station.",
)

FIGURES = (
    ("2", "Italian technicians killed in Kuwait"),
    ("900,000+", "homes and businesses without power in US storms"),
    ("12,000", "Ebola cases in Congo"),
    ("7,000", "tonnes of diesel on the tanker that capsized off Ibiza"),
    ("500", "satellites a year from Belgium's new factory"),
    ("4,000", "missing landslide victims declared dead in Nepal"),
)

DATE_CHECK = (
    "DATE CHECK — Left out on purpose because they broke before today: the Hong Kong "
    "renovation blaze that killed 168 (26 Nov); Miss Universe 2026: Jennifer Barreto wins "
    "(26 Nov); Duran Duran guitarist Andy Taylor dies aged 65 (26 Nov); Jensen Huang "
    "reinstated as Nvidia CEO (23 Nov); the COP31 talks collapsing (22–23 Nov); "
    "the Peru M6.7 earthquake (22 Nov)."
)

FOOTER = (
    "Lead illustration generated for this entry · Page drawn entirely by program · "
    "Set in Noto Serif Display & Noto Sans Condensed · Every story happened or was "
    "first reported Friday 27 November 2026. Sources: Reuters, BBC, CNN, NYT, WSJ, "
    "Al Jazeera, India Today, Mint."
)

CONTINENTS = (
    ((-168, 71), (-145, 71), (-125, 60), (-105, 73), (-80, 72), (-60, 53),
     (-54, 45), (-70, 42), (-81, 25), (-87, 21), (-79, 9), (-94, 17),
     (-107, 25), (-116, 32), (-129, 50), (-150, 58), (-168, 60)),
    ((-73, 60), (-49, 59), (-23, 77), (-43, 84), (-62, 79)),
    ((-81, 12), (-68, 10), (-48, -2), (-35, -7), (-40, -22), (-54, -36),
     (-65, -56), (-75, -44), (-71, -20), (-79, -5)),
    ((-10, 36), (-9, 44), (-1, 50), (-7, 58), (8, 58), (16, 71),
     (31, 71), (45, 62), (63, 65), (95, 77), (134, 72), (179, 65),
     (170, 52), (145, 46), (142, 35), (124, 29), (110, 19), (106, 8),
     (99, 3), (97, 20), (84, 23), (79, 7), (70, 22), (57, 25), (50, 13),
     (41, 14), (35, 29), (29, 36), (24, 40), (15, 37), (7, 44), (0, 37)),
    ((-17, 36), (8, 37), (25, 32), (35, 29), (43, 12), (51, 11),
     (42, -6), (34, -19), (27, -34), (17, -35), (11, -19), (5, -1),
     (-10, 5), (-17, 17)),
    ((112, -11), (133, -11), (145, -16), (154, -28), (145, -39),
     (130, -34), (115, -35), (112, -23)),
    ((47, -13), (51, -16), (49, -25), (44, -26)),
    ((130, 32), (141, 46), (145, 44), (141, 34)),
    ((95, 5), (103, 1), (106, -7), (114, -9), (119, -7), (114, 0),
     (118, 6), (124, 1), (132, -3), (143, -4), (148, -9), (136, -10),
     (122, -9), (108, -10), (99, -5)),
    ((166, -35), (175, -39), (179, -46), (171, -47), (165, -43)),
)


@lru_cache(maxsize=None)
def font(style, size):
    names = {
        "masthead": ("noto/NotoSerifDisplay-Black.ttf", "dejavu/DejaVuSerif-Bold.ttf"),
        "headline": ("noto/NotoSerifDisplay-CondensedBold.ttf", "dejavu/DejaVuSerifCondensed-Bold.ttf"),
        "serif": ("noto/NotoSerifDisplay-Bold.ttf", "dejavu/DejaVuSerif-Bold.ttf"),
        "body": ("noto/NotoSans-Condensed.ttf", "dejavu/DejaVuSansCondensed.ttf"),
        "bold": ("noto/NotoSans-CondensedBold.ttf", "dejavu/DejaVuSansCondensed-Bold.ttf"),
        "narrow": ("noto/NotoSans-ExtraCondensed.ttf", "dejavu/DejaVuSansCondensed.ttf"),
        "narrowbold": ("noto/NotoSans-ExtraCondensedBold.ttf", "dejavu/DejaVuSansCondensed-Bold.ttf"),
    }
    for relative in names[style]:
        candidate = Path("/usr/share/fonts/truetype") / relative
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), round(size * SCALE))
    raise FileNotFoundError(f"No Noto or DejaVu font for {style}")


def width(text, style, size):
    return font(style, size).getlength(text) / SCALE


def wrap(text, style, size, available):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if width(candidate, style, size) <= available:
            current = candidate
        else:
            if not current or width(word, style, size) > available:
                raise ValueError(f"Unbreakable text exceeds its column: {word}")
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_bounds = []

    def rect(self, box, fill, outline=None, thickness=1):
        self.draw.rectangle(tuple(round(value * SCALE) for value in box),
                            fill=fill, outline=outline, width=round(thickness * SCALE))

    def path(self, points, fill, thickness=1):
        self.draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                       fill=fill, width=max(1, round(thickness * SCALE)), joint="curve")

    def polygon(self, points, fill):
        self.draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill)

    def ellipse(self, box, fill, outline=None, thickness=1):
        self.draw.ellipse(tuple(round(value * SCALE) for value in box),
                          fill=fill, outline=outline, width=max(1, round(thickness * SCALE)))

    def line(self, text, x, y, style="body", size=11, fill=INK, anchor="lt", limit=None):
        if size < 11:
            raise ValueError("Type smaller than 11 pixels is forbidden")
        if limit is not None and width(text, style, size) > limit + 0.1:
            raise ValueError(f"Text is too wide: {text}")
        origin = (round(x * SCALE), round(y * SCALE))
        bounds = self.draw.textbbox(origin, text, font=font(style, size), anchor=anchor)
        scaled = tuple(value / SCALE for value in bounds)
        if (scaled[0] < 20 or scaled[1] < 20 or
                scaled[2] > SIZE - 20 or scaled[3] > SIZE - 20):
            raise ValueError(f"Text outside the page frame: {text}: {scaled}")
        self.draw.text(origin, text, font=font(style, size), fill=fill, anchor=anchor)
        self.text_bounds.append((text, scaled))
        return scaled[3]

    def block(self, text, box, style="body", size=11, fill=INK, leading=None, max_lines=None):
        left, top, right, bottom = box
        lines = wrap(text, style, size, right - left)
        if max_lines is not None and len(lines) > max_lines:
            raise ValueError(f"Too many lines ({len(lines)}): {text}")
        leading = leading if leading is not None else size * 1.15
        actual_bottom = top
        for index, content in enumerate(lines):
            actual_bottom = self.line(content, left, top + index * leading,
                                      style, size, fill, limit=right - left)
            if actual_bottom > bottom + 0.1:
                raise ValueError(f"Text exceeds its box by {actual_bottom - bottom:.1f}px: {text}")
        return actual_bottom


def count_bar(page, counts, order, top, accent):
    labels = [f"{name} {counts[name]}" for name in order]
    total = sum(width(label, "bold", 11) for label in labels)
    gap = (SIZE - 2 * MARGIN - total) / (len(labels) - 1)
    if gap < 8:
        raise ValueError("Count labels do not fit")
    cursor = MARGIN
    for index, label in enumerate(labels):
        page.line(label, cursor, top, "bold", 11, accent)
        cursor += width(label, "bold", 11)
        if index + 1 < len(labels):
            page.ellipse((cursor + gap / 2 - 1, top + 4, cursor + gap / 2 + 1, top + 6), RULE)
        cursor += gap


def draw_header(page):
    page.line("LATE EDITION · ALL THE NEWS OF ONE DAY ON ONE PAGE", MARGIN, 22, "bold", 11)
    page.line("No. 2026-331", SIZE - MARGIN, 22, "body", 11, anchor="rt")
    page.path(((MARGIN, 39), (SIZE - MARGIN, 39)), INK, 0.8)
    page.line("THE WORLD IN ONE DAY", 512, 44, "masthead", 70, anchor="mt")
    page.rect((MARGIN, 103, SIZE - MARGIN, 131), BURGUNDY)
    page.line("FRIDAY, 27 NOVEMBER 2026 — 36 STORIES · 8 REGIONS · ONE PAGE",
              512, 108, "bold", 20, WHITE, "mt", SIZE - 2 * MARGIN - 16)
    regions = Counter(story[1] for story in STORY_TABLE)
    fields = Counter(story[2] for story in STORY_TABLE)
    assert sum(regions.values()) == sum(fields.values()) == len(STORY_TABLE) == 36
    assert tuple(regions[name] for name in REGIONS) == (6, 7, 9, 7, 1, 2, 2, 2)
    assert tuple(fields[name] for name in FIELDS) == (8, 6, 7, 4, 3, 4, 2, 1, 1)
    count_bar(page, regions, REGIONS, 139, BURGUNDY)
    count_bar(page, fields, FIELDS, 155, GREEN)
    page.path(((MARGIN, 171), (SIZE - MARGIN, 171)), INK, 1.2)


def draw_lead(page):
    page.line("MIDDLE EAST · WAR & SECURITY — THE LEAD", MARGIN, 179, "bold", 11, BURGUNDY)
    page.line("Drones over Kuwait", MARGIN - 1, 194, "serif", 44)
    deck = ("Two Italian technicians killed as drones hit a Kuwaiti air-defence site; "
            "Italy and Kuwait blame Iran — Tehran denies any role and calls it a possible false flag.")
    page.block(deck, (MARGIN, 234, SIZE - MARGIN, 263), "body", 14, leading=16, max_lines=2)
    hero_box = (MARGIN, 253, 491, 365)
    with Image.open(ROOT / "hero.png") as source:
        hero = ImageOps.fit(source.convert("RGB"),
                            ((hero_box[2] - hero_box[0]) * SCALE,
                             (hero_box[3] - hero_box[1]) * SCALE),
                            method=Image.Resampling.LANCZOS, centering=(0.5, 0.41))
    page.image.paste(hero, (hero_box[0] * SCALE, hero_box[1] * SCALE))
    page.rect(hero_box, None, RULE, 0.5)
    bullets = (
        "The dead worked for Rheinmetall Italia, maintaining detection antennas for the Skyguard air-defence system.",
        "A Kuwaiti soldier and a Pakistani national were also wounded.",
        "Iran's foreign minister phoned his Kuwaiti and Italian counterparts to deny involvement.",
    )
    cursor = 254
    for text in bullets:
        page.ellipse((506, cursor + 4, 509, cursor + 7), BURGUNDY)
        cursor = page.block(text, (518, cursor, SIZE - MARGIN, 365),
                            "body", 14, leading=16) + 7


def scene(page, kind, box):
    left, top, right, bottom = box
    span = right - left
    height = bottom - top

    def point(horizontal, vertical):
        return (left + span * horizontal, top + height * vertical)

    def shape(coordinates, fill):
        page.polygon([point(horizontal, vertical) for horizontal, vertical in coordinates], fill)

    def rectangle(x1, y1, x2, y2, fill):
        page.rect((*point(x1, y1), *point(x2, y2)), fill)

    def stroke(coordinates, fill, thickness=1):
        page.path([point(horizontal, vertical) for horizontal, vertical in coordinates], fill, thickness)

    def oval(x1, y1, x2, y2, fill):
        page.ellipse((*point(x1, y1), *point(x2, y2)), fill)

    if kind == "storm":
        rectangle(0, 0, 1, 1, "#a9bdc7")
        rectangle(0, .60, 1, 1, "#536577")
        shape(((.33, 1), (.45, .55), (.57, .55), (.72, 1)), "#323b45")
        stroke(((.5, .68), (.51, .81)), "#f8e9b9", 1)
        stroke(((.53, .90), (.54, 1)), "#f8e9b9", 1)
        for horizontal in (.08, .20, .66, .78):
            oval(horizontal, .03, horizontal + .23, .57, "#475562")
        for horizontal in (.14, .29, .74, .88):
            stroke(((horizontal, .55), (horizontal - .025, .86)), "#dce9ed", 1)
        shape(((.57, .2), (.52, .55), (.58, .48), (.55, .79), (.65, .34), (.59, .4)), "#efd28a")
        rectangle(.39, .78, .46, .94, "#c7d3d3")
        rectangle(.58, .74, .65, .89, "#b76e56")
    elif kind == "chess":
        rectangle(0, 0, 1, 1, "#203b35")
        for row in range(2):
            for column in range(12):
                if (row + column) % 2 == 0:
                    rectangle(column / 12, .66 + row * .17, (column + 1) / 12, .83 + row * .17, "#aab89a")
        for center, colour in ((.32, "#efe5ce"), (.64, "#101e1c")):
            shape(((center - .06, .83), (center - .045, .70), (center - .025, .55),
                   (center - .035, .35), (center + .035, .35), (center + .025, .55),
                   (center + .045, .70), (center + .06, .83)), colour)
            rectangle(center - .01, .06, center + .01, .40, colour)
            rectangle(center - .035, .16, center + .035, .23, colour)
        oval(.45, .35, .50, .63, "#dfb775")
        shape(((.445, .83), (.465, .54), (.49, .54), (.51, .83)), "#dfb775")
    elif kind == "gaza":
        rectangle(0, 0, 1, 1, "#cfab94")
        oval(.70, .12, .77, .74, "#e1c289")
        for index, building in enumerate((.55, .20, .44, .34, .60, .25, .46, .63, .29, .51)):
            rectangle(index * .1, building, index * .1 + .085, 1, "#554d50")
        rectangle(.57, .34, .59, 1, "#403c43")
        for index in range(4):
            oval(.20 + index * .025, .36 - index * .13,
                 .27 + index * .04, .67 - index * .13, "#7a7272")
    elif kind == "uk":
        rectangle(0, 0, 1, 1, "#425775")
        stroke(((0, 0), (1, 1)), "#d4d6ce", 5)
        stroke(((0, 1), (1, 0)), "#d4d6ce", 5)
        rectangle(.44, 0, .56, 1, "#d4d6ce")
        rectangle(0, .36, 1, .64, "#d4d6ce")
        rectangle(.47, 0, .53, 1, "#a64e50")
        rectangle(0, .43, 1, .57, "#a64e50")
        stroke(((.13, .15), (.36, .29), (.57, .29), (.79, .74)), "#f4d6a0", 3)
        shape(((.73, .72), (.85, .90), (.86, .52)), "#f4d6a0")
    elif kind == "court":
        rectangle(0, 0, 1, 1, "#d6c9b6")
        shape(((.23, .30), (.50, .02), (.77, .30)), "#806b66")
        rectangle(.24, .33, .76, .40, "#806b66")
        for horizontal in (.28, .39, .50, .61, .70):
            rectangle(horizontal, .40, horizontal + .035, .82, "#f7efdf")
        rectangle(.22, .84, .79, .92, "#806b66")
        rectangle(.18, .94, .83, 1, "#806b66")
    elif kind == "tanker":
        rectangle(0, 0, 1, 1, "#a9c5cd")
        rectangle(0, .61, 1, 1, SEA)
        shape(((.23, .26), (.81, .54), (.75, .83), (.30, .58)), "#394854")
        shape(((.27, .45), (.79, .68), (.75, .83), (.30, .59)), "#8f4440")
        shape(((.30, .19), (.39, .23), (.38, .44), (.29, .40)), "#eee7d5")
        for horizontal in (.1, .38, .72):
            stroke(((horizontal, .86), (horizontal + .10, .81), (horizontal + .19, .86)), "#d5e3df", 1)
    elif kind == "refinery":
        rectangle(0, 0, 1, 1, "#d1af8c")
        rectangle(0, .84, 1, 1, "#4a4d4a")
        for horizontal, chimney_top in ((.16, .12), (.29, .26), (.54, .1), (.70, .31)):
            rectangle(horizontal, chimney_top, horizontal + .035, .93, "#535855")
            stroke(((horizontal - .01, .66), (horizontal + .08, .66)), "#353e3e", 1)
        stroke(((.18, .61), (.42, .61), (.42, .90)), "#4c5653", 2)
        shape(((.74, .91), (.71, .45), (.78, .61), (.81, .04), (.88, .35),
               (.88, .20), (.96, .66), (.94, .93)), "#c35936")
        shape(((.81, .93), (.79, .63), (.84, .39), (.89, .77), (.90, .92)), "#f8d47a")
    elif kind == "clinic":
        rectangle(0, 0, 1, 1, "#b9c9ac")
        rectangle(0, .79, 1, 1, "#849b72")
        shape(((.20, .42), (.49, .02), (.81, .43)), "#5c7461")
        rectangle(.25, .42, .76, .94, "#eee7d4")
        rectangle(.44, .54, .56, .94, "#74856d")
        rectangle(.48, .22, .52, .53, BURGUNDY)
        rectangle(.445, .32, .555, .43, BURGUNDY)


def draw_cards(page):
    gap = 16
    cell_width = (SIZE - 2 * MARGIN - 3 * gap) / 4
    row_tops = (377, 482)
    for index, (number, region, field, title, deck, kind) in enumerate(CARDS):
        row, column = divmod(index, 4)
        left = MARGIN + column * (cell_width + gap)
        right = left + cell_width
        top = row_tops[row]
        scene(page, kind, (left, top, right, top + 24))
        page.line(f"{number} · {region} · {field}", left, top + 26,
                  "narrowbold", 11, BURGUNDY, limit=cell_width)
        page.block(title, (left, top + 39, right, top + 73),
                   "headline", 17, leading=17, max_lines=2)
        page.block(deck, (left, top + 76, right, top + 104),
                   "narrow", 11, leading=11.5, max_lines=3)
        if column < 3:
            page.path(((right + gap / 2, top), (right + gap / 2, top + 98)), RULE, .5)
    page.path(((MARGIN, 477), (SIZE - MARGIN, 477)), RULE, .6)
    page.path(((MARGIN, 586), (SIZE - MARGIN, 586)), INK, 1)


def draw_figures(page):
    column_width = (SIZE - 2 * MARGIN) / 6
    for index, (figure, label) in enumerate(FIGURES):
        left = MARGIN + index * column_width
        if index:
            page.path(((left, 594), (left, 644)), RULE, .5)
        page.line(figure, left + column_width / 2, 594, "serif", 27, GREEN, "mt")
        lines = wrap(label, "narrow", 11, column_width - 17)
        for row, text in enumerate(lines):
            page.line(text, left + column_width / 2, 622 + row * 11.5,
                      "narrow", 11, INK, "mt", column_width - 17)
    page.path(((MARGIN, 653), (SIZE - MARGIN, 653)), INK, 1)


def inside_polygon(horizontal, vertical, polygon):
    inside = False
    previous = len(polygon) - 1
    for current, (current_x, current_y) in enumerate(polygon):
        previous_x, previous_y = polygon[previous]
        if ((current_y > vertical) != (previous_y > vertical) and
                horizontal < (previous_x - current_x) * (vertical - current_y) /
                (previous_y - current_y) + current_x):
            inside = not inside
        previous = current
    return inside


def draw_map(page, left, top, right, bottom):
    page.line("WHERE IT HAPPENED", left, top, "bold", 14, GREEN)
    map_top = top + 27
    map_bottom = map_top + 121
    map_left = left + 2
    map_right = right - 2

    def project(longitude, latitude):
        return (map_left + (longitude + 180) / 360 * (map_right - map_left),
                map_top + (84 - latitude) / 144 * (map_bottom - map_top))

    for latitude in (-30, 0, 30, 60):
        start, finish = project(-180, latitude), project(180, latitude)
        page.path((start, finish), "#dfdfd5", .5)
    for latitude in range(-54, 82, 5):
        for longitude in range(-175, 179, 5):
            if any(inside_polygon(longitude, latitude, polygon) for polygon in CONTINENTS):
                horizontal, vertical = project(longitude, latitude)
                page.ellipse((horizontal - 1, vertical - 1, horizontal + 1, vertical + 1), SEA)

    pins = (
        (1, "Kuwait", 47.98, 29.38, .59, .47),
        (2, "Gaza", 34.47, 31.50, .50, .27),
        (4, "Jazan", 42.55, 16.89, .58, .78),
        (5, "Tehran", 51.39, 35.69, .73, .26),
        (7, "New York", -74.01, 40.71, .13, .15),
        (8, "New York", -74.01, 40.71, .27, .13),
        (9, "Washington", -77.04, 38.91, .19, .49),
    )
    for number, name, longitude, latitude, offset_x, offset_y in pins:
        target_x, target_y = project(longitude, latitude)
        pin_x = map_left + offset_x * (map_right - map_left)
        pin_y = map_top + offset_y * (map_bottom - map_top)
        page.path(((target_x, target_y), (pin_x, pin_y)), BURGUNDY, .7)
        page.ellipse((target_x - 1.5, target_y - 1.5, target_x + 1.5, target_y + 1.5), BURGUNDY)
        page.ellipse((pin_x - 7, pin_y - 7, pin_x + 7, pin_y + 7), BURGUNDY, PAPER, .6)
        page.line(str(number), pin_x, pin_y - 4.5, "bold", 11, WHITE, "mt")
    legend_top = map_bottom + 14
    legend = ("1 Kuwait · 2 Gaza", "4 Jazan (Saudi Arabia)", "5 Tehran", "7 New York · 8 New York", "9 Washington")
    for index, text in enumerate(legend):
        page.line(text, left, legend_top + index * 15, "body", 11, INK, limit=right - left)
    if legend_top + len(legend) * 15 > bottom:
        raise ValueError("Map legend exceeds its box")


def draw_briefs(page):
    top = 665
    text_top = 686
    text_bottom = 916
    leading = 11.8
    gap = 15
    chosen = None
    for map_width in range(390, 229, -2):
        list_right = SIZE - MARGIN - map_width - 20
        column_width = (list_right - MARGIN - gap) / 2
        wrapped = [wrap(text, "narrow", 11, column_width) for text in BRIEFS]
        for split in range(11, 16):
            heights = tuple(sum(len(lines) for lines in column) * leading
                            for column in (wrapped[:split], wrapped[split:]))
            if max(heights) <= text_bottom - text_top:
                chosen = (list_right, column_width, split, wrapped, heights)
                break
        if chosen:
            break
    if not chosen:
        raise ValueError("Full briefs cannot fit at the minimum 11-pixel type size")
    list_right, column_width, split, wrapped, heights = chosen
    page.line("ALSO ON FRIDAY 27 NOVEMBER", MARGIN, top, "bold", 14, GREEN)
    page.path(((list_right + 9, top), (list_right + 9, 916)), RULE, .6)
    page.path(((MARGIN + column_width + gap / 2, text_top),
               (MARGIN + column_width + gap / 2, 916)), RULE, .5)
    for column, text_rows in enumerate((wrapped[:split], wrapped[split:])):
        cursor = text_top
        left = MARGIN + column * (column_width + gap)
        for lines in text_rows:
            for index, text in enumerate(lines):
                page.line(text, left, cursor, "narrow", 11, INK, limit=column_width)
                cursor += leading
    draw_map(page, list_right + 20, top, SIZE - MARGIN, 916)
    return {"brief_split": split, "brief_column_width": column_width,
            "brief_column_heights": heights, "map_width": SIZE - MARGIN - list_right - 20}


def draw_bottom(page):
    page.rect((MARGIN, 926, SIZE - MARGIN, 969), None, BURGUNDY, 1.2)
    page.block(DATE_CHECK, (MARGIN + 10, 934, SIZE - MARGIN - 10, 963),
               "body", 11, BURGUNDY, leading=12.5, max_lines=3)
    page.path(((MARGIN, 975), (SIZE - MARGIN, 975)), INK, .6)
    page.block(FOOTER, (MARGIN, 981, SIZE - MARGIN, 1004),
               "narrow", 11, MUTED, leading=11.5, max_lines=2)


def render(output):
    page = Page()
    draw_header(page)
    draw_lead(page)
    draw_cards(page)
    draw_figures(page)
    layout = draw_briefs(page)
    draw_bottom(page)
    image = page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    encoded = BytesIO()
    image.save(encoded, format="PNG", optimize=True, compress_level=9)
    file_format = "PNG"
    if encoded.tell() > 1048576:
        encoded = BytesIO()
        image.save(encoded, format="JPEG", quality=82, subsampling=0, optimize=True)
        file_format = "JPEG"
    data = encoded.getvalue()
    if len(data) > 1048576:
        raise ValueError(f"Image exceeds the 1 MiB limit: {len(data)} bytes")
    output.write_bytes(data)
    print(f"{output}: {SIZE}x{SIZE} {file_format}, {len(data)} bytes; "
          f"36 stories, region total 36, field total 36; {layout}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "entry.png")
    arguments = parser.parse_args()
    render(arguments.output)
