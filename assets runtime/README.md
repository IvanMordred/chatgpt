# eWarState — materijali za web aplikaciju

Jedna RGBA osnova + maska materijala po modelu. Aplikacija nanosi izabranu običnu boju ili kamuflažu samo kroz masku, uz senke i šavove iz osnove. Originalna providnost i položaj 1024 × 1024 ostaju isti. Odelo i pancir su odvojeni slojevi.

**Pokretanje primera:** posluži ovaj folder preko HTTP(S), kao ostatak aplikacije. Iz korena repozitorijuma: `python -m http.server 8000`, pa otvori `http://localhost:8000/assets%20runtime/demo.html`. GitHub prikazuje izvor; HTML primer treba pokrenuti na serveru. Nema npm zavisnosti.

## Šta se čuva

- `uniforms/uniform 1/base.webp`, `material_mask.png`, itd: isti raspored tipova i modela kao u `assets v2`. WebP je lossless; svih 171 osnova i glava se dekodiraju identično izvornim PNG slikama.
- `patterns/*.png`: šest zajedničkih mapa 512 × 512. Vrednosti piksela su **0, 1, 2, 3, 4**, indeksi boja, a ne vidljive sive teksture. Čitati bez korekcije boja, nearest sampling, bez mipmapa.
- `catalog.json`: 36 paleta, 216 kombinacija, 24 obične boje, modeli, maske i recepti postojećih predmeta. Rekonstrukcija svih 216 tekstura proverena je piksel po piksel u odnosu na originalne 1024 × 1024 PNG teksture.
- `region_*.png`: opcione dodatne maske. Primeri: rukavi / torzo na `uniform_1`, kruna na `cap_1`. Ostali modeli trenutno imaju jednu masku materijala. Dizajner dodaje nove maske kada želi precizniju podelu.

Maska je crno-bela: **belo = primeni materijal, crno = sačuvaj osnovu**, sivo = delimično. Efektivna maska = maska materijala × maska odabranog dela. Ona menja RGB, nikada alpha kanal. Ne menjati alpha odela da bi se ograničila kamuflaža. Ova aplikacija ne prepoznaje automatski delove na proizvoljno poslatoj slici: dizajner priprema masku jednom, a zatim aplikacija automatski primenjuje sve boje i dezene.

Za nove modele sa odvojenim metalom, staklom ili drugim materijalom masku treba ručno proveriti na spojevima. Postojeće maske prenete su iz V2; pojedinačni sivi detalji dele materijal sa tkaninom. Za nezavisno bojenje tih detalja treba ih izdvojiti dodatnom maskom. Primer krune/rukava je početna podela za dizajn, ne univerzalna automatska segmentacija svih odela.

## JavaScript i Pixi / Phaser

`materials.js` je funkcionalan Canvas 2D renderer. Menja izgled po izboru igrača, zatim rezultat koristiš kao jednu privremenu teksturu. **Ne pokretati petlju od milion piksela svakog frejma.** Učitavati samo opremljene modele; ograničiti keš rezultata i uništiti GPU teksture kada više nisu potrebne.

```js
import {CommanderMaterials} from './assets runtime/materials.js';
const materials = await CommanderMaterials.load('./assets runtime/');
const layer = await materials.render('uniform_1', {
  kind: 'camouflage', texture: 'pustinjska-01-01', region: 'sleeves'
});
// Pixi (v7/v8):
const sprite = new PIXI.Sprite(PIXI.Texture.from(layer));
// Phaser 3 alternativa: scene.textures.addCanvas('uniform-current', layer);
// scene.add.image(0, 0, 'uniform-current').setOrigin(0);
```

`render` vraća sloj u punoj dimenziji i na položaju 0,0; skaliraj ceo kontejner komandira zajedno. Postojeće PNG fajlove za boje aplikacija ne mora da preuzima.

```js
// Postojeći ID ostaje isti:
const canvas = await materials.renderItem('helmet_1_3');
// Sve dostupne varijante modela, uključujući nove virtuelne kamuflaže:
const choices = materials.styles('vest_1');
// Obična boja, na istim označenim delovima:
const solid = await materials.render('uniform_1', {
  kind: 'solid', hex: '#697447', region: 'torso'
});
```

Svih 918 postojećih ID-jeva `vrsta_model_boja` ostaju sačuvani. Nove kamuflaže za dozvoljene modele dobijaju brojeve iza postojećih; generišu se iz kataloga, bez novih PNG fajlova. Zamrzni redosled `textures` i `legacyStyles` pri nadogradnji da brojevi ostanu stabilni. Dodatne ručno izabrane boje i delove čuvaj kao `materialOverrides` uz ID predmeta; to nisu novi numerisani predmeti.

Za veći broj istovremeno animiranih komandira `material.frag` daje WebGL 1 shader jezgro koje istu operaciju izvršava na GPU. Ovo je shader jezgro, a ne gotov Pixi filter / Phaser pipeline: adapter zavisi od vaše verzije biblioteke. Koristi pune UV koordinate sloja, sve teksture van atlasa, bez trimovanja, i premultiplied alpha za `uBase`; izlaz je takođe premultiplied. Veži belu 1 × 1 teksturu za `uRegion` kada nema odabranog dela. Uniforme: `uKind` 0/1/2 = osnova/boja/kamuflaža; `uShadeDivisor` je u katalogu. Kod Canvas renderera browser koristi straight RGBA. Canvas i GPU mogu blago odstupati zbog premultiplication i zaokruživanja; browser provera meri to odstupanje u `browser-validation.json`. Osnovne slike i rekonstrukcija tekstura su zasebno proverene bez gubitka.

Pravila slojeva i zatvorenih šlemova su u `compatibility.json`. Primer primenjuje ta pravila za svoja četiri slota; ne garantuje da je svaka kombinacija opreme vizuelno kompatibilna. Postojeći PNG paket i 24 pregledane kombinacije ostaju u `assets v2`.

## Prostor i isporuka

Upoređuj ukupnu veličinu ovog runtime foldera sa 918 PNG varijanti, ne sa veličinom Git istorije. U aplikaciju / CDN objavi ovaj folder i učitavaj po potrebi. Stari PNG fajlovi ostaju za dizajn; dodavanje ovog paketa **ne smanjuje postojeći Git repozitorijum**. Detaljna merenja i provere: `validation.json`. Teksture nisu seamless; ovaj sistem ih mapira na portret, a ne na kontinuirane 3D UV površine.

Ponovna izgradnja osnova/kataloga: `python ewarstate/v2/build_runtime.py` iz korena repozitorijuma. Zahteva Pillow i NumPy; skripta ne izvozi hiljade obojenih PNG varijanti. Ručno pripremljeni JS, shader i uputstvo ostaju sačuvani.

Browser provera iz korena repozitorijuma: `node ewarstate/v2/check_runtime.cjs` uz prethodno pokrenut lokalni server na portu 8765. Za proveru je potreban Playwright i Chromium; to nisu zavisnosti same aplikacije.
