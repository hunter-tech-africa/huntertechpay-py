# Guide Complet de Gestion des Erreurs - HunterTechPay SDK

## Vue d'ensemble

Le SDK HunterTechPay Python expose maintenant **TOUTES les informations d'erreur de l'API** pour permettre aux développeurs de voir exactement ce que l'API retourne en cas d'erreur.

## Ce qui est capturé

Lorsqu'une erreur se produit, l'exception contient:

### 1. Message d'erreur
- `e.message` - Message d'erreur (peut être formaté)
- `e.api_message` - **Message EXACT de l'API (non modifié)**

### 2. Codes et statuts
- `e.status_code` - Code HTTP (400, 401, 402, 404, 500, etc.)
- `e.error_code` - Code d'erreur de l'API (ex: `VALIDATION_ERROR`)

### 3. Données complètes de la réponse
- `e.data` - **Réponse JSON complète de l'API**
- `e.response_headers` - **Tous les headers HTTP de la réponse**
- `e.response_url` - **URL qui a été appelée**
- `e.http_method` - **Méthode HTTP utilisée (GET, POST, etc.)**

### 4. Traçabilité
- `e.request_id` - ID de requête pour le support/débogage

## Exemples d'utilisation

### 1. Voir le message exact de l'API

```python
from huntertechpay import HunterTechPay
from huntertechpay.exceptions import HunterTechPayError

hunter = HunterTechPay(api_key='...', secret_key='...')

try:
    result = hunter.deposit(
        amount=5000,
        currency='XAF',
        country='CM',
        phone='+237690000000',
        service_code='OM_CM_CASHIN'
    )
except HunterTechPayError as e:
    # Message EXACT de l'API (non modifié)
    print(f"Message API: {e.api_message}")

    # Message formaté par le SDK
    print(f"Message SDK: {e.message}")

    # Sont-ils identiques ?
    print(f"Identiques: {e.api_message == e.message}")
```

### 2. Accéder à la réponse complète de l'API

```python
try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    # Réponse JSON complète de l'API
    print("Réponse complète de l'API:")
    print(e.data)

    # Exemple de sortie:
    # {
    #   'detail': 'Invalid phone number format',
    #   'error_code': 'VALIDATION_ERROR',
    #   'field': 'phone',
    #   'expected': 'E.164 format',
    #   'received': '690000000'
    # }
```

### 3. Voir les headers HTTP de la réponse

```python
try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    # Tous les headers de la réponse HTTP
    print("Headers de la réponse:")
    for header, value in e.response_headers.items():
        print(f"  {header}: {value}")

    # Exemples de headers:
    # Content-Type: application/json
    # X-Request-ID: req_abc123
    # X-RateLimit-Remaining: 99
    # Date: Sat, 21 Jun 2026 10:30:00 GMT
```

### 4. Voir l'URL et la méthode HTTP

```python
try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    print(f"URL appelée: {e.response_url}")
    print(f"Méthode HTTP: {e.http_method}")

    # Exemple:
    # URL appelée: https://api.huntertechpay.com/v1/deposits
    # Méthode HTTP: POST
```

### 5. Obtenir toutes les informations en un seul appel

```python
try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    # Convertir en dictionnaire avec TOUTES les infos
    error_info = e.to_dict()

    # error_info contient:
    # {
    #     'error_type': 'ValidationError',
    #     'message': 'Invalid phone number format',
    #     'api_message': 'Invalid phone number format',  # Message exact de l'API
    #     'status_code': 400,
    #     'error_code': 'VALIDATION_ERROR',
    #     'request_id': 'req_abc123',
    #     'data': {...},  # Réponse JSON complète
    #     'response_headers': {...},  # Tous les headers
    #     'response_url': 'https://api.huntertechpay.com/v1/deposits',
    #     'http_method': 'POST'
    # }

    # Parfait pour le logging
    import json
    print(json.dumps(error_info, indent=2))
```

### 6. Accéder à des champs spécifiques de la réponse API

```python
try:
    result = hunter.withdraw(
        amount=100000,
        currency='XAF',
        country='CM',
        phone='+237670000000',
        service_code='MTN_CM_CASHOUT'
    )
except InsufficientBalanceError as e:
    # Méthode 1: Accès direct à e.data
    available = e.data.get('available_balance', 0)
    required = e.data.get('required_balance', 0)

    # Méthode 2: Utiliser get_detail() (plus simple)
    available = e.get_detail('available_balance', 0)
    required = e.get_detail('required_balance', 0)
    currency = e.get_detail('currency', 'XAF')

    print(f"Balance disponible: {available} {currency}")
    print(f"Balance requise: {required} {currency}")
    print(f"Manque: {required - available} {currency}")
```

