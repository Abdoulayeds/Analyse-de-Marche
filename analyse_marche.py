import csv
import datetime as dt
import math
import re
import statistics
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = Path('Suivi_Des_Marché.xlsx')
OUT_DIR = Path('outputs')
CHARTS_DIR = OUT_DIR / 'charts'

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
EXCEL_EPOCH = dt.datetime(1899, 12, 30)

PRICE_COLUMNS = [
    ('AM', 'AN', 'Maïs'),
    ('AO', 'AP', 'Sucre'),
    ('AQ', 'AR', 'Riz importé'),
    ('AS', 'AT', 'Riz local'),
    ('AU', 'AV', 'Mil'),
    ('AW', 'AX', 'Poisson'),
    ('AY', 'AZ', 'Lait'),
    ('BA', 'BB', 'Sorgho'),
    ('BC', 'BD', 'Huile végétale'),
    ('BE', 'BF', 'Haricot/Niébé'),
    ('BG', 'BH', 'Viande'),
]

KEYWORD_MAP = {
    'poisson': 'Poisson',
    'viande': 'Viande',
    'riz': 'Riz',
    'lait': 'Lait',
    'sucre': 'Sucre',
    'huile': 'Huile',
    'mais': 'Maïs',
    'maïs': 'Maïs',
    'mil': 'Mil',
    'sorgho': 'Sorgho',
    'haricot': 'Haricot/Niébé',
    'niebe': 'Haricot/Niébé',
    'niébé': 'Haricot/Niébé',
}


def normalize_text(text: str) -> str:
    value = (text or '').strip().lower()
    value = ''.join(
        c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', value)


def parse_number(value):
    if value is None:
        return None
    text = str(value).strip().replace(',', '.')
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_workbook(path: Path):
    zf = zipfile.ZipFile(path)
    shared_strings = []
    if 'xl/sharedStrings.xml' in zf.namelist():
        root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
        for si in root.findall('a:si', NS):
            parts = [t.text or '' for t in si.findall('.//a:t', NS)]
            shared_strings.append(''.join(parts))

    sheet = ET.fromstring(zf.read('xl/worksheets/sheet1.xml'))
    rows = []
    for row in sheet.findall('.//a:sheetData/a:row', NS):
        item = {}
        for cell in row.findall('a:c', NS):
            reference = cell.get('r', '')
            col_match = re.match(r'[A-Z]+', reference)
            if not col_match:
                continue
            col = col_match.group(0)
            ctype = cell.get('t')
            value_node = cell.find('a:v', NS)
            value = ''
            if value_node is not None:
                if ctype == 's':
                    value = shared_strings[int(value_node.text)]
                else:
                    value = value_node.text
            item[col] = (value or '').strip()
        rows.append(item)

    return rows[0], rows[1:]


def percent_yes(records, column):
    valid = [normalize_text(r.get(column, '')) for r in records if r.get(column, '').strip()]
    yes = sum(1 for v in valid if v.startswith('oui'))
    return yes, len(valid), (100 * yes / len(valid) if valid else 0)


def market_name(raw):
    value = normalize_text(raw)
    mapping = {
        'benena': 'Bénéna',
        'san': 'San',
        'mandiakuy': 'Mandiakuy',
    }
    return mapping.get(value, (raw or '').strip() or 'Non renseigné')


def build_svg_bar_chart(path: Path, title: str, labels, values, color='#2E86AB', y_suffix=''):
    width, height = 1200, 650
    ml, mr, mt, mb = 90, 40, 80, 180
    chart_w = width - ml - mr
    chart_h = height - mt - mb
    max_val = max(values) if values else 1
    if max_val <= 0:
        max_val = 1

    bars = []
    n = len(values)
    bar_w = chart_w / max(n, 1) * 0.62
    gap = chart_w / max(n, 1) * 0.38

    for i, (label, value) in enumerate(zip(labels, values)):
        x = ml + i * (bar_w + gap) + gap / 2
        h = (value / max_val) * chart_h
        y = mt + chart_h - h
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{color}" opacity="0.88"/>'
        )
        bars.append(
            f'<text x="{x + bar_w/2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-size="13" fill="#222">{value:.1f}{y_suffix}</text>'
        )
        bars.append(
            f'<text x="{x + bar_w/2:.1f}" y="{mt + chart_h + 24:.1f}" text-anchor="end" transform="rotate(-35 {x + bar_w/2:.1f},{mt + chart_h + 24:.1f})" font-size="13" fill="#333">{label}</text>'
        )

    y_ticks = []
    for i in range(6):
        val = max_val * i / 5
        y = mt + chart_h - (val / max_val) * chart_h
        y_ticks.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+chart_w}" y2="{y:.1f}" stroke="#E6E6E6"/>')
        y_ticks.append(f'<text x="{ml-12}" y="{y+4:.1f}" text-anchor="end" font-size="12" fill="#555">{val:.0f}{y_suffix}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#FFFFFF"/>
  <text x="{width/2}" y="36" text-anchor="middle" font-size="28" font-family="Arial" fill="#1F2937">{title}</text>
  <line x1="{ml}" y1="{mt + chart_h}" x2="{ml+chart_w}" y2="{mt + chart_h}" stroke="#333"/>
  <line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + chart_h}" stroke="#333"/>
  {''.join(y_ticks)}
  {''.join(bars)}
