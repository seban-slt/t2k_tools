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
python3 extract_t2k.py input.hex output.xex
