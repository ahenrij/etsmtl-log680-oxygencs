# Configuration du script pre-commit

Pour assurer la qualité du code et le respect des conventions, il est recommandé de configurer un script pre-commit dans votre projet. Ce script sera exécuté automatiquement avant chaque commit et effectuera des vérifications pour détecter d'éventuelles erreurs ou violations de style.

## Déplacement du script pre-commit

1. Tout d'abord, localisez le script pre-commit dans le dossier racine de ce projet.

2. Installez les dépendances 
    ```bash
    pip install pylint black
    ```

3. Copiez ce script dans le dossier .git/hooks de votre projet. Assurez-vous de renommer le script en "pre-commit" (sans extension).

4. Assurez-vous que le script pre-commit est exécutable. Vous pouvez le rendre exécutable en utilisant la commande suivante dans votre terminal :

   ```bash
   chmod +x .git/hooks/pre-commit
