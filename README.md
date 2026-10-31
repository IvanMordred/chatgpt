# eWarState — materijali za dizajn

Komandiri PMC jedinica: originalni slojevi, sastavljeni primeri, koncepti opreme i kamuflažne teksture.

## 50 novih kapa, slemova i kaciga

**50 novih osnovnih modela, 262 varijante boja i kamuflaza.** Svi su prikazani na osnovnom komandiru. Za 6 kapuljaca i pustinjski slem prednji i zadnji delovi su razdvojeni: pozadina → zadnji deo → komandir → prednji deo. U manifestu su `file` i opcioni `rear_file`.

- [Preuzmi 50 novih modela i sve boje — ZIP](ewarstate/downloads/ewarstate_50_novih_modela.zip)
- [Pregled svih 50 modela na komandiru](ewarstate/headgear50/previews/all_50_models.jpg)
- [Provera uklapanja svih modela po grupama](ewarstate/headgear50/qa)
- [Boje i kamuflaze svakog modela](ewarstate/headgear50/previews)
- [Uputstvo i redosled slojeva](ewarstate/headgear50/README.md)

## Šlemovi — 240 varijanti

Jedan model, 216 kamuflaža i 24 obične boje. Transparentni PNG slojevi 1024 × 1024, poravnati na osnovnog komandira.

- [Preuzmi 240 šlemova — ZIP](ewarstate/downloads/ewarstate_240_slemova.zip)
- [Pregled 12 primera na komandiru](ewarstate/helmets/previews/selection_12.jpg)
- [Sve pregledne table](ewarstate/helmets/previews)
- [Pojedinačni PNG slojevi](ewarstate/helmets/assets)
- [Detalji uklapanja i izvori](ewarstate/helmets/README.md)

## Preuzimanje

Otvorite link, pa **Download raw file**. Za ceo repozitorijum koristite **Code → Download ZIP**.

- [216 kamuflažnih tekstura — ZIP](ewarstate/downloads/ewarstate_216_kamuflaza.zip)
- [150 predloga opreme — ZIP](ewarstate/downloads/ewarstate_150_predloga.zip)
- [12 komandira — ZIP](ewarstate/commanders/komandiri_12.zip)
- [Originalni korisnički paketi](ewarstate/source-packs)

## Pregledi

- [12 sastavljenih komandira](ewarstate/commanders/komandiri_pregled.jpg)
- [50 maski i fantomki](ewarstate/concepts/masks_50.png)
- [50 dodataka za glavu](ewarstate/concepts/headgear_50.png)
- [50 dodataka za torzo](ewarstate/concepts/torso_50.png)
- [Prvih 16 dodataka za glavu](ewarstate/concepts/headgear_initial_16.png)
- [Prvih 16 dodataka za torzo](ewarstate/concepts/torso_initial_16.png)
- [Palete sa HEX bojama](ewarstate/camouflage/previews/palete_hex.png)
- [Table svih kategorija kamuflaže](ewarstate/camouflage/previews)

## Sadržaj i ograničenja

Kamuflaža: 6 kategorija × 6 paleta × 6 dezena = **216 pojedinačnih RGB PNG tekstura, 1024 × 1024**, po pet preciznih boja. Kategorije: šumska, pustinjska, urbana, tropska, snežna i premium. Dezeni: pixel/digital, organic/woodland, stripes/tiger, speckled/dot, hex i fragment.

Premium palete: Zlatni pepeo, Krvavi mesec, Kobalt, Ametist, Patina i Obsidijan.

Šest osnova dezena ponavlja se kroz 36 paleta. Izvorni paneli su 512 × 512 i izvezeni su na 1024 × 1024 metodom nearest-neighbor. Teksture nisu seamless; spojeve treba doraditi za kontinuirane UV površine. CSV/JSON sadrže HEX palete; manifest sadrži putanje i SHA256 provere.

Koncept table opreme namenjene su dizajnerima za izdvajanje i prilagođavanje likovima; nisu poravnati transparentni slojevi. Originalni ZIP paketi sadrže postojeće slojeve. Primeri 12 komandira sastavljeni su od tih postojećih slojeva.

## Skripte

`ewarstate/scripts/build.py` reprodukuje kamuflaže iz sačuvanog atlasa uz Python, Pillow i NumPy: `python ewarstate/scripts/build.py`.

`ewarstate/scripts/compose.py` čuva prvobitni recept za komandire, sa putanjama iz sesije; za ponovno pokretanje treba raspakovati izvorne pakete i prilagoditi putanje.

## Oznake predmeta

Koristi se `vrsta_model_boja`, na primer `helmet_1_3.png`. [Pravila imenovanja](ASSET_NAMING.md). Postojeci slemovi: `helmet_1_1`–`helmet_1_240`.