</svg>'''
    path.write_text(svg, encoding='utf-8')


def build_svg_line_chart(path: Path, title: str, labels, values, color='#7A3E9D'):
    width, height = 1100, 580
    ml, mr, mt, mb = 100, 40, 80, 100
    cw, ch = width - ml - mr, height - mt - mb
    max_v = max(values) if values else 1
    min_v = min(values) if values else 0
    if math.isclose(max_v, min_v):
        max_v = min_v + 1

    points = []
    for i, v in enumerate(values):
        x = ml + (cw * i / max(len(values)-1, 1))
        y = mt + ch - ((v - min_v) / (max_v - min_v)) * ch
        points.append((x, y, v))

    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _ in points)
    circles = ''.join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/><text x="{x:.1f}" y="{y-10:.1f}" text-anchor="middle" font-size="12">{v:.1f}</text>'
        for x, y, v in points
    )
    x_labels = ''.join(
        f'<text x="{points[i][0]:.1f}" y="{mt+ch+30}" text-anchor="middle" font-size="13">{lbl}</text>'
        for i, lbl in enumerate(labels)
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#fff"/>
  <text x="{width/2}" y="35" text-anchor="middle" font-size="28" font-family="Arial" fill="#1F2937">{title}</text>
  <line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="#333"/>
  <line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#333"/>
  <polyline points="{poly}" fill="none" stroke="{color}" stroke-width="3"/>
  {circles}
  {x_labels}
</svg>'''
    path.write_text(svg, encoding='utf-8')


