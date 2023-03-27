# Hackathon Master industrue 4.0 2023



Ce hackathon deep learning propose de s'attaquer à un problème différent des régressions classique, il s'agira de prédire les réglages optimaux pour  une ligne industrielle.

On possède un jeu de donnée pour le fonctionnement d'un four couplé à un convoyeur

<img src="/Users/adrienhenry/Downloads/commentaires/schema_four.png" style="zoom:25%;" />

Un objet est transporté sur le convoyeur et selon sa vitesse et la température du four il reçoit une quantité plus ou moins grande d'énergie. Sa qualité finale sera bonne lorsque le produit recoit une quantité optimale d'énergie $E_0$ (propre à l'objet). Si le produit reçoit plus ou moins d'énergie que $E_0$, sa qualité sera moins bonne. En tant que technicien(ne) de la ligne, on peut régler la vitesse et la température de la ligne.

## Données

Le dataset original contient des donnée d'observation aléatoire de la ligne. La plupart ne sont pas très bonne car aucune expertise n'y a été apportée. Ces données peuvent être utilisées comme bon vous semble.

## Objectif

Créer un sytème de recommandation qui en fonction de l'historique des données jusqu'au point présent nous suggère un couple de réglages `{temperature_setting: ?, speed_setting: ?}`.

L'algo de recommendation pourra être évalué sur une "vrai usine"(simulatio numérique) en fonctionnement à condition de le packager de la facon suivante:

```python
# algo.py

def run_reco(history):
    # ... Your algo here ...
    reco = {
        "speed_setting": # my speed reco,
        "temperature_setting": # my temperature reco,
    }
    return reco
```

Le script `algo.py` peut éventuellement être accompagné de dépendances (par ex: poids et architecture d'un réseau de neuronnes).

## Évaluation de l'algorithme

L'algorithme sera évalué sur 20 + 200 recommendations

- Les 20 premiers points servent d'échauffement pour l'algorithme et ne sont pas pris en compte dans le score
- Pour les 200 points suivants, la qualité est évaluée pour chaque produit et le score de l'algorithme correspond à la moyenne des qualités

## Rapport

Le rapport est la partie la plus importante du hackathon et doit être rédigé avec soin:

- Les méthodes et algorithmes utilés doivent être décrits. Et leur choix doit être motivé.
- Les résultats doivent êtres commentés.
- Il est important de bien mettre en avant ce que vous avez fait même si certaines méthode n'ont pas fonctionnées et ne font pas partie de l'algorithme final.
- Il est important qu'en lisant le rapport on comprennent votre stratégie pour résoudre le problème
- Toutes les figure doivent avoir un label pour les abscisses et les ordonnées 