"""
WebDOC-kääntäjä MyMemory API:lla (ilmainen taso: 100 kääntöä/päivä).

Tukee erityisesti Suomi ↔ Englanti -käännöstä.
Oletus on englanninkielinen käännös, ja suomenkieliset viestit näytetään,
jos päivittäisen ilmaisen käännösladan käyttö on päällä.

Käyttö:
    python tools/translator.py --text "Hei maailma" --lang fi --to en
    python tools/translator.py --input webdoc.md --lang fi --to en --output webdoc-en.md
"""

import sys

# Aseta UTF-8 Windows-käytössä (emojien tuki)
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")

import argparse
import os
import sys
import time
import json
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

# Lataa .env-tiedosto (jos olemassa)
load_dotenv()


class MyMemoryTranslator:
    """
    Kääntäjä MyMemory API:lla.
    """

    BASE_URL = "https://api.mymemory.translated.net/get"
    DEFAULT_DELAY = 1.0  # sekuntia pyyntöjen välissä (rajoituksen välttämiseksi)

    def __init__(self, api_key: Optional[str] = None):
        """
        Alustaa kääntäjän.

        Args:
            api_key: MyMemory API-avain (valiton — ilmainen taso toimii ilman avainta)
        """
        self.api_key = api_key or os.getenv("MYMEMORY_API_KEY")
        self._last_request = 0.0

    def _wait_if_needed(self):
        """Vältetään liiallista API-kutsua."""
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.DEFAULT_DELAY:
            time.sleep(self.DEFAULT_DELAY - elapsed)
        self._last_request = time.time()

    def translate(
        self,
        text: str,
        lang_from: str = "fi",
        lang_to: str = "en",
    ) -> str:
        """
        Kääntää annetun tekstin.

        Args:
            text: Käännettävä teksti
            lang_from: Lähteiskieli (oletus: 'fi')
            lang_to: Kohdekieli (oletus: 'en')

        Returns:
            Käännetty teksti
        """
        if not text.strip():
            return text

        params = {
            "q": text,
            "langpair": f"{lang_from}|{lang_to}",
        }
        if self.api_key:
            params["key"] = self.api_key

        max_retries = 3
        for attempt in range(max_retries):
            self._wait_if_needed()

            try:
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                # Käsittele 429-virhe: odota 10 sek ja yritä uudelleen
                if response.status_code == 429 and attempt < max_retries - 1:
                    print("⚠️  Raja ylitetty (429). Odotetaan 10 sekuntia ja yritetään uudelleen...", file=sys.stderr)
                    print("ℹ.  Suositus: lisää MYMEMORY_API_KEY .env-tiedostoon lisätäksesi kiistamukaisuuden (5000 kääntöä/päivä).", file=sys.stderr)
                    time.sleep(10)
                    continue
                response.raise_for_status()
                data = response.json()

                if "responseData" in data and "translatedText" in data["responseData"]:
                    return data["responseData"]["translatedText"]

                # Tarkista virhe
                if "responseStatus" in data and data["responseStatus"] != 200:
                    self._print_error(data)
                    return text

                # Fallback: palauta alkuperäinen teksti
                return text

            except requests.RequestException as e:
                self._print_connection_error(e)
                return text
            except json.JSONDecodeError:
                return text

        # Kaikki yritykset lopuivat — palauta alkuperäinen teksti
        return text

    def _print_error(self, data: dict):
        """Tulostaa API-virheen."""
        status = data.get("responseStatus", "tuntematon")
        message = data.get("responseDetails", "Tuntematon virhe")

        if status == 429 or "rate limit" in str(message).lower():
            print("⚠️  Liiallista käännöstä! Kutsut ovat ylikuormittavia.", file=sys.stderr)
            print("💡 Vinkki: Ota API-avain käyttöön lisäämällä MYMEMORY_API_KEY=.env-tiedostoon.", file=sys.stderr)
            print(f"   Ilmainen taso sallii 100 kääntöä/päivä ({self.api_key} avaimella 5000/päivä).", file=sys.stderr)
        else:
            print(f"⚠️  Käännösvirhe ({status}): {message}", file=sys.stderr)

    def _print_connection_error(self, error: Exception):
        """Tulostaa yhteyden virheen."""
        print(f"⚠️  Yhteyden virhe: {error}", file=sys.stderr)
        print("💡 Tarkista verkkoyhteys.", file=sys.stderr)


