#!/usr/bin/env python3
"""
Script de test pour le SDK HunterTechPay Python

Usage:
    python test_sdk.py

Ou avec variables d'environnement:
    export HUNTER_API_KEY='htp_live_...'
    export HUNTER_SECRET_KEY='sk_live_...'
    python test_sdk.py
"""

import sys
import os
import time
from pathlib import Path
from uuid import uuid4

# Ajouter le répertoire parent au path pour importer huntertechpay
sys.path.insert(0, str(Path(__file__).parent))

from huntertechpay import HunterTechPay, HunterTechPayError


def print_header(title):
    """Afficher un header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_success(message):
    """Afficher un message de succès"""
    print(f"✅ {message}")


def print_error(message):
    """Afficher un message d'erreur"""
    print(f"❌ {message}")


def print_info(message):
    """Afficher un message d'information"""
    print(f"ℹ️  {message}")


def test_get_providers(hunter):
    """Test 1: Récupérer les providers disponibles"""
    print_header("TEST 1: Récupération des Providers (CM)")

    try:
        response = hunter.get_providers()

        if response.success:
            print_success(f"Pays: {response.country_code}")
            print_success(f"Devise: {response.currency}")
            print_success(f"Nombre de providers: {len(response.providers)}")

            print("\n📋 Liste des providers:")
            for provider in response.providers:
                print(f"\n  • {provider.name}")
                print(f"    Code: {provider.provider_code}")
                print(f"    CASHIN: {provider.cashin_service_code or 'N/A'}")
                print(f"    CASHOUT: {provider.cashout_service_code or 'N/A'}")
                print(f"    Actif: {'Oui' if provider.is_active else 'Non'}")

            return True
        else:
            print_error("La réponse ne contient pas 'success: True'")
            print(response)
            return False

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        return False


def test_deposit(hunter):
    """Test 2: Effectuer un dépôt (CASHIN)"""
    print_header("TEST 2: Dépôt (CASHIN) - Du mobile money vers le wallet")

    try:
        partner_id = f"TEST_{uuid4().hex[:8]}"

        print_info(f"Partner ID: {partner_id}")
        print_info("Montant: 100.00 XAF")
        print_info("Service Code: HT_PAIEMENTMARCHAND_MTN_CM")
        print_info("Téléphone: 670000000")

        result = hunter.deposit(
            amount=100.0,
            currency="XAF",
            country="CM",
            phone="670000000",
            service_code="HT_PAIEMENTMARCHAND_MTN_CM",
            partner_id=partner_id,
            description="Test dépôt via SDK Python"
        )

        print_success("Dépôt initié avec succès")

        print(f"\n💰 Détails du dépôt:")
        print(f"  Transaction ID: {result.transaction_id}")
        print(f"  Partner ID: {result.partner_id or partner_id}")
        print(f"  Statut: {result.status}")
        print(f"  Message: {result.message or 'N/A'}")

        # Vérifier le statut immédiatement
        print_info("\n⏳ Attente de 2 secondes avant vérification du statut...")
        time.sleep(2)
        test_check_status(hunter, partner_id)

        return partner_id

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return None
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_withdraw(hunter):
    """Test 3: Effectuer un retrait (CASHOUT)"""
    print_header("TEST 3: Retrait (CASHOUT) - Du wallet vers le mobile money")

    try:
        partner_id = f"TEST_{uuid4().hex[:8]}"

        print_info(f"Partner ID: {partner_id}")
        print_info("Montant: 50.00 XAF")
        print_info("Service Code: HT_PAIEMENTMARCHAND_MTN_CM")
        print_info("Téléphone: 670000000")

        result = hunter.withdraw(
            amount=50.0,
            currency="XAF",
            country="CM",
            phone="670000000",
            service_code="HT_PAIEMENTMARCHAND_MTN_CM",
            partner_id=partner_id,
            description="Test retrait via SDK Python"
        )

        print_success("Retrait initié avec succès")

        print(f"\n💸 Détails du retrait:")
        print(f"  Transaction ID: {result.transaction_id}")
        print(f"  Partner ID: {result.partner_id or partner_id}")
        print(f"  Statut: {result.status}")
        print(f"  Message: {result.message or 'N/A'}")

        # Vérifier le statut immédiatement
        print_info("\n⏳ Attente de 2 secondes avant vérification du statut...")
        time.sleep(2)
        test_check_status(hunter, partner_id)

        return partner_id

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return None
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_list_transactions(hunter):
    """Test 4: Lister les transactions"""
    print_header("TEST 4: Liste des Transactions (10 dernières)")

    try:
        response = hunter.list_transactions(
            page=1,
            page_size=10
        )

        if response.success:
            print_success(f"Total transactions: {response.total}")
            print_success(f"Transactions retournées: {len(response.transactions)}")

            if response.transactions:
                print("\n📋 Dernières transactions:")
                first_partner_id = None
                for i, tx in enumerate(response.transactions[:5], 1):  # Afficher les 5 premières
                    print(f"\n  {i}. Transaction ID: {tx.transaction_id}")
                    print(f"     Partner ID: {tx.partner_id or 'N/A'}")
                    print(f"     Montant: {tx.amount} {tx.currency}")
                    print(f"     Statut: {tx.status}")
                    print(f"     Type: {tx.transaction_type or 'N/A'}")
                    print(f"     Référence: {tx.reference or 'N/A'}")

                    # Retourner le premier partner_id pour le test suivant
                    if i == 1 and tx.partner_id:
                        first_partner_id = tx.partner_id

                return first_partner_id
            else:
                print_info("Aucune transaction trouvée")
                return None
        else:
            print_error("La réponse ne contient pas 'success: True'")
            print(response)
            return None

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return None
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        return None


