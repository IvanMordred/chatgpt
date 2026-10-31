# eWarState: jedan model, 240 slemova

216 kamuflaznih varijanti (svih 216 tekstura iz camouflage/manifest.json) + 24 jednobojne varijante.

Svaki assets/**/*.png je transparentni RGBA sloj 1024x1024. Dodati na master komandira na x=0,y=0 bez skaliranja. Dizajn je proveren na prilozenoj osnovnoj glavi, uniformi i panciru. Nema tvrdnje o kompatibilnosti sa svakom kosom, kapuljacom, slusalicama ili drugim dodacima. Sakriti kosu koja izlazi ispod slema; ne slagati drugo pokrivalo za glavu preko njega.

Ista silueta i alfa kanal u svih 240 varijanti. Tekstura je primenjena na masku skoljke uz zadrzane senke i osvetljenje; centralni nosac, bocne sine i donja ivica ostaju neutralni. Jednobojne varijante imaju senke i materijal, nisu ravne ikone. Zlatna i srebrna su vizuelni tonovi, ne PBR materijali.

model/helmet_base.png: generisani osnovni model registrovan na master glavu. model/shell_mask.png: maska povrsine koja se boji, pogodna i za dodatnu rucnu doradu. previews/: svih 240 varijanti na komandiru. manifest.json: veza svakog slema sa izvorom teksture. solid_colors.json: HEX baze za jednobojne varijante.

Reprodukcija: Python + Pillow + NumPy, pokrenuti python ewarstate/scripts/build_helmets.py iz repozitorijuma. Osnovni model i korisnicki master paket su sacuvani u repozitorijumu.

Nazivi predmeta: vrsta_model_boја (ASCII u samom nazivu). helmet_1_1 do helmet_1_216 su kamuflaze, helmet_1_217 do helmet_1_240 su obicne boje. Sledeci razlicit model slema je helmet_2_1 itd. Kategorije i opis boje su metapodaci, ne dodatni delovi naziva.
