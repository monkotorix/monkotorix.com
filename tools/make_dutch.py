#!/usr/bin/env python3
"""Write the Dutch pages (site/nl/) from the English ones.

    python3 tools/make_dutch.py

The English pages are the source: this script copies site/index.html and
site/privacy/index.html, swaps every English text for its Dutch translation below,
and writes site/nl/index.html and site/nl/privacy/index.html. The styles, the hero
illustration and the icons are shared that way, so only the words differ.

Every English text must appear in its page exactly as often as listed (once, unless
a count is given). When the English copy changes, the script stops and names the
text it could not find: update the pair here (both languages), then run it again.
Never edit the files in site/nl/ by hand.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Shared between the two pages.
DISCLAIMER = (
    "Monkotorix provides games and playful activities for children. It is not a medical, therapeutic, diagnostic, "
    "or professional educational service and is not intended to replace advice or support from qualified "
    "healthcare or education professionals.",
    "Monkotorix biedt spelletjes en speelse activiteiten voor kinderen. Het is geen medische, therapeutische of "
    "diagnostische dienst en ook geen professionele onderwijsdienst, en het is niet bedoeld als vervanging van advies "
    "of ondersteuning door gekwalificeerde zorg- of onderwijsprofessionals.",
)

HOME = [
    # Page language, addresses and the language switch.
    ('<html lang="en-GB">', '<html lang="nl">'),
    ('<link rel="canonical" href="https://monkotorix.com/">', '<link rel="canonical" href="https://monkotorix.com/nl/">'),
    ('<meta property="og:locale" content="en_GB">', '<meta property="og:locale" content="nl_NL">'),
    ('<meta property="og:url" content="https://monkotorix.com/">', '<meta property="og:url" content="https://monkotorix.com/nl/">'),
    ('<meta property="og:image" content="https://monkotorix.com/assets/og.jpg">',
     '<meta property="og:image" content="https://monkotorix.com/assets/og-nl.jpg">'),
    ('<a class="lang-switch" href="/nl/" hreflang="nl" lang="nl" aria-label="Nederlands" title="Deze website in het Nederlands">NL</a>',
     '<a class="lang-switch" href="/" hreflang="en" lang="en" aria-label="English" title="This website in English">EN</a>'),
    ('<a href="/privacy/">Privacy</a>\n      <a href="/nl/" hreflang="nl" lang="nl">Nederlands</a>',
     '<a href="/nl/privacy/">Privacy</a>\n      <a href="/" hreflang="en" lang="en">English</a>'),
    # Screenshots of the games in Dutch where the English one shows English words.
    ('src="/assets/neurocrew.webp"', 'src="/assets/neurocrew-nl.webp"'),

    # Head.
    ("<title>Monkotorix — Different Minds. Endless Possibilities.</title>",
     "<title>Monkotorix — Verschillende breinen. Eindeloze mogelijkheden.</title>"),
    ('<meta name="description" content="Small games with movement, puzzles, letters and numbers, made by parents for their own neurodivergent children and shared with other families.">',
     '<meta name="description" content="Kleine spelletjes vol beweging, puzzels, letters en cijfers, gemaakt door ouders voor hun eigen neurodivergente kinderen en gedeeld met andere gezinnen.">'),
    ('<meta property="og:title" content="Monkotorix — Different Minds. Endless Possibilities.">',
     '<meta property="og:title" content="Monkotorix — Verschillende breinen. Eindeloze mogelijkheden.">'),
    ('<meta property="og:description" content="Small games made by parents for their own neurodivergent children. Three games to play now, in beta.">',
     '<meta property="og:description" content="Kleine spelletjes, gemaakt door ouders voor hun eigen neurodivergente kinderen. Drie spelletjes die je nu al kunt spelen, nog in bèta.">'),

    # Top of the page.
    ('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Naar de inhoud</a>'),
    ('<nav class="topbar" aria-label="Main">', '<nav class="topbar" aria-label="Hoofdmenu">'),
    ('<li><a href="#story">Our story</a></li>', '<li><a href="#story">Ons verhaal</a></li>'),
    ('<li><a href="#goal">Our goal</a></li>', '<li><a href="#goal">Ons doel</a></li>'),
    ('<li><a href="#games">Games</a></li>', '<li><a href="#games">Spelletjes</a></li>'),
    ('id="theme-toggle" aria-label="Dark theme"', 'id="theme-toggle" aria-label="Donker thema"'),
    ('<b>Beta</b> Three games to play now</a>', '<b>Bèta</b> Drie spelletjes om nu te spelen</a>'),
    ('<p class="hero-tagline">Different Minds. Endless&nbsp;Possibilities.</p>',
     '<p class="hero-tagline">Verschillende breinen. Eindeloze&nbsp;mogelijkheden.</p>'),
    ('<p class="hero-sub">Movement, puzzles, letters and numbers — small games to play together.</p>',
     '<p class="hero-sub">Bewegen, puzzelen, letters en cijfers — kleine spelletjes om samen te spelen.</p>'),
    ('<a class="btn primary" href="#games">Play the games<svg', '<a class="btn primary" href="#games">Naar de spelletjes<svg'),
    ('<a class="btn ghost" href="#story">Our story</a>', '<a class="btn ghost" href="#story">Ons verhaal</a>'),

    # Our story.
    ('<p class="rule">Our Story</p>', '<p class="rule">Ons verhaal</p>'),
    ("Monkotorix began with parents doing their best for their neurodivergent children, using what they know inside out: building software.",
     "Monkotorix begon bij ouders die hun best deden voor hun neurodivergente kinderen, met wat ze door en door kennen: software bouwen."),
    ("We made these games for our own children first and tried them out at home. Now we’re sharing them with any family who’d like to&nbsp;play.",
     "We maakten deze spelletjes eerst voor onze eigen kinderen en probeerden ze thuis uit. Nu delen we ze met elk gezin dat zin heeft om mee te&nbsp;spelen."),

    # Our goal.
    ('<p class="rule">Our Goal</p>', '<p class="rule">Ons doel</p>'),
    ("To help our children practise the things they find hard — <em>in games they actually want to&nbsp;play</em>.",
     "We willen onze kinderen helpen oefenen met wat ze moeilijk vinden — <em>in spelletjes die ze ook echt graag&nbsp;spelen</em>."),
    ('aria-label="Monkotorix sits where games on the screen, moving the body and playing together overlap."',
     'aria-label="Monkotorix zit precies waar spelletjes op het scherm, bewegen met je lijf en samen spelen elkaar overlappen."'),
    ('<div class="c c1" aria-hidden="true">Games on<br>the screen</div>', '<div class="c c1" aria-hidden="true">Spelletjes op<br>het scherm</div>'),
    ('<div class="c c2" aria-hidden="true">Moving<br>the body</div>', '<div class="c c2" aria-hidden="true">Bewegen<br>met je lijf</div>'),
    ('<div class="c c3" aria-hidden="true">Playing<br>together</div>', '<div class="c c3" aria-hidden="true">Samen<br>spelen</div>'),
    ("Each game is built around something our children found tricky, such as listening to the whole instruction before moving, waiting for the green light, switching when the rule changes, balancing on one leg, remembering a pattern, following the line of a letter or hearing the sounds inside a word.",
     "Elk spelletje draait om iets wat onze kinderen lastig vonden, zoals eerst naar de hele opdracht luisteren en dan pas bewegen, wachten op het groene licht, omschakelen als de regel verandert, op één been balanceren, een patroon onthouden, de lijn van een letter volgen of de klanken in een woord horen."),
    ("As parents, not therapists or teachers, we believe skills like these grow with practice, and that children keep at it when they’re enjoying themselves. So fun is the way in, not the goal. We mix the play as we think suits them best: a little on the screen, plenty of moving about and a grown-up alongside.",
     "Als ouders, niet als therapeuten of leerkrachten, geloven we dat zulke vaardigheden groeien door te oefenen, en dat kinderen volhouden als ze plezier hebben. Plezier is dus het middel, niet het doel. We wisselen het spelen af zoals het volgens ons het best bij hen past: een beetje op het scherm, veel bewegen en een volwassene erbij."),
    ("<p>We try to keep every game calm, clear and forgiving:</p>",
     "<p>We proberen elk spelletje rustig en duidelijk te houden, en fouten maken mag:</p>"),
    ('<ul class="cares" aria-label="How the games feel">', '<ul class="cares" aria-label="Hoe de spelletjes aanvoelen">'),
    ("Short rounds, no lives to lose</li>", "Korte rondes, geen levens die je kunt verliezen</li>"),
    ("Instructions read aloud</li>", "Opdrachten worden voorgelezen</li>"),
    ("A wrong try just means another go</li>", "Fout? Dan gewoon nog een keer</li>"),
    ("Calm screens, sound you can switch off</li>", "Rustige schermen, geluid dat je uit kunt zetten</li>"),

    # The games.
    ('<p class="rule">The Games</p>', '<p class="rule">De spelletjes</p>'),
    ('<h2 id="games-h" class="title">Three games so&nbsp;far</h2>', '<h2 id="games-h" class="title">Tot nu toe drie&nbsp;spelletjes</h2>'),
    ("You can play them all in the browser on a phone, tablet or computer. There’s nothing to install, no sign-up, no ads and no tracking — just open a game and play together.",
     "Je speelt ze allemaal in de browser op een telefoon, tablet of computer. Niets te installeren, geen account, geen reclame en geen tracking — open een spelletje en speel samen."),
    ('<span class="badge-beta">Beta</span>', '<span class="badge-beta">Bèta</span>', 3),
    ('<span class="nowrap">Ages 4–8</span>', '<span class="nowrap">4–8 jaar</span>', 2),

    # Monko Focus.
    ('<p class="sub">Movement &amp; puzzle games · ', '<p class="sub">Beweeg- en puzzelspelletjes · '),
    ("Short, playful games for hands, eyes and the whole body. A friendly buddy shows every move as children trace, pop, catch, copy and balance their way along a magic path through five worlds — with a breathing break always one tap away.",
     "Korte, speelse spelletjes voor handen, ogen en het hele lijf. Een vriendelijk maatje doet elke beweging voor, terwijl kinderen over een toverpad door vijf werelden gaan: lijnen natrekken, bellen laten knappen, vangen, nadoen en balanceren. Met één tik is er altijd een adempauze."),
    ("<li>21 games in six groups — from tracing and catching to patterns and little sudokus</li>",
     "<li>21 spelletjes in zes groepen — van natrekken en vangen tot patronen en kleine sudoku’s</li>"),
    ("<li>Separate levels for ages 4–5 and 6–8, with harder versions for children who want more challenge</li>",
     "<li>Aparte levels voor 4–5 en 6–8 jaar, met moeilijkere versies voor kinderen die meer uitdaging willen</li>"),
    ("<li>Calm mode, bigger targets, a slower speed and read-aloud instructions</li>",
     "<li>Rustige stand, grotere doelen om op te tikken, een lager tempo en opdrachten die worden voorgelezen</li>"),
    ("<li>A “Try it for real” idea for each game in the grown-up corner, to play together away from the screen</li>",
     "<li>Bij elk spelletje een “Probeer het echt”-idee in de volwassenenhoek, om samen zonder scherm te spelen</li>"),
    ("<li>In English and Dutch</li>", "<li>In het Nederlands en het Engels</li>"),
    ("Play Monko Focus</a>", "Speel Monko Focus</a>"),
    ('alt="Monko Focus on a phone: Bear, the buddy, stands at the start of a magic path of picture stops — a bee on a trail, bubbles, a leaf for a breathing break, hands, cups and a basket of stars — that leads to a castle. A green edge round the screen shows it is the child’s turn."',
     'alt="Monko Focus op een telefoon: Beer, het maatje, staat aan het begin van een toverpad met plaatjes — een bij op een spoor, bellen, een blaadje voor een adempauze, handen, bekers en een mandje met sterren — dat naar een kasteel leidt. Een groene rand om het scherm laat zien dat het kind aan de beurt is."'),

    # Monko Reads.
    ('alt="Monko Reads on a phone: Olli the owl stands at the start of a winding path through Zonneweide, the first world, with the first three games — Letterbos, Ballonnen and Rijmen. In a speech bubble, Olli says hello and invites the child onto the magic path."',
     'alt="Monko Reads op een telefoon: Olli de uil staat aan het begin van een kronkelpad door Zonneweide, de eerste wereld, met de eerste drie spelletjes — Letterbos, Ballonnen en Rijmen. In een tekstballon zegt Olli hallo en nodigt hij het kind uit om mee te gaan over het toverpad."'),
    ('<p class="sub">Letters &amp; words game · <span class="nowrap">Ages 5–8</span></p>',
     '<p class="sub">Letter- en woordspel · <span class="nowrap">5–8 jaar</span></p>'),
    ("A cheerful game full of letters, sounds and words, in Dutch or English. Olli the owl walks children along a magic path through four worlds of short games — find the letter, pop the right balloon, spot the rhyme, build the word — and reads the instructions aloud.",
     "Een vrolijk spel vol letters, klanken en woorden, in het Nederlands of het Engels. Olli de uil neemt kinderen mee over een toverpad door vier werelden met korte spelletjes — zoek de letter, laat de goede ballon knappen, vind het rijmwoord, bouw het woord — en leest de opdrachten voor."),
    ("<li>11 letter and word games, plus a movement break</li>", "<li>11 letter- en woordspelletjes, plus een beweegpauze</li>"),
    ("<li>Four worlds, three levels and 12 badges to earn</li>", "<li>Vier werelden, drie niveaus en 12 badges om te verdienen</li>"),
    ("<li>No timers to race against</li>", "<li>Geen tijdsdruk</li>"),
    ("<li>Bold text with wide letter spacing</li>", "<li>Vette letters met veel ruimte ertussen</li>"),
    ('<li>Sound groups always stay together, like <span lang="nl">“aa”</span> and <span lang="nl">“oe”</span> in Dutch or “sh” and “ee” in English</li>',
     '<li>Lange klanken en tweetekenklanken blijven altijd bij elkaar, zoals “aa” en “oe” in het Nederlands of <span lang="en">“sh”</span> en <span lang="en">“ee”</span> in het Engels</li>'),
    ("<li>Olli reads everything aloud in his own recorded voice, in English and in Dutch</li>",
     "<li>Olli leest alles voor met zijn eigen opgenomen stem, in het Nederlands en in het Engels</li>"),
    ("Play Monko Reads</a>", "Speel Monko Reads</a>"),

    # Monko Letters.
    ('<p class="sub">Handwriting game · ', '<p class="sub">Schrijfspel · '),
    ("A calm game for writing with a finger, a pen or a mouse. Stip the ladybird shows the way as children trace block letters, then joined letters, then little words — and every star they earn grows a flower in their garden.",
     "Een rustig spel om te schrijven met je vinger, een pen of een muis. Stip het lieveheersbeestje wijst de weg terwijl kinderen eerst blokletters natrekken, daarna schrijfletters en dan woordjes — en bij elke ster die ze verdienen, groeit er een bloem in hun tuin."),
    ("<li>All 26 lowercase letters, as block letters and joined letters, plus 15 short words</li>",
     "<li>Alle 26 kleine letters, als blokletter en als schrijfletter, plus 15 korte woordjes</li>"),
    ("<li>13 levels, each ending with a trophy and a prize — a hat or glasses for Stip, a new crayon or a friend for the garden</li>",
     "<li>13 levels, elk met een beker en een prijs aan het eind — een hoedje of een bril voor Stip, een nieuw krijtje of een vriendje voor de tuin</li>"),
    ("<li>Challenges like spotting the first letter of a picture, or uncovering a secret picture letter by letter</li>",
     "<li>Uitdagingen zoals de beginletter van een plaatje vinden, of letter voor letter een geheim plaatje tevoorschijn halen</li>"),
    ("<li>No timers, no lives and no red crosses — the ink only follows the right track</li>",
     "<li>Geen klok, geen levens en geen rode kruisjes — de inkt volgt alleen het goede spoor</li>"),
    ("<li>A wider or narrower track, calm mode, read-aloud instructions and a layout for left-handed children</li>",
     "<li>Een breder of smaller spoor, een rustige stand, opdrachten die worden voorgelezen en een indeling voor linkshandige kinderen</li>"),
    ("<li>In Dutch and English. The joined letters follow a general Dutch style, so a few may look a little different from the ones taught at school</li>",
     "<li>In het Nederlands en het Engels. De schrijfletters volgen een algemene Nederlandse stijl, dus een paar letters kunnen er net iets anders uitzien dan de letters die je kind op school leert</li>"),
    ("Play Monko Letters</a>", "Speel Monko Letters</a>"),
    ('alt="Monko Letters on a phone: the letter a, for “aap”, on a big writing pad. A finger has followed Stip the ladybird round the circle of the a in blue crayon, and Stip waits at the top of the down-stroke. Above the pad, Stip explains how to write the a."',
     'alt="Monko Letters op een telefoon: de letter a, van “aap”, op een groot schrijfvlak. Een vinger is Stip het lieveheersbeestje met blauw krijt gevolgd over het rondje van de a, en Stip wacht bovenaan het stokje. Boven het schrijfvlak legt Stip uit hoe je de a schrijft."'),

    # What beta means.
    ("<h3 id=\"beta-h\">What “beta” means</h3>", "<h3 id=\"beta-h\">Wat “bèta” betekent</h3>"),
    ("All three games are ready to play, but none of them is finished yet. You may spot rough edges, and we keep changing things as our children grow and as we hear from other families. Progress is saved only in the browser on your device, so it won’t follow you to another device or browser. The <a href=\"/privacy/\">privacy notice</a> has the details.",
     "Alle drie de spelletjes zijn klaar om te spelen, maar ze zijn nog niet af. Je komt misschien nog ruwe randjes tegen, en we blijven dingen aanpassen naarmate onze kinderen groter worden en we horen hoe het bij andere gezinnen gaat. Voortgang wordt alleen opgeslagen in de browser op je apparaat, dus die gaat niet mee naar een ander apparaat of een andere browser. In de <a href=\"/nl/privacy/\">privacyverklaring</a> lees je er meer over."),

    # Why we share it.
    ('<p class="rule">Why We Share It</p>', '<p class="rule">Waarom we het delen</p>'),
    ("<span>We made what we believe our children needed.</span> <span>We hope it’s useful for yours&nbsp;too.</span>",
     "<span>We hebben gemaakt wat onze kinderen volgens ons nodig hadden.</span> <span>We hopen dat het ook jouw kinderen van pas&nbsp;komt.</span>"),
    ("Every child is different, and what suits ours may not suit yours. So we’ve kept the games simple to try: open one, play for a few minutes and see how it goes.",
     "Elk kind is anders, en wat bij de onze past, past misschien niet bij de jouwe. Daarom zijn de spelletjes makkelijk uit te proberen: open er een, speel een paar minuten en kijk hoe het gaat."),
    ("<h3>Tried a game with your child?</h3>", "<h3>Een spelletje met je kind uitgeprobeerd?</h3>"),
    ("We’d love to hear what worked, what didn’t and what you’d like to see next. Questions and ideas are welcome too.",
     "We horen graag wat goed werkte, wat niet en wat je hierna nog zou willen zien. Vragen en ideeën zijn ook welkom."),

    # Footer.
    ('<nav class="footer-links" aria-label="Footer">', '<nav class="footer-links" aria-label="Voettekst">'),
    DISCLAIMER,
    ("Monkotorix is a project of Sofmon B.V. · KvK&nbsp;93115776 · The Netherlands<br>© 2026 Sofmon B.V. All rights reserved.",
     "Monkotorix is een project van Sofmon B.V. · KvK&nbsp;93115776 · Nederland<br>© 2026 Sofmon B.V. Alle rechten voorbehouden."),
]

PRIVACY = [
    # Page language, addresses and the language link.
    ('<html lang="en-GB">', '<html lang="nl">'),
    ('<link rel="canonical" href="https://monkotorix.com/privacy/">', '<link rel="canonical" href="https://monkotorix.com/nl/privacy/">'),
    ('<meta property="og:url" content="https://monkotorix.com/privacy/">', '<meta property="og:url" content="https://monkotorix.com/nl/privacy/">'),
    ('<meta property="og:image" content="https://monkotorix.com/assets/og.jpg">',
     '<meta property="og:image" content="https://monkotorix.com/assets/og-nl.jpg">'),
    ('<a class="back" href="/">', '<a class="back" href="/nl/">'),
    ('<a class="lang" href="/nl/privacy/" hreflang="nl" lang="nl">Nederlands</a>',
     '<a class="lang" href="/privacy/" hreflang="en" lang="en">English</a>'),

    # Head.
    ("<title>Privacy notice — Monkotorix</title>", "<title>Privacyverklaring — Monkotorix</title>"),
    ('<meta name="description" content="How the Monkotorix website and its beta games, Monko Focus, Monko Reads and Monko Letters, handle data: no accounts, no ads, no tracking, and progress kept only on your device.">',
     '<meta name="description" content="Hoe de website van Monkotorix en de bètaspelletjes Monko Focus, Monko Reads en Monko Letters met gegevens omgaan: geen accounts, geen reclame, geen tracking, en voortgang alleen op je eigen apparaat.">'),
    ('<meta property="og:title" content="Privacy notice — Monkotorix">', '<meta property="og:title" content="Privacyverklaring — Monkotorix">'),
    ('<meta property="og:description" content="No accounts, no ads, no tracking — progress stays on your device.">',
     '<meta property="og:description" content="Geen accounts, geen reclame, geen tracking — je voortgang blijft op je apparaat.">'),

    # Top.
    ('<p class="eyebrow">The website and the games</p>', '<p class="eyebrow">De website en de spelletjes</p>'),
    ("<h1>Privacy notice</h1>", "<h1>Privacyverklaring</h1>"),
    ('<p class="muted">Last updated: 9 November 2026</p>', '<p class="muted">Laatst bijgewerkt: 9 november 2026</p>'),
    ("<p><strong>In short:</strong> your progress is saved only in this browser on this device. We can’t see it, and it isn’t sent anywhere. There are no accounts, no ads and no tracking. You can delete everything at any time.</p>",
     "<p><strong>Kort gezegd:</strong> je voortgang wordt alleen opgeslagen in deze browser op dit apparaat. Wij kunnen die niet zien, en er wordt niets van verstuurd. Er zijn geen accounts, geen reclame en geen tracking. Je kunt alles op elk moment wissen.</p>"),

    # Who we are.
    ("<h2>Who we are</h2>", "<h2>Wie we zijn</h2>"),
    ("<p>Monkotorix is a project of Sofmon B.V., based in the Netherlands (KvK 93115776). If you have a question about privacy, email <a href=\"mailto:hello@monkotorix.com\">hello@monkotorix.com</a>.</p>",
     "<p>Monkotorix is een project van Sofmon B.V., gevestigd in Nederland (KvK 93115776). Heb je een vraag over privacy, mail dan naar <a href=\"mailto:hello@monkotorix.com\">hello@monkotorix.com</a>.</p>"),

    # This website.
    ("<h2>This website</h2>", "<h2>Deze website</h2>"),
    ("<p>The website at monkotorix.com is a set of static pages. Its fonts, images and code are all served from this website itself, so your browser doesn’t load anything from other websites while you read it. We don’t use cookies, analytics or advertising.</p>",
     "<p>De website op monkotorix.com bestaat uit statische pagina’s. De lettertypen, afbeeldingen en code komen allemaal van deze website zelf, dus je browser laadt niets van andere websites terwijl je leest. We gebruiken geen cookies, analysetools of reclame.</p>"),
    ("<p>If you use the light/dark switch, your choice is remembered in your browser’s local storage under the name <code>monkotorix-theme</code>. It never leaves your device.</p>",
     "<p>Gebruik je de knop voor licht en donker, dan wordt je keuze onthouden in de lokale opslag van je browser, onder de naam <code>monkotorix-theme</code>. Die keuze verlaat je apparaat nooit.</p>"),
    ("<p>The website and the games are hosted on GitHub Pages, a service of GitHub, Inc. in the United States. Like any web host, GitHub receives the technical information needed to deliver the pages to you, such as your IP address and browser type. GitHub logs visitors’ IP addresses and stores them for security purposes. That information may be processed in the United States; GitHub explains how it handles it in its <a href=\"https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement\" rel=\"noopener\">privacy statement</a>. We rely on our legitimate interest in delivering a safe, working website. We don’t receive or use this information to track or profile visitors.</p>",
     "<p>De website en de spelletjes worden gehost op GitHub Pages, een dienst van GitHub, Inc. in de Verenigde Staten. Zoals elke webhost ontvangt GitHub de technische gegevens die nodig zijn om de pagina’s bij je af te leveren, zoals je IP-adres en het soort browser. GitHub legt de IP-adressen van bezoekers vast en bewaart ze voor de beveiliging. Die gegevens kunnen in de Verenigde Staten worden verwerkt; hoe GitHub ermee omgaat, staat in de <a href=\"https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement\" rel=\"noopener\" hreflang=\"en\">privacyverklaring van GitHub</a> (in het Engels). Wij baseren ons daarbij op ons gerechtvaardigd belang om een veilige, goed werkende website aan te bieden. Wij ontvangen of gebruiken deze gegevens niet om bezoekers te volgen of te profileren.</p>"),
    ("<p>If you email us, we use your message and email address only to reply to you, and we delete them when they’re no longer needed for that.</p>",
     "<p>Als je ons mailt, gebruiken we je bericht en e-mailadres alleen om je te antwoorden, en we verwijderen ze zodra ze daarvoor niet meer nodig zijn.</p>"),

    # The beta games.
    ("<h2>The beta games</h2>", "<h2>De bètaspelletjes</h2>"),
    ("<p>All three games run entirely in your browser. They don’t have accounts and don’t send what a child does anywhere — not to us, and not to anyone else.</p>",
     "<p>Alle drie de spelletjes draaien helemaal in je browser. Ze hebben geen accounts en sturen niets van wat een kind doet ergens naartoe — niet naar ons en ook niet naar iemand anders.</p>"),

    ("<p>Monko Focus stores its settings and progress in your browser’s local storage under <code>coordination-games:settings</code>. This includes the language and age band, the grown-up’s settings (sound, read-aloud and how much the buddy talks, calm mode, bigger targets, words under pictures, left-handed, the wait-your-turn light, more challenge, speed, session length and which games can be played), stars, stickers, progress along the magic path, and when each game was last played. Under <code>monko-focus:heard</code> it also remembers which instructions the child has already heard before pressing Go or “My turn!”, so that next time those buttons work straight away.</p>",
     "<p>Monko Focus bewaart zijn instellingen en voortgang in de lokale opslag van je browser, onder <code>coordination-games:settings</code>. Daarbij horen de taal en de leeftijdsgroep, de instellingen van de volwassene (geluid, voorlezen en hoeveel het maatje praat, rustige stand, grotere doelen, woorden onder plaatjes, linkshandig, het beurtlicht, meer uitdaging, tempo, speeltijd en welke spelletjes gespeeld kunnen worden), sterren, stickers, de voortgang op het toverpad en wanneer elk spelletje voor het laatst is gespeeld. Onder <code>monko-focus:heard</code> onthoudt het spel ook welke opdrachten het kind al had gehoord voordat het op Start of “Mijn beurt!” drukte, zodat die knoppen de volgende keer meteen werken.</p>"),
    ("<p>If a grown-up sets up a profile, it can also hold a first name, an age, an optional gender, the “What fits” and “Play most” choices, and a favourite sticker theme. The buddy a child picks is saved too, with or without a profile. All of this is used only to fit the games to the child, and it stays on the device. You can delete it at any time with <strong>Remove profile</strong> on the <strong>Child</strong> page of the game’s grown-up corner. This also clears the stars, the sticker book and the place on the magic path, forgets which instructions were heard, and puts the settings back to how they started (the language stays).</p>",
     "<p>Maakt een volwassene een profiel aan, dan kunnen daar ook een voornaam, een leeftijd, eventueel een geslacht, de keuzes bij “Wat past” en “Het meest spelen” en een favoriet stickerthema in staan. Het maatje dat een kind kiest, wordt ook bewaard, met of zonder profiel. Dit alles wordt alleen gebruikt om de spelletjes af te stemmen op het kind, en het blijft op het apparaat. Je kunt het op elk moment wissen met <strong>Profiel verwijderen</strong> op de pagina <strong>Kind</strong> in de volwassenenhoek van het spel. Daarmee worden ook de sterren, het stickerboek en de plek op het toverpad gewist, vergeet het spel welke opdrachten al gehoord zijn en gaan de instellingen terug naar de beginstand (de taal blijft staan).</p>"),

    ("<p>Monko Reads stores its settings and progress in your browser’s local storage under <code>monkoreads</code>: the language of the game and of the grown-up pages, voice and sound settings (the chosen voice, speed and pitch, and how much Olli talks), the grown-up’s other settings (calm mode, game speed, rests, left-handed, play time, sitting still, and which games and worlds are open), the level, stars, opened treasure chests, stickers and when each game was last played. If a grown-up fills them in, it also keeps the child’s first name and age. Progress saved before the game was renamed (it used to be called <span lang=\"nl\">Lezen met Olli</span>) sits under <code>lezen-met-olli</code>; the first time the game opens, it moves that progress to the new name and removes the old entry.</p>",
     "<p>Monko Reads bewaart zijn instellingen en voortgang in de lokale opslag van je browser, onder <code>monkoreads</code>: de taal van het spel en van de pagina’s voor volwassenen, de instellingen voor stem en geluid (de gekozen stem, snelheid en toonhoogte, en hoeveel Olli praat), de andere instellingen van de volwassene (rustige stand, speltempo, rustpauzes, linkshandig, speeltijd, stilzitten, en welke spelletjes en werelden open zijn), het niveau, de sterren, de geopende schatkisten, de stickers en wanneer elk spelletje voor het laatst is gespeeld. Als een volwassene de voornaam en leeftijd van het kind invult, bewaart het spel die ook. Voortgang van vóór de naamswijziging (het spel heette eerst Lezen met Olli) staat onder <code>lezen-met-olli</code>; de eerste keer dat je het spel opent, zet het die voortgang over naar de nieuwe naam en verwijdert het wat er onder de oude naam stond.</p>"),
    ("<p>In the game’s grown-up corner, <strong>Start over</strong> (<span lang=\"nl\">Opnieuw beginnen</span>) on the <strong>Progress</strong> page removes the stars, stickers and badges, and <strong>Remove profile</strong> (<span lang=\"nl\">Profiel verwijderen</span>) on the <strong>Child</strong> page also removes the name and age and puts the settings back to how they started (the languages stay).</p>",
     "<p>In de volwassenenhoek van het spel wis je met <strong>Opnieuw beginnen</strong> op de pagina <strong>Voortgang</strong> de sterren, stickers en badges. Met <strong>Profiel verwijderen</strong> op de pagina <strong>Kind</strong> wis je ook de naam en leeftijd, en gaan de instellingen terug naar de beginstand (de talen blijven staan).</p>"),

    ("<p>Monko Letters stores its settings and progress in your browser’s local storage under <code>monkoletters</code>: the language of the game and of the grown-up pages, the grown-up’s settings (writing hand, track width, calm mode, voice and how much Stip talks, crayon colour, the letters used for words, play time and what the child can play), the stars for each letter and word, the levels and challenges finished, today’s challenge, the prizes won and what Stip is wearing. If a grown-up fills them in, it also keeps the child’s first name and age; the name is shown on screen but never spoken. While the child plays, the play time so far is kept in session storage under <code>monkoletters:speeltijd</code>, which the browser forgets when the tab is closed.</p>",
     "<p>Monko Letters bewaart zijn instellingen en voortgang in de lokale opslag van je browser, onder <code>monkoletters</code>: de taal van het spel en van de pagina’s voor volwassenen, de instellingen van de volwassene (schrijfhand, breedte van het spoor, rustige stand, stem en hoeveel Stip praat, kleur van het krijtje, in welke letters de woordjes worden geschreven, speeltijd en wat het kind mag spelen), de sterren per letter en woord, de afgeronde levels en uitdagingen, de uitdaging van vandaag, de gewonnen prijzen en wat Stip aanheeft. Als een volwassene de voornaam en leeftijd van het kind invult, bewaart het spel die ook; de naam staat op het scherm, maar wordt nooit uitgesproken. Tijdens het spelen wordt de speeltijd tot dan toe bijgehouden in de sessieopslag, onder <code>monkoletters:speeltijd</code>; die vergeet de browser zodra het tabblad wordt gesloten.</p>"),
    ("<p>You can delete it with <strong>Remove profile</strong> (<span lang=\"nl\">Profiel verwijderen</span>) on the <strong>Child</strong> page of the game’s grown-up corner. This removes the name and age, the stars, trophies and prizes, and puts the settings back to how they started (the languages stay).</p>",
     "<p>Je kunt dit wissen met <strong>Profiel verwijderen</strong> op de pagina <strong>Kind</strong> in de volwassenenhoek van het spel. Daarmee verdwijnen de naam en leeftijd, de sterren, bekers en prijzen, en gaan de instellingen terug naar de beginstand (de talen blijven staan).</p>"),

    # Read-aloud voices.
    ("<h3>Read-aloud voices</h3>", "<h3>Voorleesstemmen</h3>"),
    ("<p>All three games can read instructions aloud with the speech voices your browser offers. Some of those voices are online voices — for example Microsoft Edge’s “Online (Natural)” voices and Chrome’s voices named “Google …”. When one of those is used, the browser sends the sentence being read to its maker’s speech service. Only the game’s own sentences and words are sent this way, never anything about the child. This is part of how the browser works, not something the games do.</p>",
     "<p>Alle drie de spelletjes kunnen opdrachten voorlezen met de spraakstemmen die je browser aanbiedt. Sommige daarvan zijn online stemmen — bijvoorbeeld de <span lang=\"en\">“Online (Natural)”</span>-stemmen van Microsoft Edge en de stemmen in Chrome waarvan de naam met “Google” begint. Wordt zo’n stem gebruikt, dan stuurt de browser de zin die wordt voorgelezen naar de spraakdienst van de maker van die stem. Op die manier worden alleen de eigen zinnen en woorden van het spel verstuurd, nooit iets over het kind. Dit hoort bij hoe de browser werkt; de spelletjes doen dit niet zelf.</p>"),
    ("<p>Monko Reads plays its own recordings of Olli’s lines in English and Dutch, which come from this website too. Only a line it has no recording of, or one that can’t load in time, is read by a device voice: it picks a voice that runs on the device when there is one, and only uses an online voice when the device has none of its own for the language. An online voice never hears the child’s name: Olli then says the line without it. Online voices are marked “(online)” in the voice list under <strong>Sound &amp; voice</strong> (<span lang=\"nl\">Geluid en stem</span>) in the grown-up corner. To be sure nothing is sent, choose a voice without that mark there, or switch off <strong>Olli talks</strong> (<span lang=\"nl\">Olli praat</span>).</p>",
     "<p>Monko Reads speelt eigen opnames af van wat Olli zegt, in het Nederlands en het Engels; ook die komen van deze website. Alleen een zin zonder opname, of een zin waarvan de opname niet op tijd laadt, wordt voorgelezen door een stem van het apparaat: het spel kiest een stem die op het apparaat zelf draait als die er is, en gebruikt alleen een online stem als het apparaat zelf geen stem voor de taal heeft. Een online stem krijgt de naam van het kind nooit te horen: Olli zegt de zin dan zonder naam. In de stemmenlijst bij <strong>Geluid en stem</strong> in de volwassenenhoek staat “(online)” achter de naam van online stemmen. Wil je zeker weten dat er niets wordt verstuurd, kies daar dan een stem zonder die vermelding, of zet <strong>Olli praat</strong> uit.</p>"),
    ("<p>Monko Focus plays its own recordings of the buddy’s lines. They come from this website like the rest of the game, so nothing is sent for them. Only a line it has no recording of, or one that can’t load in time, is read by a device voice: Monko Focus picks one for the chosen language by itself, preferring voices that run on the device or sound natural, and has no list of voices to choose from. To be sure nothing is sent, switch off <strong>Voice</strong> under <strong>Sound &amp; voice</strong> in its grown-up corner.</p>",
     "<p>Monko Focus speelt eigen opnames af van wat het maatje zegt. Die komen net als de rest van het spel van deze website, dus daarvoor wordt niets verstuurd. Alleen een zin zonder opname, of een zin waarvan de opname niet op tijd laadt, wordt voorgelezen door een stem van het apparaat: Monko Focus kiest die zelf voor de gekozen taal, met een voorkeur voor stemmen die op het apparaat draaien of natuurlijk klinken, en heeft geen lijst om uit te kiezen. Wil je zeker weten dat er niets wordt verstuurd, zet dan <strong>Stem</strong> uit bij <strong>Geluid en stem</strong> in de volwassenenhoek.</p>"),
    ("<p>Monko Letters plays its own recordings of Stip’s lines, which come from this website too. Only a line it has no recording of, or one that can’t load in time, is read by a device voice: it takes the first Dutch voice the browser offers (in English, a British English one if there is one), which can be an online voice, and has no list of voices to choose from. To be sure nothing is sent, switch off <strong>Voice</strong> (<span lang=\"nl\">Stem</span>) under <strong>Sound &amp; voice</strong> in its grown-up corner, and don’t tap Stip’s message or <strong>Read aloud</strong> (<span lang=\"nl\">Lees voor</span>).</p>",
     "<p>Monko Letters speelt eigen opnames af van wat Stip zegt; ook die komen van deze website. Alleen een zin zonder opname, of een zin waarvan de opname niet op tijd laadt, wordt voorgelezen door een stem van het apparaat: het spel neemt de eerste Nederlandse stem die de browser aanbiedt (in het Engels een Brits-Engelse stem als die er is), en dat kan een online stem zijn. Er is geen lijst om uit te kiezen. Wil je zeker weten dat er niets wordt verstuurd, zet dan <strong>Stem</strong> uit bij <strong>Geluid en stem</strong> in de volwassenenhoek, en tik niet op het berichtje van Stip of op <strong>Lees voor</strong>.</p>"),

    # Deleting everything, rights, children, changes.
    ("<h2>Deleting everything</h2>", "<h2>Alles wissen</h2>"),
    ("<p>Because everything is kept on your device, you are in control. Use the reset options in each game, or clear the site data for monkotorix.com in your browser’s settings to remove all stored progress, profiles and settings at once. Private or incognito windows forget everything when they close.</p>",
     "<p>Omdat alles op je apparaat blijft, heb je het zelf in de hand. Gebruik de wisknoppen in elk spel, of wis de websitegegevens van monkotorix.com in de instellingen van je browser om alle opgeslagen voortgang, profielen en instellingen in één keer te verwijderen. Privé- en incognitovensters vergeten alles zodra je ze sluit.</p>"),
    ("<p>On a shared device — a family tablet or a classroom computer — everyone using the same browser sees the same progress and profile.</p>",
     "<p>Op een gedeeld apparaat — een tablet van het hele gezin of een computer in de klas — ziet iedereen die dezelfde browser gebruikt dezelfde voortgang en hetzelfde profiel.</p>"),
    ("<h2>Your rights</h2>", "<h2>Je rechten</h2>"),
    ("<p>You can ask us what personal data we hold about you (normally none, apart from emails you sent us), and ask us to correct or delete it, or object to how we use it. Email <a href=\"mailto:hello@monkotorix.com\">hello@monkotorix.com</a>. If you’re not happy with our answer, you can complain to the Dutch Data Protection Authority, the <a href=\"https://autoriteitpersoonsgegevens.nl\" rel=\"noopener\" lang=\"nl\">Autoriteit Persoonsgegevens</a>.</p>",
     "<p>Je kunt ons vragen welke persoonsgegevens we van je hebben (normaal gesproken geen, behalve e-mails die je ons hebt gestuurd), en ons vragen die te corrigeren of te verwijderen, of bezwaar maken tegen hoe we ze gebruiken. Mail daarvoor naar <a href=\"mailto:hello@monkotorix.com\">hello@monkotorix.com</a>. Ben je niet tevreden met ons antwoord, dan kun je een klacht indienen bij de <a href=\"https://autoriteitpersoonsgegevens.nl\" rel=\"noopener\">Autoriteit Persoonsgegevens</a>.</p>"),
    ("<h2>Children</h2>", "<h2>Kinderen</h2>"),
    ("<p>Monkotorix is made for children to use with the grown-ups who support them. We don’t collect or receive personal information from children through the website or the games. The optional profiles in all three games are filled in by a grown-up and never leave the device.</p>",
     "<p>Monkotorix is gemaakt voor kinderen, om samen te gebruiken met de volwassenen die hen begeleiden. We verzamelen of ontvangen via de website of de spelletjes geen persoonsgegevens van kinderen. De profielen in alle drie de spelletjes zijn niet verplicht, worden ingevuld door een volwassene en verlaten het apparaat nooit.</p>"),
    ("<h2>Changes</h2>", "<h2>Wijzigingen</h2>"),
    ("<p>If the games ever start to work differently — for example, if we add optional accounts or progress sharing — we will update this notice first and say so clearly on the website.</p>",
     "<p>Als de spelletjes ooit anders gaan werken — bijvoorbeeld als we optionele accounts of het delen van voortgang toevoegen — passen we eerst deze verklaring aan en melden we dat duidelijk op de website.</p>"),

    # Footer.
    DISCLAIMER,
    ('<p><a href="/">Back to Monkotorix</a> · ', '<p><a href="/nl/">Terug naar Monkotorix</a> · '),
    ("<p>© 2026 Sofmon B.V. All rights reserved.</p>", "<p>© 2026 Sofmon B.V. Alle rechten voorbehouden.</p>"),
]

PAGES = [
    ("index.html", "nl/index.html", HOME),
    ("privacy/index.html", "nl/privacy/index.html", PRIVACY),
]


def translate(src: str, pairs) -> str:
    page = (SITE / src).read_text(encoding="utf-8")
    problems = []
    for pair in pairs:
        en, nl = pair[0], pair[1]
        want = pair[2] if len(pair) > 2 else 1
        found = page.count(en)
        if found != want:
            problems.append(f"  {src}: expected {want}×, found {found}×: {en[:110]}")
            continue
        page = page.replace(en, nl)
    if problems:
        sys.exit("English text changed; update tools/make_dutch.py:\n" + "\n".join(problems))
    return page


def main() -> None:
    for src, dst, pairs in PAGES:
        out = translate(src, pairs)
        # Every page-local link must stay on the Dutch side (games and assets are shared).
        stray = re.findall(r'href="/(?:privacy/)?"(?![^>]*hreflang="en")', out)
        if stray:
            sys.exit(f"{dst}: links still point at the English pages: {stray}")
        path = SITE / dst
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
        print(f"wrote site/{dst}")


if __name__ == "__main__":
    main()
