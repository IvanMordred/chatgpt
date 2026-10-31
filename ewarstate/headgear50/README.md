# eWarState: 50 novih modela pokrivala za glavu

50 razlicitih osnovnih modela i 262 transparentnih PNG varijanti. Platno 1024x1024, x=0,y=0 bez skaliranja na prilozenoj osnovnoj glavi. Za modele sa rear_file OBAVEZAN redosled: pozadina, rear_file (iza glave), glava, uniforma, pancir, file (prednji sloj). assets/ sadrzi prednje slojeve, rear_assets/ zadnje slojeve. Ime oba sloja je isti ID u razlicitim direktorijumima. Ne koristiti base.png kao gotov prednji sloj.

Oprema je izdvojena iz pet generisanih koncept atlasa i registrovana po ceonoj ivici. Pregledi su stvarni alfa kompoziti sa korisnickim master slojevima.

Modeli: cap_1–cap_13, helmet_2–helmet_21, beret_1–beret_4, hat_1–hat_7, hood_1–hood_6. Raniji helmet_1 nije menjan.

Boje su birane po nameni: kamuflaze za terenske modele, obicne boje za beretke i vecinu specijalistickih kaciga, signalna narandzasta/zuta za spasioce. Baze i maske za bojenje zadrzane su u models/. Za kapuljace i pustinjski vratni zastitnik zadnji delovi ispod linije obrva razdvojeni su iza glave. Tamni detalji i hromatski detalji (npr. bronzane oznake i svetla) uglavnom su izuzeti iz maske za bojenje; maske su pocetna priprema za dalju rucnu doradu, ne zasebni fizicki materijali.

Ne kombinovati sa drugim kapama/slemovima. Sakriti kosu koja izlazi kroz pokrivalo. Kompatibilnost sa svakom postojecom maskom, slusalicama ili bradom nije garantovana. Zatvorene kacige namerno prekrivaju lice; providni vizir i tesne kapuljace mogu zahtevati dodatnu rucnu doradu. Nema univerzalne tvrdnje o uklapanju.

assets/: zasebni PNG predmeti tip_model_boja. manifest.json: svi ID-ovi, boje i izvori tekstura. models.json: dizajni i precizni parametri registracije. previews/: 50 pregleda varijanti i zajednicka tabla. sources/: originalne koncept table, nisu slojevi za direktno nosenje.

Reprodukcija: python ewarstate/scripts/build_headgear50.py (Pillow, NumPy, SciPy). Nazivi boja su stabilni po modelu.


## Provera slojeva

Svih 50 baznih modela pregledano je na master komandiru. QA table imaju kontrastnu pozadinu radi otkrivanja ostataka; ta pozadina NIJE deo PNG predmeta. Za hood_1–hood_6 i helmet_7 koristiti oba sloja iz manifesta. Razdvajanje alfa kanala je provereno za sve njihove boje.

ZIP sadrzi gotove prednje i zadnje slojeve, metapodatke i preglede. Radni bazni modeli, maske bojenja i originalne koncept table nalaze se zasebno u Git repozitorijumu. Za ponovno generisanje skriptu pokrenuti iz potpunog klona repozitorijuma.
