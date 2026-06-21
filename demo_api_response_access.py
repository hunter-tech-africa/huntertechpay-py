"""
Démonstration: L'utilisateur a TOUJOURS accès à la réponse de l'API

Ce script montre que même en cas d'erreur, l'utilisateur peut voir
EXACTEMENT ce que l'API a retourné.
"""

from huntertechpay import HunterTechPay
from huntertechpay.exceptions import HunterTechPayError
import json


def demo_reponse_api_disponible():
    """
    Démo: La réponse de l'API est toujours accessible dans e.data
    """
    print("=" * 70)
    print("DÉMONSTRATION: Accès à la réponse API en cas d'erreur")
    print("=" * 70)

    hunter = HunterTechPay(
        api_key='test_key',
        secret_key='test_secret'
    )

    try:
        # Cet appel va échouer (pour la démo)
        result = hunter.deposit(
            amount=5000,
            currency='XAF',
            country='CM',
            phone='+237690000000',
            service_code='OM_CM_CASHIN'
        )

    except HunterTechPayError as e:
        print("\n✅ UNE ERREUR S'EST PRODUITE")
        print("-" * 70)

        # 1. MESSAGE EXACT DE L'API
        print("\n1️⃣ MESSAGE EXACT DE L'API (e.api_message):")
        print(f"   {e.api_message}")

        # 2. RÉPONSE JSON COMPLÈTE DE L'API
        print("\n2️⃣ RÉPONSE JSON COMPLÈTE DE L'API (e.data):")
        print(f"   {json.dumps(e.data, indent=2)}")

        # 3. CODE D'ERREUR DE L'API
        print("\n3️⃣ CODE D'ERREUR DE L'API (e.error_code):")
        print(f"   {e.error_code}")

        # 4. CODE HTTP
        print("\n4️⃣ CODE HTTP (e.status_code):")
        print(f"   {e.status_code}")

        # 5. REQUEST ID
        print("\n5️⃣ REQUEST ID POUR LE SUPPORT (e.request_id):")
        print(f"   {e.request_id}")

        # 6. TOUT EN UN DICTIONNAIRE
        print("\n6️⃣ TOUTES LES INFOS EN UN DICTIONNAIRE (e.to_dict()):")
        error_dict = e.to_dict()
        print(json.dumps(error_dict, indent=2))

        print("\n" + "=" * 70)
        print("✅ CONCLUSION: L'utilisateur voit TOUT ce que l'API retourne!")
        print("=" * 70)


def exemple_reponse_json():
    """
    Exemple: Quand l'API retourne du JSON
    """
    print("\n\n" + "=" * 70)
    print("CAS 1: API retourne une réponse JSON")
    print("=" * 70)

    print("""
Réponse de l'API (JSON):
{
    "detail": "Invalid phone number format",
    "error_code": "VALIDATION_ERROR",
    "field": "phone",
    "expected": "E.164 format",
    "received": "690000000"
}

Ce que l'utilisateur reçoit:
✅ e.api_message = "Invalid phone number format"
✅ e.error_code = "VALIDATION_ERROR"
✅ e.data = {
    "detail": "Invalid phone number format",
    "error_code": "VALIDATION_ERROR",
    "field": "phone",
    "expected": "E.164 format",
    "received": "690000000"
}

Accès aux champs:
✅ e.get_detail('field') = "phone"
✅ e.get_detail('expected') = "E.164 format"
✅ e.get_detail('received') = "690000000"
    """)


def exemple_reponse_non_json():
    """
    Exemple: Quand l'API retourne du texte brut (HTML, texte, etc.)
    """
    print("\n" + "=" * 70)
    print("CAS 2: API retourne du texte brut (non-JSON)")
    print("=" * 70)

    print("""
Réponse de l'API (HTML):
<html>
<body>
<h1>500 Internal Server Error</h1>
<p>The server encountered an error</p>
</body>
</html>

Ce que l'utilisateur reçoit:
✅ e.api_message = "<html>...</html>" (texte brut)
✅ e.data = {
    "raw_response": "<html>...</html>"
}

Accès au texte brut:
✅ e.get_detail('raw_response') = "<html>...</html>"
✅ e.api_message = Le texte complet
    """)