def test_check_status(hunter, partner_id):
    """Test 5: Vérifier le statut d'une transaction"""
    print_header(f"TEST 5: Vérification du Statut de la Transaction")

    if not partner_id:
        print_info("Pas de partner_id disponible pour ce test")
        return False

    print_info(f"Partner ID: {partner_id}")

    try:
        tx = hunter.check_status(partner_id)

        print_success("Statut récupéré avec succès")

        print(f"\n📊 Détails de la transaction:")
        print(f"  Transaction ID: {tx.transaction_id}")
        print(f"  Partner ID: {tx.partner_id or 'N/A'}")
        print(f"  Référence: {tx.reference or 'N/A'}")
        print(f"  Statut: {tx.status}")
        print(f"  Montant: {tx.amount} {tx.currency}")
        print(f"  Frais: {tx.fee_amount or 0} {tx.currency}")
        print(f"  Net: {tx.net_amount or tx.amount} {tx.currency}")
        print(f"  Type: {tx.transaction_type or 'N/A'}")
        print(f"  Provider: {tx.provider or 'N/A'}")
        print(f"  Créé le: {tx.created_at or 'N/A'}")

        # Afficher les propriétés helper
        if tx.is_successful:
            print(f"  ✅ Transaction réussie")
        elif tx.is_pending:
            print(f"  ⏳ Transaction en attente")
        elif tx.is_failed:
            print(f"  ❌ Transaction échouée")

        return True

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        return False


def test_get_balance(hunter):
    """Test 6: Récupérer les soldes des wallets"""
    print_header("TEST 6: Récupération des Soldes des Wallets")

    try:
        response = hunter.get_balance()

        if response.success:
            print_success("Soldes récupérés avec succès")

            if response.wallets:
                print(f"\n💰 Wallets ({response.total_wallets}):")
                for wallet in response.wallets:
                    print(f"\n  • Wallet {wallet.currency}")
                    print(f"    Solde disponible: {wallet.available_balance_decimal:.2f} {wallet.currency}")
                    print(f"    Solde en attente: {wallet.pending_balance_decimal:.2f} {wallet.currency}")
                    print(f"    Solde total: {wallet.balance_decimal:.2f} {wallet.currency}")
                    print(f"    Actif: {'Oui' if wallet.is_active else 'Non'}")
                    print(f"    Gelé: {'Oui' if wallet.is_frozen else 'Non'}")
            else:
                print_info("Aucun wallet trouvé")

            return True
        else:
            print_error("La réponse ne contient pas 'success: True'")
            print(response)
            return False

    except HunterTechPayError as e:
        print_error(f"Erreur API: {str(e)}")
        if hasattr(e, 'error_code') and e.error_code:
            print(f"Code erreur: {e.error_code}")
        if hasattr(e, 'data') and e.data:
            print(f"Détails: {e.data}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {str(e)}")
        return False


