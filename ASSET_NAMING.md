# Nazivi predmeta

Svaki novi predmet i njegov ID koriste tacno tri dela:

`vrsta_predmeta_brojModela_brojBoje`

Primeri: `helmet_1_3.png`, `helmet_2_1.png`, `uniform_1_1.png`, `vest_1_1.png`.

- Vrsta: engleski naziv, npr. helmet, uniform, vest, mask.
- Model: broj razlicitog osnovnog dizajna unutar iste vrste, pocev od 1.
- Boja: broj boje ili teksture tog modela, pocev od 1. Svaki model ima svoj niz boja.
- Koristiti brojeve bez vodecih nula radi doslednosti. Ekstenzija nije deo ID-a.
- Naziv palete, kamuflazne kategorije i dezena cuvati u manifestu; ne dodavati ih ID-u.
- Ne menjati dodeljene brojeve prilikom dodavanja novih varijanti.
- Originalni korisnicki izvorni paketi i koncept table nisu pojedinacni novi predmeti i zadrzavaju nazive.

Postojeci model helmet_1: 1–216 su kamuflazne teksture, 217–240 su obicne boje. Manifest u ewarstate/helmets/manifest.json cuva detaljno preslikavanje; name_mapping.json sadrzi stare i nove oznake.

Novi modeli u headgear50: cap_1–cap_13, helmet_2–helmet_21, beret_1–beret_4, hat_1–hat_7, hood_1–hood_6. Sledeci slobodni brojevi: cap_14, helmet_22, beret_5, hat_8, hood_7. Prednji i zadnji sloj koriste isti ID i naziv fajla u odvojenim direktorijumima assets/ i rear_assets/; oznake sloja su u metapodacima.

Expansion rezervisani modeli: uniform_1–30, vest_1–30, mask_1–6, scarf_1–4, balaclava_1–10, gasmask_1–10, glasses_1–2, eyepatch_1, headset_1–2, cigar_1, cigarette_1, rank_1–3, facepaint_1–5, scar_1–5, background_1–10. Sledeci model svake vrste pocinje prvim slobodnim brojem posle ovog opsega; stari izvorni paketi nisu preimenovani.
