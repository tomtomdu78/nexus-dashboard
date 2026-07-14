# NEXUS — Dashboard Shopify multi-boutiques, mis à jour chaque jour

Ce dépôt récupère automatiquement les données de vos boutiques Shopify une fois
par jour, les consolide, et publie un dashboard en ligne (GitHub Pages).
Une fois configuré, tout est automatique : chaque matin, votre URL affiche les
chiffres de la veille, sans aucune intervention.

---

## Ce qu'il vous faut avant de commencer

- Un compte GitHub (gratuit) : https://github.com/signup
- Un accès administrateur à chacune de vos boutiques Shopify
- 30 à 45 minutes pour la configuration initiale (une seule fois)

Aucune compétence en programmation n'est requise pour l'installation — il s'agit
de copier-coller et de cliquer. Le code est déjà écrit.

---

## Étape 1 — Créer un jeton d'accès API sur chaque boutique

À répéter pour **chacune** de vos boutiques.

1. Connectez-vous à l'admin de la boutique.
2. Allez dans **Paramètres** (en bas à gauche) → **Applications et canaux de vente**.
3. Cliquez sur **Développer des applications** (en haut à droite).
   - Si c'est la première fois : cliquez sur **Autoriser le développement d'applications**.
4. Cliquez sur **Créer une application**, donnez-lui un nom (ex. « NEXUS Dashboard »).
5. Onglet **Configuration** → **Configurer les API Admin**.
6. Dans « Champs d'accès Admin API », cochez au minimum :
   - `read_orders` (lecture des commandes)
   - `read_reports` (lecture des rapports / analytics)
   - `read_products` (lecture des produits)
7. Cliquez sur **Enregistrer**, puis onglet **Identifiants API** → **Installer l'application**.
8. Copiez le **jeton d'accès Admin API** (commence par `shpat_...`).
   ⚠️ Il ne s'affiche qu'une fois — notez-le en lieu sûr immédiatement.

Notez pour chaque boutique : son **domaine .myshopify.com** (ex.
`ma-boutique.myshopify.com`, visible dans l'URL de l'admin) et son **jeton**.

> Sécurité : ces jetons donnent accès en lecture à vos boutiques. Ne les mettez
> jamais dans un fichier public ni dans le code. On les stocke à l'étape 4 dans
> un « secret » GitHub chiffré, jamais visible.

---

## Étape 2 — Créer le dépôt GitHub

1. Sur GitHub, cliquez sur **New repository**.
2. Nommez-le (ex. `nexus-dashboard`), laissez-le **Public** (requis pour Pages
   gratuit ; le dashboard sera accessible via une URL, voir Étape 6 pour protéger).
3. Cliquez **Create repository**.
4. Uploadez tous les fichiers de ce projet : bouton **Add file → Upload files**,
   glissez-déposez le contenu du dossier, puis **Commit changes**.
   Conservez bien l'arborescence :
   ```
   .github/workflows/daily-update.yml
   scripts/fetch_data.py
   scripts/build_dashboard.py
   public/            (peut rester vide au départ)
   README.md
   ```

---

## Étape 3 — Activer GitHub Pages

1. Dans le dépôt : **Settings** → **Pages** (menu de gauche).
2. Sous « Build and deployment » → **Source** : choisissez **GitHub Actions**.
3. C'est tout — pas besoin de choisir une branche.

---

## Étape 4 — Enregistrer vos boutiques (le secret)

C'est ici que vos jetons sont stockés de façon chiffrée.

1. **Settings** → **Secrets and variables** → **Actions**.
2. Bouton **New repository secret**.
3. Nom : `SHOPIFY_STORES` (exactement, en majuscules).
4. Valeur : la liste de vos boutiques au format JSON ci-dessous, en remplaçant
   par vos vraies valeurs. Mettez toutes vos boutiques dans le même bloc :

   ```json
   [
     {"name": "Afro Élégance", "domain": "afro-elegance.myshopify.com", "token": "shpat_VOTRE_JETON_1", "category": "Mode africaine"},
     {"name": "Heritage Vintage", "domain": "heritage-vintage.myshopify.com", "token": "shpat_VOTRE_JETON_2", "category": "Gramophones"},
     {"name": "Mameline", "domain": "mameline.myshopify.com", "token": "shpat_VOTRE_JETON_3", "category": "Vêtements grossesse"}
   ]
   ```
   (Ajoutez une ligne par boutique, séparées par des virgules. Attention à ne pas
   oublier de virgule entre deux boutiques, ni d'en mettre après la dernière.)
5. Cliquez **Add secret**.

---

## Étape 5 — Lancer une première fois (test)

Sans attendre 3h du matin, lancez le workflow manuellement pour vérifier :

1. Onglet **Actions** du dépôt.
2. Cliquez sur « Mise à jour quotidienne NEXUS » (menu de gauche).
3. Bouton **Run workflow** → **Run workflow**.
4. Attendez ~1 minute. Un ✓ vert = succès. Un ✗ rouge = cliquez dessus pour lire
   l'erreur (souvent un jeton incorrect ou une permission API manquante).

---

## Étape 6 — Votre URL

Une fois le workflow réussi, votre dashboard est en ligne à :

```
https://VOTRE-NOM-GITHUB.github.io/nexus-dashboard/
```

(Visible aussi dans **Settings → Pages**.) Elle se mettra à jour toute seule
chaque jour à 3h UTC. Vous pouvez changer l'heure dans
`.github/workflows/daily-update.yml` (ligne `cron`).

### Rendre l'URL privée

Comme le dépôt est public, l'URL est publiquement accessible (si quelqu'un la
devine). Options pour la protéger :
- La garder simplement non partagée (peu probable qu'on la trouve).
- Passer le dépôt en **privé** : Pages privé nécessite un plan GitHub payant.
- Ajouter une protection par mot de passe via un service tiers (Cloudflare Access
  a une offre gratuite qui met un login devant votre page).

---

## Dépannage rapide

| Symptôme | Cause probable | Solution |
|---|---|---|
| Workflow ✗ à l'étape « Récupérer les données » | Jeton ou domaine incorrect | Vérifiez le JSON du secret `SHOPIFY_STORES` |
| Une boutique montre 0 € alors qu'elle vend | Permission API manquante | Ajoutez `read_reports` dans l'app Shopify |
| La page est blanche | data.json vide | Relancez le workflow, vérifiez les logs Actions |
| L'heure ne convient pas | Fuseau cron en UTC | Ajustez la ligne `cron` (Paris = UTC+1 ou +2) |

---

## Comment ça marche (résumé)

1. **fetch_data.py** interroge chaque boutique via l'API Admin de Shopify
   (requêtes ShopifyQL) et écrit `public/data.json`.
2. **build_dashboard.py** transforme ce JSON en `public/index.html` (la console NEXUS).
3. **daily-update.yml** orchestre le tout chaque nuit et publie sur GitHub Pages.

Pour rafraîchir à la demande sans attendre : Actions → Run workflow.
