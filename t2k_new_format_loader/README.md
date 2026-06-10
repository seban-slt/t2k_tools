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

## Historia

Oryginalna, częściowo niedopracowana wersja loadera została pozyskana z kasety
zapisanej w Turbo 2000F+ NEW FORMAT. Przebieg odzyskiwania i analizy tego
materiału został opisany w wątku na forum Atari Area:

- [opis walki z kasetą - część 1](https://www.atari.org.pl/forum/viewtopic.php?pid=325359#p325359)
- [opis walki z kasetą - część 2](https://www.atari.org.pl/forum/viewtopic.php?pid=325483#p325483)
- [opis walki z kasetą - część 2.5](https://www.atari.org.pl/forum/viewtopic.php?pid=325568#p325568)

Obecna wersja w tym katalogu jest uporządkowaną i rozwijaną wersją tego
loadera, dostosowaną do użycia z narzędziem `t2k_new_format.py`.

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
długi pilot
FF FF start_lo start_hi end_lo end_hi checksum 00
```

Opis z Atariki podaje w tym miejscu `3584` impulsy pilota, prawdopodobnie na
podstawie starych zapisów taśmowych. Encoder `t2k_new_format.py` używa
znormalizowanego zapisu zgodnego z generowanymi plikami `.hex/.cas`: przed
pierwszym nagłówkiem zapisuje długi pilot (3072 impulsy) jako `pwmc 48 3072`.

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

> [!NOTE]
> Ten format średnio sprawdza się przy plikach `.xex` zawierających bardzo dużo
> krótkich segmentów danych. Dotyczy to np. plików potraktowanych tzw.
> "Zagęszczaczem" Dariusza Rogozińskiego (IRON SOFT). Przy dużej liczbie
> segmentów pomiędzy kolejnymi blokami pojawia się dużo impulsów
> synchronizujących, co bezpośrednio wydłuża czas ładowania.

---

## Budowanie

Do zbudowania loadera potrzebny jest assembler [XASM](https://github.com/pfusik/xasm).

```bash
make xsm
```

Reguła `xsm` buduje plik `t2kf_new_format_ldr.xex` i sprawdza go narzędziem
`chkxex`.

Uruchomienie loadera w emulatorze:

```bash
make run
```

Reguła `run` używa emulatora [atari800](https://atari800.github.io/).

---

## Uwagi techniczne

- Aktualna wersja loadera: `v.0.3`.
- `MEMLO` dla tej wersji wynosi `$08BA`. Jest to najniższy adres, od którego
  loader może bezpiecznie ładować właściwą binarkę `.xex`; segmenty ładowanego
  programu powinny zaczynać się od `$08BA` lub wyżej.
- Loader początkowo lokuje się od `$4000`, a po uruchomieniu relokuje swój kod
  w dolny obszar pamięci Atari, od `$0700`. Takie zachowanie powinno pozwolić
  na załadowanie loadera z praktycznie dowolnego systemu, nośnika lub medium.
- Oryginalny loader działał tylko z systemem Turbo 2000F, czyli z
  magnetofonem/interfejsem przełączanym ręcznie między trybem `Turbo` i
  `Normal`.
- W tej wersji dodano obsługę automatycznego włączania wybranych interfejsów
  turbo przez sterowanie linią SIO `COMMAND`. Powinno to pozwolić na pracę z
  magnetofonami wyposażonymi w turbo AST, ATT, UM oraz Turbo 2000
  (wrocławskie).
- Podczas odczytu loader przełącza również stan linii SIO `DATA_OUT`. Powinno
  to uaktywniać interfejsy typu Blizzard oraz podobne rozwiązania, w których
  tryb `Turbo`/`Normal` wybierany jest na podstawie stanu tej linii.
- Aktualna wersja obsługuje interfejsy Turbo 2000F+ oraz KSO Turbo 2000
  (sprawdzono na realnym sprzęcie). Loader powinien działać również z
  magnetofonami wyposażonymi w interfejsy AST/ATT/UM, wrocławskie/czeskie
  Turbo 2000 oraz Blizzard Turbo.
- Przy starcie loader próbuje wykryć, czy dane z turbo przychodzą przez linię
  SIO `DATA IN`, czy przez port joysticka #2 używany przez KSO Turbo 2000.
- Szczegóły zmian wersji znajdują się w komentarzu na początku pliku
  `t2kf_new_format_loader.xsm`.

---

## TODO

- Wykonać testy na realnych magnetofonach wyposażonych w turbo: AST/ATT/UM,
  wrocławskie/czeskie Turbo 2000 oraz Blizzard Turbo.
