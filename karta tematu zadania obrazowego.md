
# Rozpoznawanie numerów tramwajów
Anna Panfil

## Problem
Program rozpoznaje numery tramwajów jeżdżących po Poznaniu. Na zdjęciu musi być widoczny front pojazdu z widocznym numerem (pojazd nie musi być na wprost patrzącego). Pod uwagę brane są tramwaje najczęściej jeżdżące po mieście, z numerem w kółku. Nieobsługiwane są pojazdy Siemens Combino, w których numer wyświetlany jest obok nazwy przystanku końcowego oraz GT8 i GT0.

Wybrałam taki problem, ponieważ numery dobrze odróżniają się od tła, więc powinny być dość łatwe do wykrycia. Druga część projektu, to rozpoznawanie cyfr, które jest często opisywane, więc znalezienie materiałów prawdopodobnie nie będzie stanowiło problemu. Ponadto ma on praktyczne zastosowanie – mógłby ułatwić osobom słabowidzącym i niewidomym korzystanie z komunikacji miejskiej.

## Rozwiązanie

## Wyniki
Dane pozyskam ze stron [ztm](https://www.facebook.com/ZTMwPoznaniu/photos_by)  i [mpk](https://www.mpk.poznan.pl/galeria/galeria), ze strony [fotozajezdnia.pl](https://fotozajezdnia.pl/categories.php?cat_id=465), ze zdjęć dołączanych do artykułów na stronach takich jak poznan.pl, gloswielkopolski.pl, tenpoznan.pl, poznan.naszemiasto.pl ... oraz ze zbiorów własnych.

Postaram się zebrać jak najwięcej zdjęć (min. 100). Jeżeli okaże się to niewystarczające, wygeneruję sztuczne dane na podstawie już zebranych.

Na zbiorze treningowym sprawdzę ile procent numerów zostało poprawnie wykrytych i jak często udało się poprawnie rozpoznać poszczególne cyfry.