def translate_file(
    input_path: str,
    output_path: str,
    lang_from: str = "fi",
    lang_to: str = "en",
    show_finnish: bool = True,
) -> bool:
    """
    Kääntää koko tiedoston.

    Args:
        input_path: Lähdetiedoston polku
        output_path: Kohdetiedoston polku
        lang_from: Lähteiskieli (oletus: 'fi')
        lang_to: Kohdekieli (oletus: 'en')
        show_finnish: Näytetäänkö suomenkieliset viestit

    Returns:
        Onnistuuko tallennus
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Tiedostoa ei löydy: {input_path}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Lukuvirhe: {e}", file=sys.stderr)
        return False

    # Jaa riveihin ja käännä (säilytetään muotoilu)
    lines = content.split("\n")
    translated_lines = []

    for i, line in enumerate(lines):
        # Ohita käännettävät rivit (markdown-otsikot, koodiblokit)
        if line.strip().startswith("```") or line.strip().startswith("|"):
            translated_lines.append(line)
            continue

        # Käännä muut rivit
        translated = translator.translate(line, lang_from, lang_to)
        translated_lines.append(translated)

        # Näytä edistymisbar Finnish-tilassa
        if show_finnish and (i % 10 == 0 or i == len(lines) - 1):
            progress = (i + 1) / len(lines) * 100
            print(f"✅ Käännetään: {progress:.0f}% suomenkielisesti (API-avain: {'✅' if translator.api_key else '❌'})")

    translated_content = "\n".join(translated_lines)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated_content)
    except Exception as e:
        print(f"❌ Tallennusvirhe: {e}", file=sys.stderr)
        return False

    print(f"✅ Käännös suoritettu! Tiedosto tallennettu: {output_path}")
    return True


# Globaali instanssi (CLI-käytettävänä)
translator = MyMemoryTranslator()


def main():
    """Pääohjelma — CLI-käsitoitus MyMemory-käännökselle."""
    parser = argparse.ArgumentParser(
        description="WebDOC-kääntäjä MyMemory API:lla (ilmainen: 100 kääntöä/päivä)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Esimerkit:
  %(prog)s --text "Hei maailma" --lang fi --to en
  %(prog)s --input webdoc.md --output webdoc-en.md --lang fi --to en
  %(prog)s --input webdoc.md --output webdoc-en.md --reverse  # fi -> en oletuksena
""",
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Käännettävä teksti suoraan komentoriviltä"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Lähdetiedoston polku (esim. webdoc.md)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Kohdetiedoston polku"
    )
    parser.add_argument(
        "--lang", "-f",
        type=str,
        default="fi",
        choices=["fi", "en"],
        help="Lähteiskieli (oletus: fi = suomi)"
    )
    parser.add_argument(
        "--to", "-t",
        type=str,
        default="en",
        choices=["fi", "en"],
        help="Kohdekieli (oletus: en = englanti)"
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Käännä suoraan suomi -> englanti (oletus)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Ylikirjoita API-avain (oletuksena: MYMEMORY_API_KEY-ympäristömuuttuja)"
    )

    args = parser.parse_args()

    # Jos --reverse on asetettu, käytetään oletus-suuntaa (fi -> en)
    if args.reverse:
        lang_from, lang_to = "fi", "en"
    else:
        lang_from, lang_to = args.lang, args.to

    # Käytetään annettua API-avainta tai ympäristömuuttujaa
    global translator
    api_key = args.api_key or os.getenv("MYMEMORY_API_KEY")
    translator = MyMemoryTranslator(api_key=api_key)

    # Näytä suomenkielinen status (jos ilmainen taso käytössä)
    has_api_key = bool(translator.api_key)
    if not has_api_key:
        print("ℹ️  Käytetään ilmaista MyMemory-tasoa (100 kääntöä/päivä).")
        print("ℹ.  Suositus: lisää MYMEMORY_API_KEY .env-tiedostoon lisätäksesi kiistamukaisuuden (5000/päivä).")

    # Käännä yksittäinen teksti
    if args.text:
        result = translator.translate(args.text, lang_from, lang_to)
        print(f"🔤 {lang_from} -> {lang_to}:")
        print(f"📝 {args.text}")
        print(f"🎯 {result}")
        return

    # Käännä tiedosto
    if args.input:
        if not args.output:
            base = Path(args.input).stem
            ext = Path(args.input).suffix
            args.output = f"{base}-{lang_to}{ext}"

        success = translate_file(
            input_path=args.input,
            output_path=args.output,
            lang_from=lang_from,
            lang_to=lang_to,
            show_finnish=True,  # Näytetään suomenkielinen edistymisviesti
        )
        if not success:
            sys.exit(1)
        return

    # Jos ei argumentteja, näytetään ohjeet
    if not any([args.text, args.input]):
        parser.print_help()


if __name__ == "__main__":
    main()