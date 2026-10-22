#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera 'peliculas.json' para la app cam match.

- Lee la lista de películas de PELICULAS (abajo).
- Consulta TMDB (API v3 o v4) para obtener:
    * titulo          -> título en español (fallback al original)
    * titulo_original -> título original de TMDB
    * poster          -> URL completa w600_and_h900_face
- Guarda el resultado en 'peliculas.json'.

Uso:
    export TMDB_READ_TOKEN="eyJ..."   # v4 (recomendado)
    # o
    export TMDB_API_KEY="tu_clave_v3"
    python generar_peliculas.py
"""

import json
import os
import sys
import time
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------
TMDB_READ_TOKEN = os.environ.get("TMDB_READ_TOKEN")  # v4, JWT
TMDB_API_KEY    = os.environ.get("TMDB_API_KEY")     # v3, 32 chars

BASE_URL    = "https://api.themoviedb.org/3"
IMAGE_BASE  = "https://image.tmdb.org/t/p/w600_and_h900_face"
OUTPUT_FILE = "peliculas.json"

MAX_RETRIES     = 3
RETRY_DELAY     = 2
REQUEST_DELAY   = 0.25

# ---------------------------------------------------------------------------
# LISTA DE PELÍCULAS (título de búsqueda + año)
# ---------------------------------------------------------------------------
# 'titulo' es solo el término de búsqueda; el resultado real vendrá de TMDB.
PELICULAS = [
    {"id": 1,  "titulo": "Parasite",                                                   "anio": 2019},
    {"id": 2,  "titulo": "12 Angry Men",                                               "anio": 1957},
    {"id": 3,  "titulo": "Sunset Boulevard",                                           "anio": 1950},
    {"id": 4,  "titulo": "Playtime",                                                   "anio": 1967},
    {"id": 5,  "titulo": "Persona",                                                    "anio": 1966},
    {"id": 6,  "titulo": "A Woman Under The Influence",                                "anio": 1974},
    {"id": 7,  "titulo": "Les 400 Coups",                                              "anio": 1959},
    {"id": 8,  "titulo": "Trois Couleurs. Rouge",                                      "anio": 1994},
    {"id": 9,  "titulo": "Marketa Lazarova",                                           "anio": 1967},
    {"id": 10, "titulo": "Do The Right Thing",                                         "anio": 1989},
    {"id": 11, "titulo": "Citizen Kane",                                               "anio": 1941},
    {"id": 12, "titulo": "Vagabond",                                                   "anio": 1985},
    {"id": 13, "titulo": "Le Samourai",                                                "anio": 1967},
    {"id": 14, "titulo": "Les yeux sans visage",                                       "anio": 1960},
    {"id": 15, "titulo": "Chungking Express",                                          "anio": 1994},
    {"id": 16, "titulo": "Amarcord",                                                   "anio": 1973},
    {"id": 17, "titulo": "Il conformista",                                             "anio": 1970},
    {"id": 18, "titulo": "Shoplifters",                                                "anio": 2018},
    {"id": 19, "titulo": "The Saragossa Manuscript",                                   "anio": 1965},
    {"id": 20, "titulo": "Peeping Tom",                                                "anio": 1960},
    {"id": 21, "titulo": "Gritos y susurros",                                          "anio": 1972},
    {"id": 22, "titulo": "Anatomy of a Murder",                                        "anio": 1959},
    {"id": 23, "titulo": "Jeanne Dielman, 23 Quai Du Commerce 1080, Bruxelles",        "anio": 1975},
    {"id": 24, "titulo": "Poetry",                                                     "anio": 2010},
    {"id": 25, "titulo": "Blue Velvet",                                                "anio": 1986},
    {"id": 26, "titulo": "Network",                                                    "anio": 1976},
    {"id": 27, "titulo": "Beau Travail",                                               "anio": 1999},
    {"id": 28, "titulo": "La Haine",                                                   "anio": 1995},
    {"id": 29, "titulo": "La Maman et la Putain",                                      "anio": 1973},
    {"id": 30, "titulo": "Le Bonheur",                                                 "anio": 1965},
    {"id": 31, "titulo": "Les diaboliques",                                            "anio": 1955},
    {"id": 32, "titulo": "Belle de Jour",                                              "anio": 1967},
    {"id": 33, "titulo": "Indagine su un cittadino al de sopra di ogni sospetto",      "anio": 1970},
    {"id": 34, "titulo": "Perfect Days",                                               "anio": 2023},
    {"id": 35, "titulo": "Welt Am Draht",                                              "anio": 1973},
    {"id": 36, "titulo": "Walkabout",                                                  "anio": 1971},
    {"id": 37, "titulo": "Two Days, One Night",                                        "anio": 2014},
    {"id": 38, "titulo": "Lavoura Arcaica",                                            "anio": 2001},
    {"id": 39, "titulo": "Aquarius",                                                   "anio": 2016},
    {"id": 40, "titulo": "Safe",                                                       "anio": 1995},
    {"id": 41, "titulo": "Anatomie d'une chute",                                       "anio": 2023},
    {"id": 42, "titulo": "Roma città aperta",                                          "anio": 1945},
    {"id": 43, "titulo": "La notte",                                                   "anio": 1961},
    {"id": 44, "titulo": "Hana bi",                                                    "anio": 1997},
    {"id": 45, "titulo": "La calle de la vergüenza",                                   "anio": 1956},
    {"id": 46, "titulo": "Spoorloos",                                                  "anio": 1988},
    {"id": 47, "titulo": "Zimna Wojna",                                                "anio": 2018},
    {"id": 48, "titulo": "If",                                                         "anio": 1968},
    {"id": 49, "titulo": "The Servant",                                                "anio": 1963},
    {"id": 50, "titulo": "The Innocents",                                              "anio": 1961},
    {"id": 51, "titulo": "4 Months, 3 Weeks And 2 Days",                               "anio": 2007},
    {"id": 52, "titulo": "Das Lehrerzimmer",                                           "anio": 2023},
    {"id": 53, "titulo": "Zama",                                                       "anio": 2017},
    {"id": 54, "titulo": "El aura",                                                    "anio": 2005},
    {"id": 55, "titulo": "Arrebato",                                                   "anio": 1979},
    {"id": 56, "titulo": "Teorema",                                                    "anio": 1968},
    {"id": 57, "titulo": "Funeral Parade of Roses",                                    "anio": 1969},
    {"id": 58, "titulo": "Fish Tank",                                                  "anio": 2009},
    {"id": 59, "titulo": "W.R. - Misterije organizma",                                 "anio": 1971},
    {"id": 60, "titulo": "Bacurau",                                                    "anio": 2019},
    {"id": 61, "titulo": "Una mujer fantástica",                                       "anio": 2017},
    {"id": 62, "titulo": "Memoria",                                                    "anio": 2021},
    {"id": 63, "titulo": "Primavera, verano, otoño, invierno... y otra vez primavera", "anio": 2003},
    {"id": 64, "titulo": "Los colonos",                                                "anio": 2023},
    {"id": 65, "titulo": "Gueros",                                                     "anio": 2014},
    {"id": 66, "titulo": "Ghost World",                                                "anio": 2001},
    {"id": 67, "titulo": "An Education",                                               "anio": 2009},
    {"id": 68, "titulo": "La luz incidente",                                           "anio": 2015},
]


# ---------------------------------------------------------------------------
# HELPERS DE TMDB
# ---------------------------------------------------------------------------
def _headers() -> dict:
    if TMDB_READ_TOKEN:
        return {"Authorization": f"Bearer {TMDB_READ_TOKEN}", "accept": "application/json"}
    return {"accept": "application/json"}


def _params_base() -> dict:
    return {} if TMDB_READ_TOKEN else {"api_key": TMDB_API_KEY}


def _validar_credenciales() -> bool:
    if not TMDB_READ_TOKEN and not TMDB_API_KEY:
        print("❌ No hay credenciales de TMDB.")
        print("   Exporta TMDB_READ_TOKEN (v4) o TMDB_API_KEY (v3).")
        return False
    return True


def _get(url: str, params: dict) -> Optional[dict]:
    """GET con reintentos y manejo de errores."""
    for intento in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, headers=_headers(), timeout=10)

            if r.status_code == 429:
                espera = int(r.headers.get("Retry-After", RETRY_DELAY * intento))
                print(f"   ⏳ Rate limit. Esperando {espera}s...")
                time.sleep(espera)
                continue

            r.raise_for_status()
            return r.json()

        except requests.exceptions.Timeout:
            print(f"   ⚠️  Timeout ({intento}/{MAX_RETRIES})")
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Conexión ({intento}/{MAX_RETRIES})")
        except requests.exceptions.HTTPError as e:
            print(f"   ⚠️  HTTP {e} ({intento}/{MAX_RETRIES})")
        except ValueError:
            print("   ⚠️  JSON inválido")
            return None

        if intento < MAX_RETRIES:
            time.sleep(RETRY_DELAY * intento)
    return None


def buscar_pelicula(titulo: str, anio: int) -> Optional[dict]:
    """Busca por título+año; devuelve el primer resultado o None."""
    data = _get(
        f"{BASE_URL}/search/movie",
        {**_params_base(), "query": titulo, "year": anio, "include_adult": "false"},
    )
    if not data:
        return None
    results = data.get("results", [])
    return results[0] if results else None


def obtener_detalles(movie_id: int) -> Optional[dict]:
    """Detalles con título en español y título original."""
    return _get(
        f"{BASE_URL}/movie/{movie_id}",
        {**_params_base(), "language": "es-ES"},
    )


def construir_poster(poster_path: Optional[str]) -> Optional[str]:
    if not poster_path:
        return None
    return f"{IMAGE_BASE}{poster_path}"


# ---------------------------------------------------------------------------
# PROCESO PRINCIPAL
# ---------------------------------------------------------------------------
def procesar() -> list:
    resultado = []
    total = len(PELICULAS)

    for idx, peli in enumerate(PELICULAS, start=1):
        pid     = peli["id"]
        termino = peli["titulo"]
        anio    = peli["anio"]

        print(f"[{idx}/{total}] 🎬 {termino} ({anio})")

        # 1. Búsqueda
        encontrada = buscar_pelicula(termino, anio)
        if not encontrada:
            print("   ❌ No encontrada en TMDB")
            resultado.append({
                "id": pid,
                "titulo": termino,
                "titulo_original": termino,
                "anio": anio,
                "poster": None,
            })
            time.sleep(REQUEST_DELAY)
            continue

        tmdb_id       = encontrada["id"]
        titulo_orig   = encontrada.get("original_title") or encontrada.get("title") or termino
        poster_path   = encontrada.get("poster_path")

        # 2. Detalles en español para título traducido (si existe)
        titulo_es = termino
        detalles  = obtener_detalles(tmdb_id)
        if detalles:
            titulo_es   = detalles.get("title") or titulo_orig
            poster_path = detalles.get("poster_path") or poster_path

        poster_url = construir_poster(poster_path)

        if poster_url:
            print(f"   ✅ {titulo_es}  →  {poster_url}")
        else:
            print(f"   ⚠️  Sin póster: {titulo_es}")

        resultado.append({
            "id": pid,
            "titulo": titulo_es,
            "titulo_original": titulo_orig,
            "anio": anio,
            "poster": poster_url,
        })

        time.sleep(REQUEST_DELAY)

    return resultado


def guardar(resultado: list, ruta: str = OUTPUT_FILE) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Guardado en '{ruta}'")


def main() -> int:
    if not _validar_credenciales():
        return 1

    resultado = procesar()
    guardar(resultado)

    con_poster = sum(1 for r in resultado if r["poster"])
    print(f"\n📊 {con_poster}/{len(resultado)} películas con póster.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido.")
        sys.exit(130)
