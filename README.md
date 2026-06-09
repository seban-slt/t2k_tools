### **T2K TOOLS** – Pomocnicze skrypty do pracy z kasetami Atari w systemach Turbo 2000 i pokrewnych.

Przez lata pracy nad archiwizacją kaset zapisanych w różnych systemach (standardowych oraz turbo), w moje ręce trafiło wiele nośników zapisanych w systemie **Turbo 2000** i jego odmianach, takich jak:

- Turbo KSO 2000  
- Turbo 2000F  
- Turbo 2001

To repozytorium będzie stopniowo się rozrastać — w miarę odnajdywania i porządkowania skryptów oraz narzędzi, które tworzyłem na własne potrzeby podczas pracy z kasetami. Początkowo były to narzędzia pisane z myślą o prywatnym użytku, jednak uznałem, że skoro mogą się przydać także innym — warto się nimi podzielić.

---

## 🔧 T2K_EXTRACT

Jednym z dostępnych narzędzi jest `t2k_extract` – prosty skrypt w Pythonie umożliwiający konwersję pliku `.hex`, zawierającego bloki typu **PWMD** (wygenerowanego np. przez [a8cas-util](http://www.arus.net.pl/FUJI/a8cas-util/)), do postaci binarnej.

### Cechy:

- Obsługuje dane zapisane w formacie Turbo 2000 / 2001 / 2000F / KSO.
- Odczytuje rekordy danych oraz blok nagłówkowy (nazwa).
- Tworzy binarny plik wynikowy, który może być używany bezpośrednio (np. ładowany przez emulator).

### Wymagania:

- Plik `.hex` musi zawierać poprawny zestaw rekordów danych, zgodnych z natywnym formatem systemu Turbo 2000.
- Narzędzie **nie sprawdza poprawności danych** – zakłada, że dostarczony plik zawiera zgodne i poprawne rekordy.

### Dokumentacja formatu

Dokładny opis formatu Turbo 2000/KSO/2001 można znaleźć tutaj: [Atariki: KSO Turbo 2000 – Format standardowy](http://atariki.krap.pl/index.php/KSO_Turbo_2000#Format_standardowy)

---

## Przykładowe użycie

```bash
python3 t2k_extract.py input_file.hex
```

## Przykład użycia

Poniżej znajduje się przykładowy przebieg konwersji i sprawdzenia pliku z kasety Turbo 2000:

```text
$ ./a8cas-util.pl conv -t turbo2000 hobby_tronic_90.wav hobby_tronic.hex
Starting ecasound... started.
SUMMARY: Data blocks: 28 (0 Errors).
86 HEX blocks stored in file hobby_tronic.hex.

$ ./t2k_extract.py hobby_tronic.hex
nazwa pliku T2K: "HOBBY TRO."

Przetwarzam blok nr 001 o długości 3072 bajtów.
Przetwarzam blok nr 002 o długości 3072 bajtów.
Przetwarzam blok nr 003 o długości 3072 bajtów.
Przetwarzam blok nr 004 o długości 3072 bajtów.
Przetwarzam blok nr 005 o długości 3072 bajtów.
Przetwarzam blok nr 006 o długości 3072 bajtów.
Przetwarzam blok nr 007 o długości 3072 bajtów.
Przetwarzam blok nr 008 o długości 3072 bajtów.
Przetwarzam blok nr 009 o długości 3072 bajtów.
Przetwarzam blok nr 010 o długości 3072 bajtów.
Przetwarzam blok nr 011 o długości 3072 bajtów.
Przetwarzam blok nr 012 o długości 3072 bajtów.
Przetwarzam blok nr 013 o długości 3072 bajtów.
Przetwarzam blok nr 014 o długości 3072 bajtów.
Przetwarzam blok nr 015 o długości 3072 bajtów.
Przetwarzam blok nr 016 o długości 3072 bajtów.
Przetwarzam blok nr 017 o długości 3072 bajtów.
Przetwarzam blok nr 018 o długości 3072 bajtów.
Przetwarzam blok nr 019 o długości 3072 bajtów.
Przetwarzam blok nr 020 o długości 3072 bajtów.
Przetwarzam blok nr 021 o długości 3072 bajtów.
Przetwarzam blok nr 022 o długości 3072 bajtów.
Przetwarzam blok nr 023 o długości 3072 bajtów.
Przetwarzam blok nr 024 o długości 3072 bajtów.
Przetwarzam blok nr 025 o długości 3072 bajtów.
Przetwarzam blok nr 026 o długości 3072 bajtów.
Przetwarzam blok nr 027 o długości 0268 bajtów.

Operacja zakończona, plik 'hobby_tronic.xex' o długości 80140 bajtów zapisano.
```

Po konwersji możemy podejrzeć strukturę wygenerowanego pliku za pomocą ulubionego narzędzia, w moim przypadku jest to [chkxex](https://github.com/seban-slt/tcx_tools/blob/master/chkxex.py) który kiedyś napisałem jako pomoc przy analizowaniu plików z Turbo Copy 3/4. `chkxex` jest częścią pakietu [TCX Tools](https://github.com/seban-slt/tcx_tools).

```text
$ chkxex hobby_tronic.xex
Input file is hobby_tronic.xex and the file size is 80140 bytes.

Header is: $ffff
block 001: $014f-$0165 ($0017)
block 002: $02e2-$02e3 ($0002) ---> INIT $014f
Header is: $ffff
block 003: $0180-$0195 ($0016)
Header is: $ffff
block 004: $0480-$061d ($019e)
Header is: $ffff
block 005: $0165-$0179 ($0015)
block 006: $02e2-$02e3 ($0002) ---> INIT $0165
Header is: $ffff
block 007: $9a77-$bbff ($2189)
Header is: $ffff
block 008: $017e-$017f ($0002)
block 009: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 010: $9d59-$bbff ($1ea7)
Header is: $ffff
block 011: $017e-$017f ($0002)
block 012: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 013: $5ccc-$bbff ($5f34)
Header is: $ffff
block 014: $017e-$017f ($0002)
block 015: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 016: $8ea0-$bbff ($2d60)
Header is: $ffff
block 017: $017e-$017f ($0002)
block 018: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 019: $aada-$bbff ($1126)
Header is: $ffff
block 020: $017e-$017f ($0002)
block 021: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 022: $8d2b-$bbff ($2ed5)
Header is: $ffff
block 023: $017e-$017f ($0002)
block 024: $02e2-$02e3 ($0002) ---> INIT $0480
Header is: $ffff
block 025: $9243-$bbff ($29bd)
Header is: $ffff
block 026: $017e-$017f ($0002)
block 027: $02e0-$02e1 ($0002) --->  RUN $0480

File hobby_tronic.xex is OK!
```

---

## 🔧 T2K_NEW_FORMAT

Kolejnym narzędziem jest `t2k_new_format.py` – skrypt w Pythonie służący do dekodowania i kodowania plików zapisanych w tzw. **Turbo 2000F+ NEW FORMAT**.

Narzędzie pozwala zarówno odtworzyć plik binarny `.xex` z pliku `.hex` zawierającego bloki **PWMD**, jak i wykonać operację odwrotną: zakodować plik `.xex` do postaci `.hex` lub `.cas`, gotowej do dalszej obróbki albo testów w emulatorze.

### Cechy:

- Dekoduje pliki `.hex` zawierające bloki **PWMD** w formacie Turbo 2000F+ NEW FORMAT.
- Tworzy wynikowy plik Atari DOS binary / `.xex`.
- Koduje pliki `.xex` do tekstowego `.hex` albo binarnego `.cas`.
- Obsługuje opcjonalny blok nazwy i loader zapisane fizycznie w standardowym bloku Turbo 2000.
- Sprawdza sumy kontrolne bloków oraz długości segmentów wynikające z zakresów adresów.
- W trybie szczegółowym wypisuje informacje o segmentach, numerach bloków i wykrytych wektorach `RUNAD` / `INITAD`.

### Zastosowanie:

`t2k_new_format.py` przydaje się przy pracy z kasetami Turbo 2000F+, w których właściwe dane programu zapisane są w nowszym formacie: jako pary bloków nagłówka i danych. Każdy nagłówek opisuje zakres adresów Atari, a następujący po nim blok zawiera dane dla tego zakresu.

Skrypt może być użyty m.in. do:

- konwersji zrzutu `.hex` z kasety do pliku `.xex`,
- wyciągnięcia loadera z początku nagrania,
- pominięcia loadera przy dekodowaniu właściwego programu,
- wygenerowania pliku `.hex` lub `.cas` z istniejącego `.xex`,
- przygotowania wersji z dołączonym loaderem obsługującym Turbo 2000F+ NEW FORMAT.

### Wymagania:

- Przy dekodowaniu wejściowy plik `.hex` musi zawierać linie `pwmd` z bajtami bloków Turbo 2000F+ NEW FORMAT.
- Jeśli nagranie zawiera standardowy blok nazwy i loader na początku, należy użyć opcji `--skip-loader`, aby dekodować sam właściwy program.
- Przy kodowaniu plik wejściowy musi być poprawnym plikiem Atari DOS binary / `.xex`.
- Loader dodawany przez `--add-loader` musi obsługiwać ładowanie danych w Turbo 2000F+ NEW FORMAT. Dodanie zwykłego, standardowego loadera Turbo 2000 nie ma sensu, ponieważ nie odczyta on dalszych bloków zapisanych w new format.
- Technicznie plik loadera musi zaczynać się od nagłówka `FF FF` i mieścić się w jednym standardowym bloku Turbo 2000, czyli maksymalnie 3072 bajtach.

### Opcje:

```text
--encode
    Koduje plik .xex do Turbo 2000F+ NEW FORMAT.
    Bez tej opcji narzędzie pracuje w trybie dekodowania .hex -> .xex.

--format auto|hex|cas
    Wybiera format wyjściowy przy kodowaniu.
    Domyślne auto zapisuje .cas dla pliku z rozszerzeniem .cas,
    w pozostałych przypadkach zapisuje .hex.

--skip-loader
    Przy dekodowaniu pomija pierwszy blok nazwy i drugi blok loadera.

--extract-loader LOADER.XEX
    Przy dekodowaniu wyciąga loader z drugiego bloku PWMD
    i zapisuje go jako plik DOS binary / XEX.

--add-loader LOADER.XEX
    Przy kodowaniu dodaje na początku standardowy blok nazwy
    oraz jeden blok z loaderem. Sam loader musi obsługiwać
    ładowanie danych w Turbo 2000F+ NEW FORMAT.

--tape-name NAME
    Ustawia nazwę zapisywaną w standardowym bloku nazwy.
    Nazwa ma maksymalnie 10 bajtów.

--title TEXT
    Ustawia opisową linię FUJI w pliku .hex.

-v, --verbose
    Wypisuje szczegóły operacji.
```

---

## Przykładowe użycie

Dekodowanie pliku `.hex` do `.xex`:

```bash
python3 t2k_new_format.py input_file.hex output_file.xex
```

Dekodowanie pliku `.hex`, w którym na początku znajduje się standardowy blok nazwy i loader:

```bash
python3 t2k_new_format.py --skip-loader input_file.hex output_file.xex
```

Wyciągnięcie loadera z pliku `.hex` i jednoczesne zdekodowanie właściwego programu:

```bash
python3 t2k_new_format.py --extract-loader loader.xex --skip-loader input_file.hex output_file.xex
```

Kodowanie pliku `.xex` do tekstowego `.hex`:

```bash
python3 t2k_new_format.py --encode input_file.xex output_file.hex
```

Kodowanie pliku `.xex` do binarnego `.cas`:

```bash
python3 t2k_new_format.py --encode --format cas input_file.xex output_file.cas
```

Kodowanie pliku `.xex` z dodaniem loadera obsługującego Turbo 2000F+ NEW FORMAT:

```bash
python3 t2k_new_format.py --encode --add-loader loader.xex --tape-name PROGRAM input_file.xex output_file.hex
```

## Tryb szczegółowy

Dodanie opcji `-v` / `--verbose` powoduje wypisanie dodatkowych informacji diagnostycznych. Przy dekodowaniu są to m.in. liczba odnalezionych bloków `pwmd`, pominięty blok nazwy i loadera, adresy segmentów, numery bloków oraz wykryte wektory `RUNAD` / `INITAD`. Przy kodowaniu narzędzie wypisuje zakodowane segmenty oraz podsumowanie zapisanego pliku.

Po konwersji wynikowy plik `.xex` można dodatkowo sprawdzić np. za pomocą `chkxex`, tak jak w przykładzie dla `t2k_extract.py`.

## Przykład użycia

Poniżej znajduje się rzeczywisty przykład przygotowany na podstawie dema **Revenge of Magnus** oraz loadera `t2kf_new_format_ldr_v03.xex`, który obsługuje ładowanie danych w Turbo 2000F+ NEW FORMAT.

Najpierw kodujemy plik `.xex` do tekstowego `.hex` i dodajemy loader:

```text
$ ./t2k_new_format.py --encode --add-loader examples/t2kf_new_format_ldr_v03.xex --tape-name MAGNUS -v examples/revenge_of_magnus.xex /tmp/revenge_of_magnus.hex
added loader: examples/t2kf_new_format_ldr_v03.xex (792 bytes), name='MAGNUS'
encoded   1: $0041-$0041      1 bytes
encoded   2: $022F-$022F      1 bytes
encoded   3: $D400-$D400      1 bytes
encoded   4: $02C8-$02C8      1 bytes
encoded   5: $0244-$0244      1 bytes
encoded   6: $6401-$888E   9358 bytes
encoded   7: $0600-$0636     55 bytes
encoded   8: $02E2-$02E3      2 bytes INITAD
encoded   9: $A099-$BFFF   8039 bytes
encoded  10: $0528-$0530      9 bytes
encoded  11: $0500-$050D     14 bytes
encoded  12: $2710-$280B    252 bytes
encoded  13: $280C-$283A     47 bytes
encoded  14: $02E0-$02E1      2 bytes RUNAD
encoded  15: $02C6-$02C6      1 bytes
encoded  16: $D018-$D018      1 bytes
written: /tmp/revenge_of_magnus.hex format=hex segments=16 data_bytes=17785
```

Następnie dekodujemy wygenerowany plik `.hex`, pomijając dodany blok nazwy i loader. Przy okazji można wyciągnąć loader z nagrania do osobnego pliku:

```text
$ ./t2k_new_format.py --skip-loader --extract-loader /tmp/magnus_loader_extracted.xex -v /tmp/revenge_of_magnus.hex /tmp/revenge_of_magnus_decoded.xex
pwmd blocks: 35
loader written: /tmp/magnus_loader_extracted.xex (792 bytes)
skipped name:   pwmd#1, line=5, name='MAGNUS'
skipped loader: pwmd#2, line=7, data_len=792 bytes, physical_data=3072 bytes
segment   1: pwmd#  3/#  4 line     9/   11 $0041-$0041      1 bytes
segment   2: pwmd#  5/#  6 line    13/   15 $022F-$022F      1 bytes
segment   3: pwmd#  7/#  8 line    17/   19 $D400-$D400      1 bytes
segment   4: pwmd#  9/# 10 line    21/   23 $02C8-$02C8      1 bytes
segment   5: pwmd# 11/# 12 line    25/   27 $0244-$0244      1 bytes
segment   6: pwmd# 13/# 14 line    29/   31 $6401-$888E   9358 bytes
segment   7: pwmd# 15/# 16 line    33/   35 $0600-$0636     55 bytes
segment   8: pwmd# 17/# 18 line    37/   39 $02E2-$02E3      2 bytes INITAD
segment   9: pwmd# 19/# 20 line    41/   43 $A099-$BFFF   8039 bytes
segment  10: pwmd# 21/# 22 line    45/   47 $0528-$0530      9 bytes
segment  11: pwmd# 23/# 24 line    49/   51 $0500-$050D     14 bytes
segment  12: pwmd# 25/# 26 line    53/   55 $2710-$280B    252 bytes
segment  13: pwmd# 27/# 28 line    57/   59 $280C-$283A     47 bytes
segment  14: pwmd# 29/# 30 line    61/   63 $02E0-$02E1      2 bytes RUNAD
segment  15: pwmd# 31/# 32 line    65/   67 $02C6-$02C6      1 bytes
segment  16: pwmd# 33/# 34 line    69/   71 $D018-$D018      1 bytes
EOF: pwmd#35, line=73
written: /tmp/revenge_of_magnus_decoded.xex segments=16 data_bytes=17785
```

Wynikowy plik `.xex` można sprawdzić narzędziem `chkxex`:

```text
$ chkxex /tmp/revenge_of_magnus_decoded.xex
Input file is /tmp/revenge_of_magnus_decoded.xex and the file size is 17851 bytes.

Header is: $ffff
block 001: $0041-$0041 ($0001)
block 002: $022f-$022f ($0001)
block 003: $d400-$d400 ($0001)
block 004: $02c8-$02c8 ($0001)
block 005: $0244-$0244 ($0001)
block 006: $6401-$888e ($248e)
block 007: $0600-$0636 ($0037)
block 008: $02e2-$02e3 ($0002) ---> INIT $0600
block 009: $a099-$bfff ($1f67)
block 010: $0528-$0530 ($0009)
block 011: $0500-$050d ($000e)
block 012: $2710-$280b ($00fc)
block 013: $280c-$283a ($002f)
block 014: $02e0-$02e1 ($0002) --->  RUN $2710
block 015: $02c6-$02c6 ($0001)
block 016: $d018-$d018 ($0001)

File /tmp/revenge_of_magnus_decoded.xex is OK!
```

Warto zauważyć, że zdekodowany plik `.xex` może nie być bajtowo identyczny z wejściowym plikiem `.xex`, ponieważ narzędzie zapisuje znormalizowany DOS binary. Dane segmentów i ich kolejność pozostają jednak zgodne, co widać w wyniku `chkxex`.
