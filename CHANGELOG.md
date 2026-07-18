# Changelog

Wszystkie istotne zmiany w integracji Husty będą dokumentowane w tym pliku.

## [Unreleased]

### Planowane

- Sterowanie zaworem odcinającym, jeśli zostanie udostępnione przez API.
- Ręczne uruchamianie regeneracji, jeśli zostanie udostępnione przez API.
- Obsługa kolejnych modeli urządzeń Husty.

## [0.1.1] - 2026-07-18

### Dodano

- Obsługę czujników Husty SaoCal Leak Protect.
- Czujnik zalania.
- Temperaturę.
- Wilgotność.
- Poziom baterii.
- Stan połączenia modułu Leak Protect.
- Datę ostatniej aktualizacji modułu.

## [0.1.0] - 2026-07-17

### Zmieniono

- Integracja korzysta z oficjalnego API Husty.
- Autoryzacja odbywa się przy użyciu klucza API.
- Usunięto logowanie adresem e-mail i hasłem.
- Usunięto zależność od sesji aplikacji internetowej.
- Interwał odświeżania ustawiono na 120 sekund.

### Dodano

- Obsługę ponownej autoryzacji po unieważnieniu klucza.
- Statystyki zużycia wody.
- Dane urządzenia w rejestrze Home Assistanta.

## [0.0.6] - 2026-07-16

### Naprawiono

- Cykliczne odświeżanie encji.
- Obsługę `DataUpdateCoordinator`.
- Powiązanie encji z urządzeniem.
