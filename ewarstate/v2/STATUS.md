# eWarState V2 — završena ponovna izrada

171 pojedinačno izrađen osnovni model, 918 PNG varijanti. Produkcioni folder je `assets v2/` u korenu repozitorijuma, sa rasporedom kategorija / model / vrsta_model_boja.png.

Svaki osnovni model pregledan je na originalnoj glavi. Korigovani su skriveni zadnji mostovi i povratni pregibi, neželjeno nacrtana lica, kaiševi preko lica, otvori maski i fantomki, položaj slušalica i celog mikrofona. Uniforme su novi samostalni krojevi sa prirodnim ramenima, bez izdvajanja pravougaonika iz atlasa i bez spajanja sa pancirima.

Boje prate maske materijala. Maska prvog šlema prati povezanu površinu školjke; svetla, medicinski krst i reflektujuće trake imaju zasebno očuvane materijale. Prvi šlem ima svih 216 kamuflaža i 24 obične boje.

Tehnički provereno: 918 jedinstvenih RGBA PNG fajlova, 1024 × 1024; alfa kanal ostaje jednak registrovanoj osnovi; ispravni ID-jevi i traženi folderi; svih 216 tekstura povezano sa prvim modelom; izvorne i registrovane SHA256 vrednosti aktuelne. Lokalni HTTP preglednik učitao je svih 24 pripremljenih kombinacija bez JavaScript grešaka.

Opseg vizuelne provere: svih 171 osnova na istoj glavi, materijali kroz jednobojne i kamuflažne preglede, svih 240 varijanti prvog šlema na preglednim tablama i 24 konkretne kombinacije. Nije potvrđena svaka moguća kombinacija svih predmeta. Pravila i primeri su u `assets v2/compatibility.json` i `examples.json`.

`models/` čuva registrovane osnove i maske materijala; `sources/` pojedinačne završne izvorne slike; `jobs.json` istorijske promptove; `registration.json` recept i trag provere. Radni keš i neuspešni pokušaji nisu deo produkcione kolekcije. Originalni korisnički paketi i samostalne kamuflažne teksture ostaju sačuvani.
