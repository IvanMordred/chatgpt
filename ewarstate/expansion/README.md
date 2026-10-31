# eWarState — odela, panciri, maske i detalji

120 novih modela / 416 pojedinacnih varijanti:
- 30 uniformi i odela BEZ pancira: 146 varijanti.
- 30 zasebnih prsluka, pancira i nosaca opreme: 120 varijanti.
- 30 predmeta za lice: 6 polumaski, 4 semage/marame/sala, 10 balaklava i 10 respiratora/gas maski: 120 varijanti.
- 10 dodataka: naocare, povez, dve slusalice sa mikrofonima, cigara, cigareta, tri oznake cina.
- 5 boja za lice i 5 oziljaka.
- 10 pozadina.

## Upotreba

Svaki predmet je zaseban RGBA PNG 1024x1024 na x=0,y=0 bez skaliranja. Naziv je vrsta_model_boja. Boja 1 je originalna neutralna/prirodna varijanta. Ostale boje navedene su u manifest.json.

Redosled: pozadina → glava → uniforma → pancir → boje/oziljci → oprema za lice → naocare/slusalice → cigara/cigareta → oznake cina. Ako se koristi pokrivalo za glavu sa zadnjim delom, taj deo ide iza glave. Puna maska i balaklava zauzimaju isti slot; ne slagati ih automatski. Boje za lice staviti PRE maski i naocara. Oznake cina su zasebni prednji slojevi na predvidjenom mestu na grudima.

Odela i panciri nisu spojeni. Ne dodavati staru uniformu ispod nove pri proveri kroja, jer stari rukavi mogu proviriti. Panciri su demonstrirani preko originalne odvojene uniforme, a 12 kombinacija preko novih odela je u qa/combinations_12.jpg.

Zadnje povrsine kragni, traka i otvora koje su skrivene glavom uklonjene su iz prednjeg sloja. Nisu crtane niti izvezene nevidljive zadnje povrsine. Otvori za vrat/lice/ruke su alfa-providni. Neki prednji delovi (kragne, salovi) namerno prekrivaju donji vrat.

## Provera i ogranicenja

Svih 120 osnovnih modela prikazano je na prilozenom master komandiru. Ispravljene su zadnje ivice kragni i registracija tri balaklave. Pregledi varijanti predstavljaju stvarne alfa kompozite. QA pozadina na pregledima nije deo PNG opreme.

Nisu pregledane sve moguce kombinacije. Visoke kragne, krupne semage, teski oklopi, pune maske, slusalice i pokrivala za glavu mogu zahtevati zabrane kombinovanja ili dalju rucnu doradu. Nema univerzalne kompatibilnosti sa buducim licima.

Osnove su generisane na 12 koncept tabli, izdvojene, registrovane na master, a odabrane boje i kamuflaze primenjene uz sacuvane senke. Izvorna rezolucija po predmetu manja je od izvoza 1024x1024; povecanje ne predstavlja novi izvorni detalj. Pozadine su centralno kropovane na kvadrat, ne razvucene.

assets/: PNG fajlovi. models/: radne neutralne baze. sources/: izvorne table. previews/: svaki model i njegove boje. qa/: provere uklapanja, kombinacije i izvestaj. manifest.json: svi ID-ovi, slotovi, boje i provere. models.json: izvor i registracija.

Ponovno generisanje iz klona: Python + Pillow + NumPy + SciPy; python ewarstate/scripts/build_expansion.py pa python ewarstate/scripts/finalize_expansion.py.

ZIP paketi sadrze predmete i preglede, bez radnih baza i izvornih tabli, koje su dostupne u Git repozitorijumu.
