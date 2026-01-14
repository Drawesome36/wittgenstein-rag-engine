#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar todas las obras de Wittgenstein del Wittgenstein Project
"""
import requests
from bs4 import BeautifulSoup
import html2text
import os
import time
import re
import sys

# Configurar la salida para UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.wittgensteinproject.org"

# Diccionario con todas las obras organizadas por idioma
OBRAS = {
    "aleman": [
        ("Tagebücher 1914-1916", "/w/index.php/Tageb%C3%BCcher_1914-1916"),
        ("Logisch-philosophische Abhandlung (interactiva)", "/w/index.php/Logisch-philosophische_Abhandlung_(Darstellung_in_Baumstruktur)"),
        ("Logisch-philosophische Abhandlung (estática)", "/w/index.php/Logisch-philosophische_Abhandlung_(statische_Darstellung_in_Baumstruktur)"),
        ("Wörterbuch für Volksschulen", "/w/index.php/W%C3%B6rterbuch_f%C3%BCr_Volksschulen"),
        ("Vortrag über Ethik", "/w/index.php/Vortrag_%C3%BCber_Ethik"),
        ("Bemerkungen über Frazers The Golden Bough", "/w/index.php/Bemerkungen_%C3%BCber_Frazers_%E2%80%9CThe_Golden_Bough%E2%80%9D"),
        ("Philosophische Untersuchungen", "/w/index.php/Philosophische_Untersuchungen"),
        ("Zettel", "/w/index.php/Zettel"),
        ("Bemerkungen über die Farben", "/w/index.php/Bemerkungen_%C3%BCber_die_Farben"),
        ("Über Gewißheit", "/w/index.php/%C3%9Cber_Gewi%C3%9Fheit"),
        ("Vermischte Bemerkungen", "/w/index.php/Vermischte_Bemerkungen"),
    ],
    "ingles": [
        ("Review of P. Coffey, The Science of Logic", "/w/index.php/Review_of_P._Coffey,_%E2%80%9CThe_Science_of_Logic%E2%80%9D"),
        ("Notes on Logic", "/w/index.php/Notes_on_Logic"),
        ("Notes Dictated to G.E. Moore in Norway", "/w/index.php/Notes_Dictated_to_G.E._Moore_in_Norway"),
        ("Tractatus Logico-Philosophicus (interactive)", "/w/index.php/Tractatus_Logico-Philosophicus_(tree-like_view)"),
        ("Tractatus Logico-Philosophicus (static)", "/w/index.php/Tractatus_Logico-Philosophicus_(static_tree-like_view)"),
        ("Some Remarks on Logical Form", "/w/index.php/Some_Remarks_on_Logical_Form"),
        ("Lecture on Ethics", "/w/index.php/Lecture_on_Ethics"),
        ("Letter to the Editor of Mind", "/w/index.php/Letter_to_the_Editor_of_%E2%80%9CMind%E2%80%9D"),
        ("Blue Book", "/w/index.php/Blue_Book"),
        ("Brown Book", "/w/index.php/Brown_Book"),
    ],
    "frances": [
        ("Tractatus logico-philosophicus (interactif)", "/w/index.php/Tractatus_logico-philosophicus_(version_arborescente_interactive)"),
        ("Tractatus logico-philosophicus (statique)", "/w/index.php/Tractatus_logico-philosophicus_(version_arborescente_statique)"),
        ("Une conférence sur l'Ethique", "/w/index.php/Une_conf%C3%A9rence_sur_l%E2%80%99Ethique"),
    ],
    "italiano": [
        ("Recensione di La scienza della logica di P. Coffey", "/w/index.php/Recensione_di_%E2%80%9CLa_scienza_della_logica%E2%80%9D_di_P._Coffey"),
        ("Note sulla logica", "/w/index.php/Note_sulla_logica"),
        ("Note dettate a G.E. Moore in Norvegia", "/w/index.php/Note_dettate_a_G.E._Moore_in_Norvegia"),
        ("Quaderni 1914-1916", "/w/index.php/Quaderni_1914-1916"),
        ("Tractatus logico-philosophicus (interattivo)", "/w/index.php/Tractatus_logico-philosophicus_(visualizzazione_ad_albero)"),
        ("Tractatus logico-philosophicus (statico)", "/w/index.php/Tractatus_logico-philosophicus_(visualizzazione_ad_albero_statica)"),
        ("Carteggio Ludwig-Paul Wittgenstein 1920-1939", "/w/index.php/Carteggio_Ludwig-Paul_Wittgenstein_1920-1939"),
        ("Alcune osservazioni sulla forma logica", "/w/index.php/Alcune_osservazioni_sulla_forma_logica"),
        ("Conferenza sull'etica", "/w/index.php/Conferenza_sull%E2%80%99etica"),
        ("Lettera al direttore di Mind", "/w/index.php/Lettera_al_direttore_di_%E2%80%9CMind%E2%80%9D"),
        ("Osservazioni sul Ramo d'oro di Frazer", "/w/index.php/Osservazioni_sul_%E2%80%9CRamo_d%E2%80%99oro%E2%80%9D_di_Frazer"),
        ("Libro blu", "/w/index.php/Libro_blu"),
        ("Libro marrone", "/w/index.php/Libro_marrone"),
        ("Osservazioni sui colori", "/w/index.php/Osservazioni_sui_colori"),
    ],
    "espanol": [
        ("Reseña, La Ciencia de la Lógica", "/w/index.php/Rese%C3%B1a,_%C2%ABLa_Ciencia_de_la_L%C3%B3gica%C2%BB"),
        ("Tratado lógico-filosófico (interactivo)", "/w/index.php/Tratado_l%C3%B3gico-filos%C3%B3fico_(presentaci%C3%B3n_en_%C3%A1rbol)"),
        ("Tratado lógico-filosófico (estático)", "/w/index.php/Tratado_l%C3%B3gico-filos%C3%B3fico_(presentaci%C3%B3n_est%C3%A1tica_en_%C3%A1rbol)"),
        ("Algunas observaciones sobre la forma lógica", "/w/index.php/Algunas_observaciones_sobre_la_forma_l%C3%B3gica"),
        ("Conferencia sobre Ética", "/w/index.php/Conferencia_sobre_%C3%89tica"),
        ("Observaciones sobre La rama dorada de Frazer", "/w/index.php/Observaciones_sobre_%E2%80%9CLa_rama_dorada%E2%80%9D_de_Frazer"),
        ("Filosofía", "/w/index.php/Filosof%C3%ADa"),
        ("Investigaciones filosóficas (edición A)", "/w/index.php/Investigaciones_filos%C3%B3ficas_(edici%C3%B3n_A)"),
        ("Investigaciones filosóficas (edición B)", "/w/index.php/Investigaciones_filos%C3%B3ficas_(edici%C3%B3n_B)"),
        ("Sobre la certeza", "/w/index.php/Sobre_la_certeza"),
    ],
    "portugues": [
        ("Notas Ditadas a G.E. Moore na Noruega", "/w/index.php/Notas_Ditadas_a_G.E._Moore_na_Noruega"),
        ("Tractatus Logico-Philosophicus (interativo)", "/w/index.php/Tractatus_Logico-Philosophicus_(visualiza%C3%A7%C3%A3o_em_%C3%A1rvore)"),
        ("Observações sobre O ramo de ouro de Frazer", "/w/index.php/Observa%C3%A7%C3%B5es_sobre_%E2%80%9CO_ramo_de_ouro%E2%80%9D_de_Frazer"),
    ],
    "griego": [
        ("Μια διάλεξη για την Ηθική", "/w/index.php/%CE%9C%CE%B9%CE%B1_%CE%B4%CE%B9%CE%AC%CE%BB%CE%B5%CE%BE%CE%B7_%CE%B3%CE%B9%CE%B1_%CF%84%CE%B7%CE%BD_%CE%97%CE%B8%CE%B9%CE%BA%CE%AE"),
    ],
    "rumano": [
        ("Prelegere despre etică", "/w/index.php/Prelegere_despre_etic%C4%83"),
    ],
    "danes": [
        ("Forelæsning om etik", "/w/index.php/Forel%C3%A6sning_om_etik"),
    ],
    "hindi": [
        ("फ़िलोसॉफ़िकल इन्वेस्टिगेशंस", "/w/index.php/%E0%A4%AB%E0%A4%BC%E0%A4%BF%E0%A4%B2%E0%A5%8B%E0%A4%B8%E0%A5%89%E0%A4%AB%E0%A4%BC%E0%A4%BF%E0%A4%95%E0%A4%B2_%E0%A4%87%E0%A4%A8%E0%A5%8D%E0%A4%B5%E0%A5%87%E0%A4%B8%E0%A5%8D%E0%A4%9F%E0%A4%BF%E0%A4%97%E0%A5%87%E0%A4%B6%E0%A4%82%E0%A4%B8"),
        ("ऑन सर्टेन्टि", "/w/index.php/%E0%A4%91%E0%A4%A8_%E0%A4%B8%E0%A4%B0%E0%A5%8D%E0%A4%9F%E0%A5%87%E0%A4%A8%E0%A5%8D%E0%A4%9F%E0%A4%BF"),
    ],
    "arabe": [
        ("مراجعة كتاب علم المنطق لبيتر كوفي", "/w/index.php/%D9%85%D8%B1%D8%A7%D8%AC%D8%B9%D8%A9_%D9%83%D8%AA%D8%A7%D8%A8_%22%D8%B9%D9%84%D9%85_%D8%A7%D9%84%D9%85%D9%86%D8%B7%D9%82%22_%D9%84%D8%A8%D9%8A%D8%AA%D8%B1_%D9%83%D9%88%D9%81%D9%8A"),
        ("مقدمة قاموس المدارس الإبتدائية", "/w/index.php/%D9%85%D9%82%D8%AF%D9%85%D8%A9_%D9%82%D8%A7%D9%85%D9%88%D8%B3_%D8%A7%D9%84%D9%85%D8%AF%D8%A7%D8%B1%D8%B3_%D8%A7%D9%84%D8%A5%D8%A8%D8%AA%D8%AF%D8%A7%D8%A6%D9%8A%D8%A9"),
        ("محاضرة في علم الأخلاق", "/w/index.php/%D9%85%D8%AD%D8%A7%D8%B6%D8%B1%D8%A9_%D9%81%D9%8A_%D8%B9%D9%84%D9%85_%D8%A7%D9%84%D8%A3%D8%AE%D9%84%D8%A7%D9%82"),
        ("Mind رسالة إلى محرر", "/w/index.php/%E2%80%9CMind%E2%80%9D_%D8%B1%D8%B3%D8%A7%D9%84%D8%A9_%D8%A5%D9%84%D9%89_%D9%85%D8%AD%D8%B1%D8%B1"),
    ],
    "turco": [
        ("P. Coffey'in Mantık Bilimi Eseri Üzerine Bir İnceleme", "/w/index.php/P._Coffey%E2%80%99in_%E2%80%9CMant%C4%B1k_Bilimi%E2%80%9D_Eseri_%C3%9Czerine_Bir_%C4%B0nceleme"),
    ]
}


def limpiar_nombre_archivo(nombre):
    """Limpia el nombre del archivo para que sea válido en el sistema de archivos"""
    # Reemplazar caracteres no válidos
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)
    # Limitar longitud
    if len(nombre) > 200:
        nombre = nombre[:200]
    return nombre


def descargar_obra(idioma, titulo, url_relativa):
    """Descarga una obra y la convierte a Markdown"""
    url_completa = BASE_URL + url_relativa

    print(f"Descargando: {titulo} ({idioma})...")

    try:
        # Hacer la petición
        response = requests.get(url_completa, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el contenido principal
        # El contenido principal suele estar en div con id "mw-content-text"
        content_div = soup.find('div', {'id': 'mw-content-text'})

        if not content_div:
            # Intentar con otros selectores comunes
            content_div = soup.find('div', {'class': 'mw-parser-output'})

        if not content_div:
            # Si no encuentra el contenido, usar el body completo
            content_div = soup.find('body')

        if content_div:
            # Remover elementos no deseados (navegación, menús, etc.)
            for elemento in content_div.find_all(['script', 'style', 'nav', 'footer']):
                elemento.decompose()

            # Convertir a Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            h.body_width = 0  # Sin límite de ancho

            markdown = h.handle(str(content_div))

            # Crear nombre de archivo con prefijo de idioma
            nombre_archivo = f"[{idioma}] {limpiar_nombre_archivo(titulo)}.md"
            ruta_archivo = os.path.join("wittgenstein_obras", nombre_archivo)

            # Guardar archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(f"# {titulo}\n\n")
                f.write(f"**Fuente:** {url_completa}\n\n")
                f.write("---\n\n")
                f.write(markdown)

            print(f"[OK] Guardado: {ruta_archivo}")
            return True
        else:
            print(f"[ERROR] No se pudo extraer contenido de: {titulo}")
            return False

    except Exception as e:
        print(f"[ERROR] Error al descargar {titulo}: {str(e)}")
        return False


def main():
    """Función principal"""
    print("=" * 60)
    print("Descargando obras de Wittgenstein del Wittgenstein Project")
    print("=" * 60)
    print()

    total_obras = sum(len(obras) for obras in OBRAS.values())
    contador = 0
    exitosas = 0
    fallidas = 0

    for idioma, obras in OBRAS.items():
        print(f"\n{'='*60}")
        print(f"Idioma: {idioma.upper()} ({len(obras)} obras)")
        print(f"{'='*60}\n")

        for titulo, url in obras:
            contador += 1
            print(f"[{contador}/{total_obras}] ", end="")

            if descargar_obra(idioma, titulo, url):
                exitosas += 1
            else:
                fallidas += 1

            # Pausa breve para no sobrecargar el servidor
            time.sleep(1)

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Total de obras: {total_obras}")
    print(f"Descargadas exitosamente: {exitosas}")
    print(f"Fallidas: {fallidas}")
    print("\nTodas las obras se han guardado en la carpeta 'wittgenstein_obras/'")
    print("=" * 60)


if __name__ == "__main__":
    main()