def exemple_erreur_insufficent_balance():
    """
    Exemple: Erreur de balance insuffisante
    """
    print("\n" + "=" * 70)
    print("CAS 3: Erreur 'Insufficient Balance'")
    print("=" * 70)

    print("""
Réponse de l'API:
{
    "detail": "Insufficient balance for withdrawal",
    "error_code": "INSUFFICIENT_BALANCE",
    "available_balance": 5000,
    "required_balance": 10000,
    "currency": "XAF",
    "wallet_id": "wallet_123"
}

Ce que l'utilisateur reçoit:
✅ e.api_message = "Insufficient balance for withdrawal"
✅ e.error_code = "INSUFFICIENT_BALANCE"
✅ e.data = {
    "detail": "Insufficient balance for withdrawal",
    "error_code": "INSUFFICIENT_BALANCE",
    "available_balance": 5000,
    "required_balance": 10000,
    "currency": "XAF",
    "wallet_id": "wallet_123"
}

Accès facile aux données:
✅ e.get_detail('available_balance') = 5000
✅ e.get_detail('required_balance') = 10000
✅ e.get_detail('currency') = "XAF"
✅ e.get_detail('wallet_id') = "wallet_123"

Code utilisateur:
    available = e.get_detail('available_balance', 0)
    required = e.get_detail('required_balance', 0)
    print(f"Manque: {required - available} XAF")
    """)


def recap_final():
    """
    Récapitulatif final
    """
    print("\n" + "=" * 70)
    print("📋 RÉCAPITULATIF: RÉPONSE API TOUJOURS ACCESSIBLE")
    print("=" * 70)

    print("""
┌─────────────────────────────────────────────────────────────────┐
│  GARANTIE: L'utilisateur voit TOUJOURS la réponse de l'API     │
└─────────────────────────────────────────────────────────────────┘

En cas d'erreur, l'utilisateur a accès à:

1️⃣  e.api_message
    └─ Message EXACT de l'API (non modifié)

2️⃣  e.data
    └─ Réponse JSON COMPLÈTE de l'API
    └─ Si non-JSON: e.data['raw_response'] contient le texte brut

3️⃣  e.error_code
    └─ Code d'erreur de l'API

4️⃣  e.status_code
    └─ Code HTTP (400, 401, 402, etc.)

5️⃣  e.request_id
    └─ ID pour contacter le support

6️⃣  e.get_detail(key, default)
    └─ Méthode helper pour accéder aux champs de e.data

7️⃣  e.to_dict()
    └─ Tout en un dictionnaire (pour logging)


┌─────────────────────────────────────────────────────────────────┐
│  TYPE DE RÉPONSE                                                │
├─────────────────────────────────────────────────────────────────┤
│  ✅ JSON          → e.data contient l'objet JSON complet        │
│  ✅ Texte brut    → e.data['raw_response'] contient le texte    │
│  ✅ HTML          → e.data['raw_response'] contient le HTML     │
│  ✅ Vide          → e.data = {} (vide mais accessible)          │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│  EXEMPLE D'UTILISATION                                          │
└─────────────────────────────────────────────────────────────────┘

try:
    result = hunter.deposit(...)

except HunterTechPayError as e:
    # Voir la réponse exacte de l'API
    print(f"API dit: {e.api_message}")
    print(f"Réponse complète: {e.data}")

    # Logger pour analyse
    import logging
    logging.error("API error", extra=e.to_dict())

    # Accéder à un champ spécifique
    if 'available_balance' in e.data:
        print(f"Balance: {e.data['available_balance']}")

    # Ou avec helper
    balance = e.get_detail('available_balance', 0)
    """)


if __name__ == '__main__':
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  HUNTERTECHPAY SDK - ACCÈS À LA RÉPONSE API EN CAS D'ERREUR".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Exemples
    exemple_reponse_json()
    exemple_reponse_non_json()
    exemple_erreur_insufficent_balance()
    recap_final()

    print("\n" + "=" * 70)
    print("✅ CONCLUSION")
    print("=" * 70)
    print("""
L'utilisateur du SDK a TOUJOURS accès à la réponse de l'API,
même en cas d'erreur. Aucune information n'est cachée ou perdue.

Tout est accessible via:
  - e.api_message  (message exact)
  - e.data         (réponse complète)
  - e.to_dict()    (tout en dictionnaire)
  - e.get_detail() (accès facile aux champs)
    """)
    print("=" * 70)
