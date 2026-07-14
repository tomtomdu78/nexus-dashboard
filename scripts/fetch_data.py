"""
NEXUS — Récupération quotidienne des données Shopify multi-boutiques.

Ce script interroge chaque boutique via l'API Admin GraphQL de Shopify,
récupère le CA / commandes / retours / top produits pour l'année en cours,
consolide le tout et écrit un fichier data.json que le générateur HTML lira.

Aucune donnée sensible n'est écrite en dur ici : les domaines et tokens
proviennent de la variable d'environnement SHOPIFY_STORES (voir README).
"""

import os
import json
import sys
from datetime import date
from urllib import request, error

API_VERSION = "2025-01"  # version de l'API Admin Shopify


def load_stores():
    """
    Charge la config des boutiques depuis la variable d'environnement.
    Format attendu (JSON) :
      [{"name": "Ma boutique", "domain": "xxx.myshopify.com",
        "token": "shpat_...", "category": "Mode"}, ...]
    """
    raw = os.environ.get("SHOPIFY_STORES")
    if not raw:
        sys.exit("ERREUR: variable d'environnement SHOPIFY_STORES absente.")
    try:
        stores = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"ERREUR: SHOPIFY_STORES n'est pas un JSON valide — {e}")
    if not isinstance(stores, list) or not stores:
        sys.exit("ERREUR: SHOPIFY_STORES doit être une liste non vide.")
    return stores


def graphql(domain, token, query, variables=None):
    """Envoie une requête GraphQL à une boutique et renvoie le JSON."""
    url = f"https://{domain}/admin/api/{API_VERSION}/graphql.json"
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Shopify-Access-Token", token)
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        print(f"  ! HTTP {e.code} sur {domain}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  ! Erreur réseau sur {domain}: {e}")
        return None


# Requête ShopifyQL via l'endpoint GraphQL (analytics).
# On récupère les agrégats de vente pour l'année en cours.
SALES_QUERY = """
query($q: String!) {
  shopifyqlQuery(query: $q) {
    __typename
    ... on TableResponse {
      tableData {
        rowData
        columns { name }
      }
    }
    parseErrors { message }
  }
}
"""


def run_shopifyql(domain, token, ql):
    """Exécute une requête ShopifyQL, renvoie la liste de lignes (rowData)."""
    res = graphql(domain, token, SALES_QUERY, {"q": ql})
    if not res:
        return []
    node = res.get("data", {}).get("shopifyqlQuery")
    if not node:
        # Certaines erreurs remontent dans "errors"
        errs = res.get("errors")
        if errs:
            print(f"  ! ShopifyQL erreurs: {errs[:1]}")
        return []
    if node.get("parseErrors"):
        print(f"  ! ShopifyQL parseErrors: {node['parseErrors']}")
        return []
    table = node.get("tableData") or {}
    return table.get("rowData", [])


def fetch_store(store):
    """Récupère les indicateurs d'une boutique pour l'année en cours."""
    domain = store["domain"]
    token = store["token"]
    year = date.today().year
    since = f"{year}-01-01"
    print(f"→ {store['name']} ({domain})")

    # 1) Agrégats globaux
    ql_totals = (
        "FROM sales SHOW orders, gross_sales, discounts, returns, "
        "net_sales, average_order_value "
        f"SINCE {since} UNTIL today"
    )
    rows = run_shopifyql(domain, token, ql_totals)
    totals = rows[0] if rows else [0, 0, 0, 0, 0, 0]

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    orders = int(num(totals[0]))
    gross = num(totals[1])
    disc = abs(num(totals[2]))
    ret = abs(num(totals[3]))
    net = num(totals[4])
    aov = num(totals[5])

    # 2) CA mensuel (7 mois max sur l'année)
    ql_month = (
        "FROM sales SHOW total_sales "
        f"TIMESERIES month SINCE {since} UNTIL today"
    )
    mrows = run_shopifyql(domain, token, ql_month)
    monthly = [round(num(r[1]), 2) for r in mrows] if mrows else []

    # 3) Top 5 produits
    ql_prod = (
        "FROM sales SHOW gross_sales GROUP BY product_title "
        f"ORDER BY gross_sales DESC LIMIT 5 SINCE {since} UNTIL today"
    )
    prows = run_shopifyql(domain, token, ql_prod)
    products = [[r[0], round(num(r[1]), 2)] for r in prows if r[0]] if prows else []

    retpct = round(ret / gross * 100, 1) if gross else 0.0

    return {
        "name": store["name"],
        "domain": domain,
        "category": store.get("category", ""),
        "ca": round(net, 2),
        "gross": round(gross, 2),
        "discounts": round(disc, 2),
        "returns": round(ret, 2),
        "orders": orders,
        "aov": round(aov, 2),
        "returnPct": retpct,
        "monthly": monthly,
        "products": products,
        "boot": orders == 0,
    }


def main():
    stores = load_stores()
    results = []
    for s in stores:
        try:
            results.append(fetch_store(s))
        except Exception as e:
            print(f"  ! Échec {s.get('name','?')}: {e}")

    active = [r for r in results if not r["boot"]]
    consolidated = {
        "generatedAt": date.today().isoformat(),
        "storeCount": len(results),
        "activeCount": len(active),
        "totalCA": round(sum(r["ca"] for r in results), 2),
        "totalOrders": sum(r["orders"] for r in results),
        "totalGross": round(sum(r["gross"] for r in results), 2),
        "totalReturns": round(sum(r["returns"] for r in results), 2),
        "stores": sorted(results, key=lambda r: r["ca"], reverse=True),
    }
    orders = consolidated["totalOrders"]
    gross = consolidated["totalGross"]
    consolidated["avgBasket"] = round(consolidated["totalCA"] / orders, 2) if orders else 0
    consolidated["returnPct"] = round(consolidated["totalReturns"] / gross * 100, 1) if gross else 0

    out = os.path.join(os.path.dirname(__file__), "..", "public", "data.json")
    out = os.path.abspath(out)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Données consolidées écrites: {out}")
    print(f"  CA total: {consolidated['totalCA']} € · "
          f"{consolidated['totalOrders']} commandes · "
          f"{len(active)}/{len(results)} boutiques actives")


if __name__ == "__main__":
    main()
