### **T2K NEW FORMAT LOADER** - loader dla Turbo 2000F+ NEW FORMAT.

Ten katalog zawiera źródła loadera przeznaczonego do ładowania danych zapisanych
w formacie **Turbo 2000F+ NEW FORMAT**.

Loader jest używany razem z narzędziem `t2k_new_format.py`, przede wszystkim
przy kodowaniu plików Atari DOS binary / `.xex` do postaci `.hex` lub `.cas`
z opcją `--add-loader`.

---

## Zawartość

- `t2kf_new_format_loader.xsm` - źródło loadera w asemblerze.
- `t2kf_new_format_ldr.xex` - zbudowany plik loadera.
- `makefile` - proste reguły budowania i uruchamiania loadera.

---

## Zastosowanie

Loader obsługuje właściwe bloki danych zapisane w Turbo 2000F+ NEW FORMAT.
Nie jest to zwykły standardowy loader Turbo 2000 - musi rozumieć pary bloków
nagłówek/dane oraz końcowy znacznik EOF używane przez new format.

Plik loadera można dodać do generowanego nagrania za pomocą opcji
`--add-loader`:

```bash
python3 ../t2k_new_format.py --encode --add-loader t2kf_new_format_ldr.xex input.xex output.hex
```

Tak przygotowany plik `.hex` lub `.cas` zawiera na początku standardowy blok
nazwy oraz blok loadera, a po nim właściwe dane programu zapisane w new format.

---

## Format danych

Opis formatu Turbo 2000F+ NEW FORMAT znajduje się na Atariki:
[KSO Turbo 2000 - "Nowy format" (Turbo 2000F+)](http://atariki.krap.pl/index.php/KSO_Turbo_2000#.22Nowy_format.22_.28Turbo_2000F.2B.29).

Nagranie zaczyna się tak samo jak w oryginalnym formacie Turbo 2000:

```text
standardowy blok nazwy Turbo 2000
standardowy blok danych Turbo 2000 z loaderem
```

Ten drugi blok zawiera loader, który przejmuje kontrolę nad dalszym
wczytywaniem właściwego programu.

Właściwe dane programu są później zapisane jako kolejne pary bloków:

```text
nagłówek segmentu
dane segmentu
```

Pierwszy nagłówek jest poprzedzony długim sygnałem pilotującym i ma postać:

```text
3584 impulsy pilota
FF FF start_lo start_hi end_lo end_hi checksum 00
```

Po nim występuje krótki pilot i blok danych:

```text
kilka-kilkanaście impulsów pilota
bajty danych
checksum
00
```

Kolejne nagłówki nie zawierają już początkowego znacznika `FF FF` i są
poprzedzane krótkim pilotem. Jeżeli poprzedni blok był ładowany pod adres
`INITAD` (`$02E2`), przed następnym nagłówkiem występuje dłuższy pilot:

```text
kilka-kilkanaście impulsów pilota
albo 768 impulsów pilota po bloku INITAD
start_lo start_hi end_lo end_hi checksum 00
```

Po każdym nagłówku występuje blok danych o długości wynikającej z zakresu
adresów:

```text
length = end - start + 1
```

Bloki new format kończą się sumą kontrolną modulo 256 oraz bajtem `00`.
Koniec danych oznaczany jest specjalnym nagłówkiem:

```text
FF FF FF FF FC 00
```

Przerwa/cisza pojawia się tylko bezpośrednio po bloku nazwy. Pozostałe bloki są
rozdzielane impulsami sygnału pilotującego.

Loader odczytuje te nagłówki, ładuje dane pod wskazane adresy, wykonuje wektor
`INITAD`, jeśli został ustawiony, a po znaczniku końca danych uruchamia program
przez `RUNAD`.

---

## Budowanie

Do zbudowania loadera potrzebny jest assembler `xasm`.

```bash
make xsm
```

Reguła `xsm` buduje plik `t2kf_new_format_ldr.xex` i sprawdza go narzędziem
`chkxex`.

Uruchomienie loadera w emulatorze:

```bash
make run
```

Reguła `run` używa emulatora `atari800`.

---

## Uwagi techniczne

- Aktualna wersja loadera: `v.0.3`.
- `MEMLO` dla tej wersji wynosi `$08BA`. Jest to najniższy adres, od którego
  loader może bezpiecznie ładować właściwą binarkę `.xex`; segmenty ładowanego
  programu powinny zaczynać się od `$08BA` lub wyżej.
- Loader początkowo lokuje się od $4000, a po uruchomieniu relokuje swój kod w dolny obszar pamięci Atari (od $0700). Takie zachowanie loadera powinno pozwolić na załadowanie go z praktycznie dowolnego systemu/nośnika/medium
- Aktualna wersja obsługuje interfejsy Turbo 2000F+, KSO Turbo 2000, AST/ATT/UM oraz
  Blizzard Turbo (czysto eksperymentalnie).
- Szczegóły zmian wersji znajdują się w komentarzu na początku pliku
  `t2kf_new_format_loader.xsm`.

---

## TODO

- Opisać dokładnie format bloków obsługiwanych przez loader.
- Opisać wymagania pamięciowe i używane wektory systemowe.
- Dodać opis procesu budowania oraz zależności narzędziowych.