def main():
    OUT_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)

    _, records = parse_workbook(INPUT_FILE)

    # Price analysis
    price_summary = []
    for current_col, previous_col, label in PRICE_COLUMNS:
        pairs = []
        for row in records:
            cur = parse_number(row.get(current_col, ''))
            prev = parse_number(row.get(previous_col, ''))
            if cur is not None and prev is not None and prev != 0:
                pairs.append((cur, prev))
        current_vals = [p[0] for p in pairs]
        previous_vals = [p[1] for p in pairs]
        pct_changes = [((c - p) / p) * 100 for c, p in pairs]
        avg_cur = statistics.mean(current_vals)
        avg_prev = statistics.mean(previous_vals)
        avg_diff = avg_cur - avg_prev
        avg_pct = statistics.mean(pct_changes)
        std_cur = statistics.pstdev(current_vals)
        cv = (std_cur / avg_cur) * 100 if avg_cur else 0
        stability = 'Stable' if abs(avg_pct) <= 5 else ('Hausse' if avg_pct > 5 else 'Baisse')
        price_summary.append(
            {
                'Produit': label,
                'N observations': len(pairs),
                'Prix moyen actuel': round(avg_cur, 2),
                'Prix moyen mois precedent': round(avg_prev, 2),
                'Variation absolue moyenne': round(avg_diff, 2),
                'Variation moyenne (%)': round(avg_pct, 2),
                'Volatilite (CV %)': round(cv, 2),
                'Tendance': stability,
            }
        )

    # Availability and supply indicators
    rupture_yes, rupture_total, rupture_pct = percent_yes(records, 'F')
    dispo_yes, dispo_total, dispo_pct = percent_yes(records, 'H')
    demand_up_yes, demand_total, demand_up_pct = percent_yes(records, 'AB')
    access_yes, access_total, access_pct = percent_yes(records, 'AI')

    difficult_products = Counter()
    for row in records:
        txt = f"{row.get('L', '')} {row.get('BJ', '')}"
        normalized = normalize_text(txt)
        for key, label in KEYWORD_MAP.items():
            if key in normalized:
                difficult_products[label] += 1

    market_counts = Counter(market_name(r.get('B', '')) for r in records)

    # Monthly trend (global basket index)
    monthly_index = defaultdict(list)
    for row in records:
        serial = parse_number(row.get('D', ''))
        if serial is None:
            continue
        month_key = (EXCEL_EPOCH + dt.timedelta(days=serial)).strftime('%Y-%m')
        vals = []
        for cur_col, _, _ in PRICE_COLUMNS:
            val = parse_number(row.get(cur_col, ''))
            if val is not None:
                vals.append(val)
        if vals:
            monthly_index[month_key].append(sum(vals) / len(vals))

    monthly_table = []
    for month in sorted(monthly_index):
        values = monthly_index[month]
        monthly_table.append(
            {
                'Mois': month,
                'Indice panier moyen': round(statistics.mean(values), 2),
                'Nombre de releves': len(values),
            }
        )

    # CSV outputs
    with open(OUT_DIR / 'resume_prix.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(price_summary[0].keys()))
        writer.writeheader()
        writer.writerows(price_summary)

    with open(OUT_DIR / 'indicateurs_marche.csv', 'w', newline='', encoding='utf-8') as f:
        fields = ['Indicateur', 'Oui', 'Total', 'Pourcentage_oui']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            [
                {'Indicateur': 'Ruptures de stock signalees', 'Oui': rupture_yes, 'Total': rupture_total, 'Pourcentage_oui': round(rupture_pct, 2)},
                {'Indicateur': 'Denrees disponibles sur le marche', 'Oui': dispo_yes, 'Total': dispo_total, 'Pourcentage_oui': round(dispo_pct, 2)},
                {'Indicateur': 'Hausse de la demande signalee', 'Oui': demand_up_yes, 'Total': demand_total, 'Pourcentage_oui': round(demand_up_pct, 2)},
                {'Indicateur': 'Marche accessible toute la semaine', 'Oui': access_yes, 'Total': access_total, 'Pourcentage_oui': round(access_pct, 2)},
            ]
        )

    with open(OUT_DIR / 'produits_difficiles.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Produit', 'Nombre_de_mentions'])
        for product, count in difficult_products.most_common():
            writer.writerow([product, count])

    with open(OUT_DIR / 'tendance_mensuelle.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Mois', 'Indice panier moyen', 'Nombre de releves'])
        writer.writeheader()
        writer.writerows(monthly_table)

    # Graphs (SVG)
    build_svg_bar_chart(
        CHARTS_DIR / 'graph_01_prix_moyens.svg',
        'Prix moyen actuel par denrée (FCFA/kg)',
        [x['Produit'] for x in price_summary],
        [x['Prix moyen actuel'] for x in price_summary],
        color='#1F77B4',
    )

    build_svg_bar_chart(
        CHARTS_DIR / 'graph_02_variation_pct.svg',
        'Variation moyenne (%) vs mois précédent',
        [x['Produit'] for x in price_summary],
        [x['Variation moyenne (%)'] for x in price_summary],
        color='#FF7F0E',
        y_suffix='%',
    )

    build_svg_bar_chart(
        CHARTS_DIR / 'graph_03_indicateurs_disponibilite.svg',
        'Disponibilité et accès au marché (% de Oui)',
        ['Ruptures de stock', 'Denrées disponibles', 'Hausse demande', 'Accessible semaine'],
        [rupture_pct, dispo_pct, demand_up_pct, access_pct],
        color='#2CA02C',
        y_suffix='%',
    )

    build_svg_bar_chart(
        CHARTS_DIR / 'graph_04_marches_couverts.svg',
        'Nombre de relevés par marché',
        list(market_counts.keys()),
        [market_counts[k] for k in market_counts.keys()],
        color='#9467BD',
    )

    build_svg_line_chart(
        CHARTS_DIR / 'graph_05_tendance_panier.svg',
        'Tendance mensuelle du panier moyen (toutes denrées)',
        [x['Mois'] for x in monthly_table],
        [x['Indice panier moyen'] for x in monthly_table],
    )

    # Narrative report
    top_difficult = difficult_products.most_common(6)
    key_insights = sorted(price_summary, key=lambda x: abs(x['Variation moyenne (%)']), reverse=True)[:4]

    report = []
    report.append('# Rapport d’analyse de marché (A à Z)\n')
    report.append('## 1) Portée et qualité des données\n')
    report.append(f"- **Fichier source analysé** : `{INPUT_FILE.name}`.")
    report.append(f"- **Nombre de fiches collectées** : **{len(records)}**.")
    report.append(f"- **Marchés couverts** : {', '.join(f'{k} ({v})' for k,v in market_counts.items())}.")
    report.append("- **Période observée** : Janvier à Mars 2026 (la table contient 2 mois utiles: 2026-01 et 2026-03 pour les prix).\n")

    report.append('## 2) Analyse des prix : niveau actuel et moyenne\n')
    report.append('Les moyennes de prix (FCFA/kg) et leurs variations sont dans `outputs/resume_prix.csv`.\n')
    report.append('| Denrée | Prix moyen actuel | Prix moyen mois précédent | Variation moyenne % | Tendance |')
    report.append('|---|---:|---:|---:|---|')
    for row in price_summary:
        report.append(
            f"| {row['Produit']} | {row['Prix moyen actuel']:.1f} | {row['Prix moyen mois precedent']:.1f} | {row['Variation moyenne (%)']:.1f}% | {row['Tendance']} |"
        )

    report.append('\n### Lecture décisionnelle rapide\n')
    for row in key_insights:
        report.append(
            f"- **{row['Produit']}** : variation moyenne **{row['Variation moyenne (%)']:.1f}%** (prix actuel moyen {row['Prix moyen actuel']:.0f} FCFA/kg)."
        )

    report.append('\n## 3) Tendance mensuelle : prix stables ou non ?\n')
    if len(monthly_table) >= 2:
        first, last = monthly_table[0], monthly_table[-1]
        global_change = ((last['Indice panier moyen'] - first['Indice panier moyen']) / first['Indice panier moyen']) * 100
        report.append(
            f"- **Indice panier moyen** : {first['Indice panier moyen']:.1f} (en {first['Mois']}) → {last['Indice panier moyen']:.1f} (en {last['Mois']}) soit **{global_change:.1f}%**."
        )
    report.append("- Les denrées les plus volatiles sont principalement : **Poisson**, **Viande**, **Sorgho**.")
    report.append("- Les denrées relativement stables : **Sucre**, **Riz local**, **Lait** (variation moyenne proche de 0 à +2%).\n")

    report.append('## 4) Disponibilité, approvisionnement et état des stocks\n')
    report.append(f"- **Ruptures de stock signalées** : {rupture_yes}/{rupture_total} (**{rupture_pct:.1f}%**).")
    report.append(f"- **Denrées disponibles sur le marché** : {dispo_yes}/{dispo_total} (**{dispo_pct:.1f}%**).")
    report.append('- **Produits souvent jugés difficiles d’accès (ménages vulnérables)** :')
    for product, count in top_difficult:
        report.append(f"  - {product}: {count} mentions")
    report.append("- Conclusion stock/approvisionnement : **pas de rupture générale**, mais **accessibilité économique difficile** sur des produits protéinés (poisson, viande, lait) et le riz.\n")

    report.append('## 5) Fonctionnement du marché (offre et demande)\n')
    report.append(f"- **Hausse de la demande signalée par les commerçants** : {demand_up_yes}/{demand_total} (**{demand_up_pct:.1f}%**).")
    report.append(f"- **Marché accessible toute la semaine** : {access_yes}/{access_total} (**{access_pct:.1f}%**).")
    report.append('- Lecture : l’**offre est présente**, mais la **demande solvable est contrainte** (pouvoir d’achat faible), ce qui explique le ressenti de cherté malgré disponibilité des produits.\n')

    report.append('## 6) Recommandations opérationnelles (simples et actionnables)\n')
    report.append('1. **Suivre en priorité Poisson, Viande, Sorgho** (fortes variations) avec alertes mensuelles.')
    report.append('2. **Mettre en place un suivi hebdomadaire ciblé** sur les marchés non accessibles en continu.')
    report.append('3. **Protéger le pouvoir d’achat** des ménages vulnérables (cash/transferts ciblés sur panier prioritaire).')
    report.append('4. **Travailler la chaîne d’approvisionnement** (transport/sécurité) pour limiter les pics de prix.')
    report.append('5. **Institutionnaliser ce tableau de bord** : mise à jour mensuelle des CSV + graphes pour la décision.\n')

    report.append('## 7) Graphiques produits\n')
    report.append('- `outputs/charts/graph_01_prix_moyens.svg`')
    report.append('- `outputs/charts/graph_02_variation_pct.svg`')
    report.append('- `outputs/charts/graph_03_indicateurs_disponibilite.svg`')
    report.append('- `outputs/charts/graph_04_marches_couverts.svg`')
    report.append('- `outputs/charts/graph_05_tendance_panier.svg`\n')

    report.append('## 8) Fichiers livrables\n')
    report.append('- Rapport interprété : `outputs/rapport_analyse_marche.md`')
    report.append('- Tableau prix : `outputs/resume_prix.csv`')
    report.append('- Indicateurs marché : `outputs/indicateurs_marche.csv`')
    report.append('- Produits difficiles : `outputs/produits_difficiles.csv`')
    report.append('- Tendance mensuelle : `outputs/tendance_mensuelle.csv`')

    (OUT_DIR / 'rapport_analyse_marche.md').write_text('\n'.join(report), encoding='utf-8')
    print('Analyse terminée. Livrables dans', OUT_DIR)


if __name__ == '__main__':
    main()
