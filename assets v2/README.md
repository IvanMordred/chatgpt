# eWarState — oprema V2

171 ponovo izrađen osnovni model, 918 varijanti. PNG slojevi su RGBA, 1024 × 1024, poravnati na priloženu osnovnu glavu. Nazivi modela i boja ostaju stabilni.

## Folderi

```text
assets v2/
  helmets/
    helmet 1/
      helmet_1_1.png
      helmet_1_2.png
      …
      helmet_1_240.png
    helmet 2/
      helmet_2_1.png
      …
  uniforms/
    uniform 1/
      uniform_1_1.png
      …
  vests/
    vest 1/
      vest_1_1.png
      …
```

Ista struktura važi za sve kategorije: kategorija → vrsta i broj modela → `vrsta_model_boja.png`. Broj boje počinje od 1 za svaki model. `manifest.json` povezuje svaki broj sa bojom, teksturom i SHA256 proverom; putanje u manifestu su relativne korenu Git repozitorijuma.

`helmet_1_1`–`helmet_1_216` koriste svih 216 postojećih kamuflaža. `helmet_1_217`–`helmet_1_240` su 24 obične boje. Kamuflaže obuhvataju šest kategorija, po šest paleta i šest dezena; digitalni dezen je u svakoj kategoriji. Premium: Zlatni pepeo, Krvavi mesec, Kobalt, Ametist, Patina i Obsidijan.

## Pregled i preuzimanje

- [24 složena komandira — prva tabla](previews/commanders_1.jpg)
- [24 složena komandira — druga tabla](previews/commanders_2.jpg)
- [Svi modeli po kategorijama na komandiru](previews/overviews)
- [Svaki model i njegove boje](previews/models)
- [Sve kamuflaže i obične boje prvog šlema](previews/helmet%201)
- [ZIP paketi manji od 20 MiB](../ewarstate/downloads/v2/README.md)
- [Manifest svih 918 predmeta](manifest.json)
- [Tehnička provera](validation.json)

Za interaktivan pregled preuzmi ovu celu strukturu i otvori `preview.html` u pregledaču. Radi lokalno, bez servera i interneta. Na GitHubu se HTML prikazuje kao kod; preglednik pokreni iz preuzetog foldera. Dugme „Nasumičan komandir” koristi pripremljene kombinacije uz promenu njihovih boja. Oznake ispod izbora otvaraju samostalni PNG sloj.

## Slaganje slojeva

Svi predmeti se dodaju na x=0, y=0 bez dodatnog skaliranja. Redosled: pozadina → osnovna glava → boja za lice / ožiljak → odelo → pancir → čin → maska / marama → pokrivalo za glavu → naočare → slušalice → cigara / cigareta.

Odela i panciri su potpuno odvojeni. Donje ivice odela i pancira prate donju ivicu portreta; ovo su slojevi za bistu komandira. Ostala oprema ima slobodne margine. Fantomke i maske imaju providne otvore; zatamnjena stakla su deo dizajna gde postoje. Skriveni zadnji mostovi, povratni pregibi i zadnje trake nisu zasebno nacrtani preko glave. Slušalice imaju prednje ušne školjke i ceo mikrofon, bez dodatnog obruča preko šlema.

Svih 171 osnovnih modela pregledano je na istoj glavi. Provereni su materijali kroz jednobojne i kamuflažne primere i 24 navedene kombinacije. To nije potvrda svake moguće kombinacije opreme: zatvorena kaciga zamenjuje masku i naočare; kacige sa ugrađenim štitnicima za uši ne treba spajati sa drugim slušalicama. Videti `compatibility.json` i konkretne recepte u `examples.json`.

## Sadržaj

| Vrsta | Osnovni modeli | PNG varijante |
|---|---:|---:|
| background | 10 | 10 |
| balaclava | 10 | 40 |
| beret | 4 | 20 |
| cap | 13 | 70 |
| cigar | 1 | 1 |
| cigarette | 1 | 1 |
| eyepatch | 1 | 1 |
| facepaint | 5 | 5 |
| gasmask | 10 | 40 |
| glasses | 2 | 2 |
| hat | 7 | 36 |
| headset | 2 | 2 |
| helmet | 21 | 350 |
| hood | 6 | 26 |
| mask | 6 | 24 |
| rank | 3 | 3 |
| scar | 5 | 5 |
| scarf | 4 | 16 |
| uniform | 30 | 146 |
| vest | 30 | 120 |

## Izvori i ponovni izvoz

Registrovane osnove i maske materijala nalaze se u `ewarstate/v2/models/`, pojedinačni izvorni nacrti u `ewarstate/v2/sources/`, a geometrija i provere u `ewarstate/v2/registration.json`. To su radni izvori; predmeti za korišćenje su PNG fajlovi u `assets v2/`.

Ponovni izvoz boja: `python ewarstate/v2/build_variants.py`. Potrebni su Python, Pillow, NumPy i SciPy. Skripta koristi sačuvane registrovane osnove i postojeće teksture; nije potrebno novo generisanje slika. `validate_pack.py` proverava format, alfa kanal, nazive, putanje, jedinstvenost i veze sa izvorima.

Originalni korisnički ZIP paketi i postojeće kamuflažne teksture su sačuvani. Ranije generisane serije izvan `assets v2/` su prethodne verzije, zamenjene ovom kolekcijom.
