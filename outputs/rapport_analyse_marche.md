# Rapport d’analyse de marché (A à Z)

## 1) Portée et qualité des données

- **Fichier source analysé** : `Suivi_Des_Marché.xlsx`.
- **Nombre de fiches collectées** : **62**.
- **Marchés couverts** : Bénéna (22), San (20), Mandiakuy (20).
- **Période observée** : Janvier à Mars 2026 (la table contient 2 mois utiles: 2026-01 et 2026-03 pour les prix).

## 2) Analyse des prix : niveau actuel et moyenne

Les moyennes de prix (FCFA/kg) et leurs variations sont dans `outputs/resume_prix.csv`.

| Denrée | Prix moyen actuel | Prix moyen mois précédent | Variation moyenne % | Tendance |
|---|---:|---:|---:|---|
| Maïs | 169.9 | 161.4 | 6.0% | Hausse |
| Sucre | 541.1 | 534.7 | 1.2% | Stable |
| Riz importé | 459.4 | 446.9 | 3.0% | Stable |
| Riz local | 386.1 | 378.1 | 2.3% | Stable |
| Mil | 177.7 | 169.6 | 5.5% | Hausse |
| Poisson | 3175.8 | 3001.1 | 18.8% | Hausse |
| Lait | 2175.8 | 2138.7 | 1.6% | Stable |
| Sorgho | 176.2 | 165.6 | 6.8% | Hausse |
| Huile végétale | 985.5 | 1012.1 | -2.2% | Stable |
| Haricot/Niébé | 426.2 | 405.6 | 4.8% | Stable |
| Viande | 3237.9 | 3080.7 | 7.4% | Hausse |

### Lecture décisionnelle rapide

- **Poisson** : variation moyenne **18.8%** (prix actuel moyen 3176 FCFA/kg).
- **Viande** : variation moyenne **7.4%** (prix actuel moyen 3238 FCFA/kg).
- **Sorgho** : variation moyenne **6.8%** (prix actuel moyen 176 FCFA/kg).
- **Maïs** : variation moyenne **6.0%** (prix actuel moyen 170 FCFA/kg).

## 3) Tendance mensuelle : prix stables ou non ?

- **Indice panier moyen** : 1047.1 (en 2026-01) → 1086.7 (en 2026-03) soit **3.8%**.
- Les denrées les plus volatiles sont principalement : **Poisson**, **Viande**, **Sorgho**.
- Les denrées relativement stables : **Sucre**, **Riz local**, **Lait** (variation moyenne proche de 0 à +2%).

## 4) Disponibilité, approvisionnement et état des stocks

- **Ruptures de stock signalées** : 0/62 (**0.0%**).
- **Denrées disponibles sur le marché** : 61/62 (**98.4%**).
- **Produits souvent jugés difficiles d’accès (ménages vulnérables)** :
  - Poisson: 62 mentions
  - Viande: 62 mentions
  - Lait: 62 mentions
  - Riz: 55 mentions
  - Huile: 43 mentions
  - Sucre: 26 mentions
- Conclusion stock/approvisionnement : **pas de rupture générale**, mais **accessibilité économique difficile** sur des produits protéinés (poisson, viande, lait) et le riz.

## 5) Fonctionnement du marché (offre et demande)

- **Hausse de la demande signalée par les commerçants** : 4/62 (**6.5%**).
- **Marché accessible toute la semaine** : 23/62 (**37.1%**).
- Lecture : l’**offre est présente**, mais la **demande solvable est contrainte** (pouvoir d’achat faible), ce qui explique le ressenti de cherté malgré disponibilité des produits.

## 6) Recommandations opérationnelles (simples et actionnables)

1. **Suivre en priorité Poisson, Viande, Sorgho** (fortes variations) avec alertes mensuelles.
2. **Mettre en place un suivi hebdomadaire ciblé** sur les marchés non accessibles en continu.
3. **Protéger le pouvoir d’achat** des ménages vulnérables (cash/transferts ciblés sur panier prioritaire).
4. **Travailler la chaîne d’approvisionnement** (transport/sécurité) pour limiter les pics de prix.
5. **Institutionnaliser ce tableau de bord** : mise à jour mensuelle des CSV + graphes pour la décision.

## 7) Graphiques produits

- `outputs/charts/graph_01_prix_moyens.svg`
- `outputs/charts/graph_02_variation_pct.svg`
- `outputs/charts/graph_03_indicateurs_disponibilite.svg`
- `outputs/charts/graph_04_marches_couverts.svg`
- `outputs/charts/graph_05_tendance_panier.svg`

## 8) Fichiers livrables

- Rapport interprété : `outputs/rapport_analyse_marche.md`
- Tableau prix : `outputs/resume_prix.csv`
- Indicateurs marché : `outputs/indicateurs_marche.csv`
- Produits difficiles : `outputs/produits_difficiles.csv`
- Tendance mensuelle : `outputs/tendance_mensuelle.csv`