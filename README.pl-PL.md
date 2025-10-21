# Squadrats2Garmin
Projekt Squadrats2Garmin project to zestaw narzędzi, które pomagają zbieraczom _Squadratów_ 
posługującym się komputerami rowerowymi i zegarkami firmy Garmin.

## Co to są Squadraty?
No właśnie. [Wyjaśnij mi to](https://squadrats.com/explain) jakbym był twoim dziadkiem!

## Co właściwie daje mi to narzędzie?
Dzięki temu narzędziu możesz widzieć krawędzie dużych i małych kwadratów bezpośrednio na swoim urządzeniu Garmin.
Koniec z ciągłym spoglądaniem na telefon, żeby upewnić się czy kwadrat jest zaliczony.

Możesz pobrać gotową siatkę kwadratów dla interesującego Cię obszaru albo wygenerować swoją własną.

### Wspierane urządzenia
Wszystkie urządzenia Garmin, które wspierają wgrywanie niestandardowych map w formacie IMG. Obejmuje to:

Komputery rowerowe:
- Edge 10x0
- Edge 8x0
- Edge 5x0 (od Edge 520)

Urządzenia podręczne:
- GPSMAP 62, 65

Zegarki
- Garmin Descent
- Garmin Enduro
- Garmin epix
- Garmin Fenix 8, 7, 6, 5X i 5 Plus
- Garmin Forerunner 9xx
- Garmin MARQ
- Garmin tactix

## Gotowe siatki kwadratów
Folder [dist](dist) zawiera gotowe siatki kwadratów. Użyj [instrukcji](dist/README.pl-PL.md) i ruszaj w teren!

Skontaktuj się ze mną jeśli brakuje interesującego Cię obszaru.

## Generowanie własnej siatki kwadratów
Ten projekt zawiera narzędzia, które pozwolą Ci wygenerować siatkę dla dowolnego obszaru. 
Ten proces wymaga znajomości narzędzi takich jak `git`, `Python` i `bash` oraz dostępu do komputera z systemem macOS lub Linux.
```shell
# zainstaluj narzędzie mkgmap
$ sudo apt install mkgmap

# sklonuj repozytorium
$ git clone git@github.com:kbrazulewicz/squadrats2garmin.git
$ cd squadrats2garmin

# ustaw środowisko Python
$ python3 -m venv .venv
$ pip install -r requirements.txt

# aktywuj środowisko Python
$ source .venv/bin/activate
```

Aby wygenerować siatkę uruchom skrypt `squadrats2garmin` jako argument podając ścieżkę do pliku konfiguracyjnego, np.
```shell
# uruchom skrypt
$ python3 squadrats2garmin.py -c config/PL-Polska.json
```
Dowiedz się więcej o [formacie pliku konfiguracyjnego](config/README.md)

## Często zadawane pytania

### Czy mogę zobaczyć które kwadraty zebrał_m?
Nie. Na urządzeniu Garmin możesz zobaczyć siatkę kwadratów bez informacji o tych które zebrał_ś.

### Jak mogę użyć gotowych siatek kwadratów?
Zainstaluj gotowe siatki na swoim urządzeniu Garmin według [instrukcji](dist/README.pl-PL.md).

### Jak mogę stworzyć własną siatkę?
Zobacz sekcję [Generowanie własnej siatki kwadratów](#generowanie-własnej-siatki-kwadratów).

### Jak mogę wyświetlić siatkę w innym kolorze?
Aby użyć własnych kolorów potrzebujesz zmienić domyślną konfigurację.
- zobacz sekcję [Generowanie własnej siatki kwadratów](#generowanie-własnej-siatki-kwadratów)
- dokonaj niezbędnych modyfikcaji w pliku `etc/squadrats.typ.txt`
  - `Type=0x11400` - siatka Squadratinhos
  - `Type=0x11410` - siatka Squadrats (mapa w niskiej skali)
  - `Type=0x11411` - siatka Squadrats (mapa w wysokiej skali)

### Jak mogę się z Tobą skontaktować?
Utwórz nowe [issue](https://github.com/kbrazulewicz/squadrats2garmin/issues) w projekcie.

### Jak mogę Cię wspierać?
<a href="https://buycoffee.to/cykloprzygoda" target="_blank"><img src="https://buycoffee.to/img/share-button-primary.png" style="width: 156px; height: 40px" alt="Postaw mi kawę na buycoffee.to"></a>