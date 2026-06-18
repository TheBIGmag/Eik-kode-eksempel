# Livetiming → Livestream

**Formål:** Hente data fra Livetiming.nl og formatere det, så det kan vises i en livestream.

## Baggrund

Livestreamen kan læse data fra en txt-fil. Det betyder, at man styrer, hvad der vises på skærmen, ved at opdatere txt-filen med det ønskede indhold — og filen kan ændres løbende, mens streamen kører. Der opdateres også billede af den kører, der er i bilen.

Livetiming.nl har ingen officiel API, men de har en hjemmeside, der viser dataene. Opgaven er derfor at bygge den manglende API selv: hente data for en bestemt bil og skrive det til txt-filen.

## Sådan virker koden

Koden starter med at efterligne en webbrowser, der henter et øjebliksbillede ("snapshot") af løbet. I dette snapshot får man al data med på én gang. Ulempen er, at det ikke opdaterer sig løbende, når nye tider kommer ind — men det er faktisk en fordel her, fordi det giver mulighed for at søge igennem alle bilerne, finde den rigtige og aflæse dens interne id.

Af en eller anden grund har Livetiming valgt at give bilerne et id, der ikke er deres startnummer. Dette id er det første element i det array, der sendes over websocket'en, og er derfor det centrale at få fat i. En opdatering for bil nummer 10 og 65, som har id 235 og 345, vil for eksempel se sådan ud:

```
[235, {"nummer": 10, "tid": 23423, …}],
[345, {"nummer": 65, "tid": 23500, …}]
```

Rækkefølgen af dataene følger den tabel, som siden selv viser dataene i. Derfor er de reelt heller ikke et objekt, når det bliver sendt, men et array således:

```
[235, [10, 23423, …]],
[345, [65, 23500, …]]
```

Det første snapshot bruges til at finde id'et ved at søge alle data-arrays igennem efter det, der har det rigtige startnummer. Da scriptet skal køre på en Raspberry Pi, der samtidig streamer liveudsendelsen (over 5G), er det nødvendigt at tænke over både regnekraft og båndbredde.

Dataene for bilen bliver formateret og gemt i filen, så streamen starter med de nyeste informationer.

Herefter sender websocket'en kun *ændringer* til det data, der blev hentet ved den første forespørgsel — sådan har Livetiming indrettet deres system. Jeg starter derfor en tråd, der lytter efter nye opdateringer og holder øje med bilen ud fra det id, jeg allerede har fundet. Det sparer en del søgning: en opdatering indeholder ofte kun 1–4 biler, så søgningen bliver på 1–4 punkter i stedet for 1–4 gange antallet af opdaterede datafelter.

## Filtrering af tider

Livetiming sender nogle gange en omgangstid på over 10 minutter, hvis bilen har været i pit under en træning. De tider filtrerer jeg fra, før jeg gemmer.

Grunden til, at jeg tjekker to gange — både mod last lap og mod best lap — er for ikke at misse et edge case: i træning 2 kan føreren godt køre sin egen hurtigste tid uden at slå tiden fra træning 1, som er den, teamet ønsker at holde ham op imod.

## Forbehold (reverse engineering)

Et par steder tager jeg en genvej og plukker data fra en bestemt position i array'et, fordi jeg ved, at det ligger der. I en ideel verden ville jeg have identificeret alle parametre og dokumenteret, hvad hver enkelt betyder. Det var ikke nødvendigt, da jeg byggede det, så jeg ved reelt ikke, hvad de øvrige parametre dækker over — et bud ville være rent gætværk, eftersom det hele er reverse engineered. Det kunne for eksempel være beskeder fra race control eller opdateringer til banekortet med bilernes placering — altså al den data, Livetiming-siden ellers viser.


