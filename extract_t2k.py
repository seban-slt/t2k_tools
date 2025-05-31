#!/usr/bin/env python3
#
# skrypt umożliwia konwersję pliku .hex zawierającego bloki PWMD (wygenerownane np. przez a8cas-util.pl) do postaci binarnej
# plik hex musi zawierać poprawny zbiór rekordów danych zgodnych z natywnym formatem Turbo 2000/2001/2000F/KSO, tzn.
#
# poprawne nagranie powinno składać sie z bloku nazwy oraz następujących po nim rekordów danych,
# dokładniejszy opis natywnego formatu można znaleźć tu: http://atariki.krap.pl/index.php/KSO_Turbo_2000#Format_standardowy
#
# narzędzie zostało stworzone aby umożliwić prosta konwersję zbiorów zapisanych w standardowym formacie "Turbo 2000",
# do postaci binarnej, dzieki temu możliwe jest pominięcie programu kopijącego po stronie Atari
#
# !!! UWAGA !!! Narzędzie nie sprawdza zgodności i poprawności danych zawartych w blokach "PWMD", oczekuje ono
# że dostarczone do niego dane będą poprawne i zgodne z natywnym formatem  Turbo 200x/KSO/F
#
# Seban/Slight, Warszawa, Listopad 2023, (P) Public Domain (P)

import os
import sys
import re

# Sprawdzenie, czy podano argument wejściowy (w domyśle nazwę pliku do przetworzenia)
if len(sys.argv) != 2:
    print("Podaj nazwę pliku .hex jako argument.")
    sys.exit(1)

# przetworznie nazwy pliku
input_file = sys.argv[1]
base_name = os.path.splitext(input_file)[0]
final_name = base_name + ".xex"

# tutaj przechowamy nazwę pliku wyjściowego (deklaruemy jako typ bytes)
xex_name =  b''

# flaga określająca czy w pliku wejściowym odnaleziono już segment zawierający nazwę pliku
xex_name_found = False

# Otwarcie pliku wejściowego do odczytu
with open(input_file, 'r') as file:

    # Odczyt poszególnych linii danych z pliku
    lines = file.readlines()

block_no = 1

# Przetwarzanie linii w poszukiwaniu pasujących wzorców
for line in lines:
    # Wyszukanie wszystkich pasujących wzorców "pwmd" oraz ciągów heksadecymalnych
    matches = re.findall(r'pwmd\s+([0-9a-fA-F\s]+)', line)

    # Jeśli nie mamy jeszcze nazwy pliku xex, znajdź ją w pierwszym segmencie "pwmd"
    if not xex_name_found and matches:
        for match in matches:
            hex_values = match.split()

            # Sprawdź, czy długość jest co najmniej 4 (2 bajty długości danych + 2 pierwsze zawsze ignorowane)
            if len(hex_values) >= 4 and hex_values[2] == '00' and hex_values[3] == 'ff':
                xex_name = bytes([int(val, 16) for val in hex_values[4:-1]])
                xex_name_found = True
                xex_name = xex_name.decode()
                print(f'nazwa pliku T2K: "{xex_name}"\n')

		# tworzymy nowy pusty plik wyjściowy
                with open(final_name, 'wb'):
                    pass

    # Jeśli mamy nazwę pliku to przetwarzamy i zapisujemy dane do pliku o tej nazwie
    if xex_name_found and matches:
        for match in matches:
            hex_values = match.split()
            if len(hex_values) > 2:
                # Pobranie długości istotnych danych z dwóch kolejnych bajtów
                data_length = int(hex_values[2], 16) + int(hex_values[3], 16) * 256

                # Jeśli mamy wystarczającą ilość danych w przetwarzanym segmencie, zapisujemy istotne dane do pliku
                if len(hex_values) >= data_length + 4:
                    data = bytes([int(val, 16) for val in hex_values[4:data_length + 4]])

                    # otwieramy plik do zapisu w trybie dołączania i dopisujemy kolejny przetworzony rekord danych
                    with open(final_name, 'ab') as xex_file:
                        xex_file.write(data)

                    print(f"Przetwarzam blok nr {block_no:03} o długości {len(data):04} bajtów.")
                    block_no += 1

size = os.path.getsize(final_name)
print()
print(f"Operacja zakończona, plik '{final_name}' o długości {size} bajtów zapisano.")