def main():
    """Fonction principale"""
    print_header("🧪 TEST DU SDK HUNTERTECHPAY PYTHON")

    # Récupérer les credentials
    # api_key = os.environ.get('HUNTER_API_KEY')
    # secret_key = os.environ.get('HUNTER_SECRET_KEY')
    
    api_key = None
    secret_key = None

    if not api_key or not secret_key:
        print_info("Variables d'environnement non définies")
        print("Veuillez entrer vos credentials:")
        api_key = input("API Key (htp_live_...): ").strip()
        secret_key = input("Secret Key (sk_live_...): ").strip()
    else:
        print_success("Credentials chargés depuis les variables d'environnement")
        print(f"API Key: {api_key[:20]}...")
        print(f"Secret Key: {secret_key[:15]}...")

    if not api_key or not secret_key:
        print_error("API Key et Secret Key requis!")
        sys.exit(1)

    # Initialiser le SDK
    print_info("\n🔧 Initialisation du SDK...")
    print_info(f"Base URL: http://localhost:8007")

    try:
        hunter = HunterTechPay(
            api_key=api_key,
            secret_key=secret_key,
            base_url='http://localhost:8007',
            timeout=30
        )
        print_success("SDK initialisé avec succès")
    except Exception as e:
        print_error(f"Erreur d'initialisation: {str(e)}")
        sys.exit(1)

    # Exécuter les tests
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }

    deposit_partner_id = None
    withdraw_partner_id = None

    # Test 1: Get Providers
    results['total'] += 1
    if test_get_providers(hunter):
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(1)  # Pause entre les tests

    # Test 2: Deposit (CASHIN)
    print_info("\n⚠️  Test optionnel - Appuyez sur Entrée pour tester le dépôt, ou 's' pour sauter")
    user_input = input("Tester le dépôt ? (Entrée/s): ").strip().lower()
    if user_input != 's':
        results['total'] += 1
        deposit_partner_id = test_deposit(hunter)
        if deposit_partner_id:
            results['passed'] += 1
        else:
            results['failed'] += 1
        time.sleep(1)

    # Test 3: Withdraw (CASHOUT)
    print_info("\n⚠️  Test optionnel - Appuyez sur Entrée pour tester le retrait, ou 's' pour sauter")
    user_input = input("Tester le retrait ? (Entrée/s): ").strip().lower()
    if user_input != 's':
        results['total'] += 1
        withdraw_partner_id = test_withdraw(hunter)
        if withdraw_partner_id:
            results['passed'] += 1
        else:
            results['failed'] += 1
        time.sleep(1)

    # Test 4: List Transactions
    results['total'] += 1
    first_partner_id = test_list_transactions(hunter)
    if first_partner_id:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(1)

    # Test 5: Check Status (seulement si aucun dépôt/retrait n'a été fait)
    # Note: test_check_status est déjà appelé dans test_deposit et test_withdraw
    # Ce test ne s'exécute que si l'utilisateur a sauté les tests optionnels
    if not deposit_partner_id and not withdraw_partner_id and first_partner_id:
        results['total'] += 1
        if test_check_status(hunter, first_partner_id):
            results['passed'] += 1
        else:
            results['failed'] += 1
        time.sleep(1)

    # Test 6: Get Balance
    results['total'] += 1
    if test_get_balance(hunter):
        results['passed'] += 1
    else:
        results['failed'] += 1

    # Résumé
    print_header("📊 RÉSUMÉ DES TESTS")
    print(f"Total de tests: {results['total']}")
    print(f"✅ Réussis: {results['passed']}")
    print(f"❌ Échoués: {results['failed']}")

    if results['failed'] == 0:
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("✅ Le SDK est prêt à être utilisé et commité")
        return 0
    else:
        print(f"\n⚠️  {results['failed']} test(s) ont échoué")
        print("Veuillez corriger les erreurs avant de commiter")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {str(e)}")
        sys.exit(1)
