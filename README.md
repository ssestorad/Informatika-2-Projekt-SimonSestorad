# Farkle se schopnostmi

Tato hra je rozšířenou verzí klasické kostkové hry **Farkle**, obohacenou o **speciální schopnosti hráčů**, které přidávají strategickou hloubku a zvyšují znovuhratelnost. Hraje se **hráč proti hráči** nebo **hráč proti AI**, hra má vlastní obrazovku **nastavení** a je plně **lokalizovaná do tří jazyků** (čeština, angličtina, hebrejština).

![Ukázka hry](assets/screenshot.png)

---

## Jak hru spustit

**Požadavky:** Python 3 s modulem `tkinter` (u instalace z [python.org](https://www.python.org/) je součástí výchozí instalace; na Linuxu může být potřeba doinstalovat balíček `python3-tk`).

```bash
git clone https://github.com/ssestorad/Informatika-2-Projekt-SimonSestorad.git
cd Informatika-2-Projekt-SimonSestorad
python main.py
```

Hra se ovládá myší — kostky se vybírají kliknutím, dál se pokračuje tlačítky HÁZEJ / POTVRĎ VÝBĚR / BANK. Pro rychlejší hraní jdou použít i **klávesové zkratky**: `Enter` = házej / pokračuj po Farkle, `mezerník` = bank, `C` = potvrď výběr (vždy jen když je daná akce skutečně dostupná). Herní okno je možné libovolně **zvětšit nebo zmenšit** tažením za okraj.

---

## Cíl hry

Cílem hry je být **první hráč**, který dosáhne cílového počtu bodů (výchozí hodnota **10 000 bodů**, dá se změnit v nastavení).

---

## Herní režimy

Z hlavního menu se vybírá mezi dvěma tlačítky:

* **HRÁČ VS HRÁČ** — klasická hra pro dva lidi u jednoho počítače, oba zadají jméno.
* **HRÁČ VS AI** — hraje se proti počítači, který se jmenuje "AI". Kromě jména se vybírá i **obtížnost**:
  * **OPATRNÁ** — bankuje při první rozumné příležitosti, moc neriskuje.
  * **RISKUJÍCÍ** — pokračuje v házení déle, i s málo kostkami na stole.

  AI hraje podle úplně stejných pravidel a se stejnými schopnostmi jako člověk, jen se sama rozhoduje mezi dalším hodem a bankem. Tahy AI běží se zpožděním mezi kroky (hod → výběr → potvrzení → rozhodnutí), ať je vidět, co dělá — tlačítka se během jejího tahu schovají a nahradí textem "AI hraje…".

---

## Nastavení

Z hlavního menu je dostupné tlačítko **NASTAVENÍ**, kde lze upravit:

* **Cílové skóre** — kolik bodů je potřeba k výhře (výchozí 10 000).
* **Minimální bank** — kolik bodů musí mít hráč nasbíráno v kole, aby mohl kolo ukončit a zapsat si je (výchozí 500).
* **Rozlišení okna** — počáteční velikost herního okna, vybírá se z předpřipravených možností (okno pak jde libovolně přetáhnout na jinou velikost).
* **Jazyk** — přepínání mezi třemi jazyky pomocí vlaječek:
  * 🇨🇿 **čeština**
  * 🇬🇧🇺🇸 **angličtina**
  * 🇮🇱 **hebrejština**

  Lokalizované je kompletně celé rozhraní hry — nadpisy, tlačítka, popisky kostek, bodovací kombinace i hlášky, které se za běhu objevují v herním logu (Farkle, bank, aktivace schopností apod.).

Nastavení se **ukládá mezi spuštěními** (do souboru `settings.json` vedle hry), takže se po restartu hry nemusí nastavovat znovu.

---

## Pravidla hry

### Průběh tahu

1. **Hod.** Hráč začíná své kolo tlačítkem HÁZEJ, které hodí všemi šesti kostkami (kostky, které ještě nejsou odložené, se předtím krátce zamíchají animací, než se ustálí na skutečném výsledku, a hod je doprovázený zvukem).
2. **Výběr bodovaných kostek.** Z hozených kostek musí hráč kliknutím vybrat **alespoň jednu bodovanou kostku** nebo kombinaci (viz bodovací tabulka níže) — nebodované kostky vybrat nejde. Vybrané kostky (stav VYBRÁNO) ukazují svůj součet v panelu „Vybráno k odložení".
   * Hráč nemusí vybrat úplně všechny bodované kostky z hodu — může si nechat jen část a zbytek riskovat v dalším hodu (např. nechat si jednu jedničku a zkusit ze zbylých kostek trefit trojici).
3. **Potvrzení výběru.** Tlačítkem POTVRĎ VÝBĚR se vybrané kostky **odloží (uloží)** a jejich body se přičtou k „Nasbíráno v kole". Odložené kostky (stav ULOŽENO) se dál nehází.
4. **Horké kostky.** Pokud tímto potvrzením hráč odloží **úplně všech 6 kostek**, získává *horké kostky* — všech šest se resetuje a hází se jimi znovu od začátku, body nasbírané v kole se ale nemažou.
5. Se zbývajícími (dosud neodloženými) kostkami se hráč rozhoduje:
   * **házet dál** a zkusit získat další body, nebo
   * **ukončit kolo** tlačítkem BANK a zapsat si nasbírané body do celkového skóre — jde to jen tehdy, když má hráč v kole nasbíráno alespoň tolik bodů, kolik určuje **minimální bank** (viz Nastavení, výchozí 500).
6. Po zapsání banku (nebo po Farkle, viz níže) **přichází na řadu druhý hráč**.

### Farkle

Pokud hod **neobsahuje žádnou bodovanou kostku** (mezi kostkami, které ještě nejsou odložené), je to *Farkle* — hráč přichází o **všechny body nasbírané v tomto kole**, i kdyby si předtím odložil sebevíc. Než se tah předá dalšímu hráči, hra vyhozené (nebodující) kostky zobrazí zvýrazněné červeně spolu s upozorněním, takže je vidět přesně, co Farkle způsobilo — teprve po potvrzení tlačítkem POKRAČOVAT se tah předá.

---

## Bodovací tabulka

| Kombinace        | Body |
| ---------------- | ---- |
| Jednička (1)     | 100  |
| Pětka (5)        | 50   |
| 3 × dvojka (2)   | 200  |
| 3 × trojka (3)   | 300  |
| 3 × čtyřka (4)   | 400  |
| 3 × pětka (5)    | 500  |
| 3 × šestka (6)   | 600  |
| 3 × jednička (1) | 1000 |
| 3 × dvojice (např. 2-2, 5-5, 6-6) | 1000 |
| Postupka (1-2-3-4-5-6) | 2000 |
| 6 stejných čísel | 5000 |

---

## Schopnosti hráčů

Přehled níže nemusíš mít v hlavě — stačí ve hře najet myší na fialový odznak aktivní schopnosti nahoře a zobrazí se bublinová nápověda s vysvětlením, co dělá.

### Pravidla schopností

* Na začátku hry dostane každý hráč náhodnou **primární schopnost** (obě jsou vždy různé) — losuje se ze všech 9 schopností níže.
* **Každých 5 tahů** hráč dostane novou **sekundární schopnost**, vylosovanou z šesti "útočných/bankovních" schopností (Dvojnásobník, Sabotáž, Krádež, Fast Points, 10% Boost, Extra tah). **Pojistka, Zrcadlový štít a Zmizík** tedy může hráč získat **jen jako primární** schopnost na úplném začátku hry.
* Hráči je vždy aktivní **jen jedna schopnost — ta nejnovější**. Jakmile hráč poprvé dostane sekundární schopnost (v 5. tahu), natrvalo přebere místo primární — pokud primární do té doby nebyla použita, propadá.
* Schopnosti se aktivují **automaticky**, jakmile nastane jejich podmínka — u Dvojnásobníku, Fast Points, 10% Boostu, Sabotáže, Krádeže, Zmizíku a Extra tahu hned při nejbližším zapsání banku; u Pojistky až při Farkle a u Zrcadlového štítu až při soupeřově útoku.
* Schopnosti **nelze odkládat ani šetřit na později** a každá se použije **nejvýš jednou** — pokud ale hráč později vylosuje schopnost, kterou už dřív spotřeboval, dostává ji znovu čerstvou.

### Přehled schopností

* **DVOJNÁSOBNÍK** – Bank zapsaný při nejbližším BANKu se **zdvojnásobí (×2)**.
* **FAST POINTS** – K nejbližšímu zapsanému banku se přidá rovnou **+500 bodů**.
* **10 % BOOST** – Po zapsání nejbližšího banku získáš navíc **+10 % svého celkového skóre** (počítáno už s právě přičteným bankem).
* **EXTRA TAH** – Po zapsání nejbližšího banku **hraješ hned další tah navíc** — tah se soupeři nepředává.
* **SABOTÁŽ** – Při zapsání banku zničíš soupeři **25 % jeho aktuálního celkového skóre** (body nikam nepřecházejí, prostě zmizí).
* **KRÁDEŽ** – Při zapsání banku ukradneš soupeři **15 % jeho aktuálního celkového skóre** a přičteš si je k vlastnímu.
* **ZMIZÍK** – Při zapsání banku vymažeš soupeři přesně tolik bodů, kolik měl jeho **poslední zapsaný bank** (pokud ještě nebankoval, nic se nestane). Pokud **vyprší nevyužitý**, sundá soupeři rovnou **500 bodů**.
* **POJISTKA** – Když příště hodíš *Farkle*, body nasbírané v tom kole se ti přesto **automaticky připíšou** místo ztráty.
* **ZRCADLOVÝ ŠTÍT** – Pasivní obrana. Použije-li na tebe soupeř Sabotáž nebo Krádež, útok se **odrazí zpátky** — útočník místo tebe ztratí 30 % svého celkového skóre. Pokud štít **vyprší nevyužitý** (nahradí ho nová schopnost), získáš jako náhradu **+500 bodů**.

---

## Konec hry

Po dosažení cílového skóre se místo pouhého oznámení vítěze zobrazí **výsledková tabulka**, která srovnává oba hráče: finální skóre, počet tahů, počet Farklů (i v procentech), počet úspěšných banků, nejvyšší jednorázový bank, celkem vsazené body, body získané i ztracené díky schopnostem a přehled použitých schopností.

---
