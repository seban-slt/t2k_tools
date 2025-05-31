### **T2K TOOLS** – Pomocnicze skrypty do pracy z kasetami Atari w systemach Turbo 2000 i pokrewnych.

Przez lata pracy nad archiwizacją kaset zapisanych w różnych systemach (standardowych oraz turbo), w moje ręce trafiło wiele nośników zapisanych w systemie **Turbo 2000** i jego odmianach, takich jak:

- Turbo KSO 2000  
- Turbo 2000F  
- Turbo 2001

To repozytorium będzie stopniowo się rozrastać — w miarę odnajdywania i porządkowania skryptów oraz narzędzi, które tworzyłem na własne potrzeby podczas pracy z kasetami. Początkowo były to narzędzia pisane z myślą o prywatnym użytku, jednak uznałem, że skoro mogą się przydać także innym — warto się nimi podzielić.

---

## 🔧 EXTRACT_T2K

Jednym z dostępnych narzędzi jest `extract_t2k` – prosty skrypt w Pythonie umożliwiający konwersję pliku `.hex`, zawierającego bloki typu **PMWD** (wygenerowanego np. przez [a8cas-util](http://www.arus.net.pl/FUJI/a8cas-util/)), do postaci binarnej.

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
python3 extract_t2k.py input_file.hex
```

## Przykład użycia

Poniżej znajduje się przykładowy przebieg konwersji i sprawdzenia pliku z kasety Turbo 2000:

```text
$ ./a8cas-util.pl conv -t turbo2000 hobby_tronic_90.wav hobby_tronic.hex
Starting ecasound... started.
SUMMARY: Data blocks: 28 (0 Errors).
86 HEX blocks stored in file hobby_tronic.hex.

$ ./extract_t2k.py hobby_tronic.hex
nazwa pliku T2K: "HOBBY TRO."
```

Po konwersji możemy podejrzeć strukturę wygenerowanego pliku za pomocą ulubionego narzędzia, w moim przypadku jest to [chkxex](https://github.com/seban-slt/tcx_tools/blob/master/chkxex.py) który kiedyś napisałem jako pomoc przy analizowaniu plików z Turbo Copy 3/4. `chkxex` jest częścią pakietu [TCX Tools](https://github.com/seban-slt/tcx_tools)

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