### 7. Logging complet pour le débogage

```python
import logging
import json

logger = logging.getLogger(__name__)

try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    # Logger TOUTES les informations
    error_dict = e.to_dict()

    logger.error(
        f"Deposit failed: {e.message}",
        extra={
            'error_type': error_dict['error_type'],
            'api_message': error_dict['api_message'],
            'status_code': error_dict['status_code'],
            'error_code': error_dict['error_code'],
            'request_id': error_dict['request_id'],
            'api_response': error_dict['data'],
            'response_headers': error_dict['response_headers'],
            'url': error_dict['response_url'],
            'method': error_dict['http_method']
        }
    )
```

### 8. Réponse non-JSON (HTML, texte brut, etc.)

Quand l'API retourne une réponse qui n'est pas du JSON (erreur serveur, HTML, etc.):

```python
try:
    result = hunter.deposit(...)
except ServerError as e:
    # Le texte brut est dans e.data['raw_response']
    if 'raw_response' in e.data:
        print(f"Réponse brute: {e.data['raw_response']}")

    # Le message API contiendra aussi le texte
    print(f"Message API: {e.api_message}")
```

## Affichage automatique des détails

Quand vous affichez l'exception, tous les détails supplémentaires sont automatiquement inclus:

```python
try:
    result = hunter.deposit(...)
except HunterTechPayError as e:
    # L'affichage simple montre TOUT
    print(e)

    # Sortie:
    # Invalid phone number format | Status: 400 | Code: VALIDATION_ERROR | Request ID: req_abc123 | Details: {"field": "phone", "expected": "E.164 format", "received": "690000000"}
```

## Types d'exceptions

Toutes ces exceptions exposent les mêmes informations:

```python
from huntertechpay.exceptions import (
    HunterTechPayError,        # Base exception
    ValidationError,           # 400 - Erreur de validation
    AuthenticationError,       # 401 - Erreur d'authentification
    PaymentError,             # 402 - Erreur de paiement
    InsufficientBalanceError, # 402 - Balance insuffisante
    FrozenAccountError,       # 403 - Compte gelé
    NotFoundError,            # 404 - Ressource non trouvée
    RateLimitError,           # 429 - Limite de taux dépassée
    ServerError,              # 500+ - Erreur serveur
    NetworkError,             # Erreur réseau
    TimeoutError,             # Timeout
)
```

## Gestion par type d'erreur

```python
try:
    result = hunter.deposit(...)

except ValidationError as e:
    # Erreurs de validation (400)
    print(f"Paramètres invalides: {e.api_message}")
    print(f"Détails: {e.data}")

except AuthenticationError as e:
    # Erreurs d'authentification (401)
    print(f"Authentification échouée: {e.api_message}")

except InsufficientBalanceError as e:
    # Balance insuffisante
    available = e.get_detail('available_balance', 0)
    print(f"Balance insuffisante. Disponible: {available}")

except PaymentError as e:
    # Autres erreurs de paiement
    print(f"Paiement échoué: {e.api_message}")

except ServerError as e:
    # Erreurs serveur (500+)
    print(f"Erreur serveur: {e.api_message}")
    print(f"Request ID pour le support: {e.request_id}")
    # Réessayer avec backoff exponentiel

except NetworkError as e:
    # Erreurs réseau
    print(f"Erreur réseau: {e.api_message}")
    # Vérifier la connexion et réessayer

except HunterTechPayError as e:
    # Toutes autres erreurs
    print(f"Erreur: {e.api_message}")
    error_dict = e.to_dict()
    # Logger pour investigation
```

## Résumé

### Avant les améliorations ❌
```python
except HunterTechPayError as e:
    print(e.message)  # Message simple
    # Difficile de voir les détails complets de l'API
```

### Après les améliorations ✅
```python
except HunterTechPayError as e:
    # 1. Message exact de l'API
    print(e.api_message)

    # 2. Réponse JSON complète
    print(e.data)

    # 3. Headers HTTP
    print(e.response_headers)

    # 4. URL et méthode
    print(e.response_url, e.http_method)

    # 5. Tout en un dictionnaire
    error_dict = e.to_dict()

    # 6. Accès facile aux champs spécifiques
    value = e.get_detail('field_name', default)
```

## Avantages

1. **Transparence totale** - Voir exactement ce que l'API retourne
2. **Meilleur débogage** - Accès à tous les détails HTTP
3. **Logging complet** - Capturer toutes les informations pour l'analyse
4. **Pas de breaking changes** - Compatible avec le code existant
5. **Flexible** - Plusieurs façons d'accéder aux données
