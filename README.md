# PiraPire — Backend API

Aplicación backend para el análisis de finanzas personales.
Ayuda al usuario a entender en qué gasta su dinero, cuánto ingresa, cuáles son sus gastos fijos, cuánto paga en cuotas y cómo evolucionan sus finanzas en el tiempo.

---

## Stack

- Python 3.12 · Django 5.1 · Django REST Framework 3.15
- PostgreSQL · Docker · JWT (Simple JWT)

---

## Instalación local

```bash
# 1. Copiar variables de entorno
cp .env.example .env
# Editar .env con tu contraseña real de PostgreSQL

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Aplicar migraciones y crear superusuario
python manage.py migrate
python init_admin.py

# 4. Levantar servidor
python manage.py runserver 0.0.0.0:25610
```

O con Docker (sin instalar nada localmente):

```bash
cp .env.example .env
docker compose up --build
```

**Requisito:** PostgreSQL corriendo en `localhost:5432` con el usuario y contraseña configurados en `.env`.

---

## URLs y Frontend

| Entorno / Página | URL |
|------------------|-----|
| **Frontend Web (Dashboard)** | `http://localhost:25610/dashboard/` |
| **Iniciar Sesión** | `http://localhost:25610/login/` |
| **Registrarse** | `http://localhost:25610/register/` |
| **API base** | `http://localhost:25610/api/` |
| **Admin Django** | `http://localhost:25610/admin/` |

Credenciales admin demo: `admin` / `admin123`

---

## Frontend Web (Django Templates)

PiraPire ahora incluye una interfaz web nativa construida directamente sobre Django. 

### Stack de Tecnologías Frontend
- **Django Templates:** Renderizado nativo desde el servidor, usando sesiones de Django para autenticación web.
- **Tailwind CSS (CDN):** Estilo visual moderno y limpio sin necesidad de dependencias de Node.js.
- **Chart.js (CDN):** Gráficos interactivos en tiempo real para visualizar la distribución del dinero.
- **JavaScript nativo:** Lógica interactiva en formularios de registro y movimientos.

### Diseño y UX
- **Mobile First:** Totalmente adaptado para pantallas pequeñas (360px de ancho en adelante).
- **Glassmorphism:** Tarjetas transparentes con efectos de blur, gradientes suaves de fondo y bordes e iluminación sutiles.
- **Responsive:** Visualización en formato de lista adaptada en celulares y tablas en ordenadores de escritorio.
- **Barra de navegación inferior** para dispositivos móviles y **sidebar lateral** para computadoras de escritorio.

---

## Autenticación

PiraPire usa **JWT (JSON Web Tokens)**. Todos los endpoints (excepto registro y login) requieren el header:

```
Authorization: Bearer <access_token>
```

### Flujo de autenticación

```
POST /api/auth/register/   → crear cuenta
POST /api/auth/login/      → obtener tokens
POST /api/auth/token/refresh/ → renovar access token cuando expire
```

---

## Endpoints

### 🔐 Autenticación — `/api/auth/`

#### Registrar usuario
```
POST /api/auth/register/
```
Body:
```json
{
  "username": "juan",
  "email": "juan@ejemplo.com",
  "password": "contraseña123",
  "first_name": "Juan",
  "last_name": "García"
}
```
Respuesta `201`:
```json
{
  "username": "juan",
  "email": "juan@ejemplo.com",
  "first_name": "Juan",
  "last_name": "García"
}
```

---

#### Login
```
POST /api/auth/login/
```
Body:
```json
{
  "username": "juan",
  "password": "contraseña123"
}
```
Respuesta `200`:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
> El `access` token dura **1 día**. El `refresh` token dura **7 días**.

---

#### Renovar token
```
POST /api/auth/token/refresh/
```
Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```
Respuesta `200`:
```json
{
  "access": "eyJ0eXAiOiJKV1Qi... (nuevo token)"
}
```

---

#### Mi perfil
```
GET /api/auth/me/
```
Respuesta `200`:
```json
{
  "id": 1,
  "username": "juan",
  "email": "juan@ejemplo.com",
  "first_name": "Juan",
  "last_name": "García"
}
```

---

### 💳 Cuentas — `/api/wallets/`

Tipos disponibles: `CASH` · `BANK` · `DEBIT` · `CREDIT` · `E_WALLET` · `OTHER`

#### Listar mis cuentas
```
GET /api/wallets/
```
Respuesta:
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "user": 1,
      "name": "Cuenta banco",
      "type": "BANK",
      "initial_balance": "500000.00",
      "current_balance": "320000.00",
      "currency": "PYG",
      "is_active": true,
      "created_at": "2026-07-01T10:00:00Z",
      "updated_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

#### Crear cuenta
```
POST /api/wallets/
```
Body:
```json
{
  "name": "Efectivo",
  "type": "CASH",
  "initial_balance": "100000.00",
  "currency": "PYG"
}
```

#### Detalle / editar / eliminar
```
GET    /api/wallets/{id}/
PUT    /api/wallets/{id}/
PATCH  /api/wallets/{id}/
DELETE /api/wallets/{id}/
```

> `current_balance` se calcula automáticamente (saldo inicial + ingresos − gastos).

---

### 🏷️ Categorías — `/api/categories/`

Tipos (`applies_to`): `INCOME` · `EXPENSE` · `BOTH`

Las categorías predeterminadas del sistema **no se pueden modificar ni eliminar**.

#### Categorías predeterminadas del sistema
| Nombre | Tipo |
|--------|------|
| Alimentación | EXPENSE |
| Transporte | EXPENSE |
| Hogar | EXPENSE |
| Servicios | EXPENSE |
| Salud | EXPENSE |
| Educación | EXPENSE |
| Entretenimiento | EXPENSE |
| Tecnología | EXPENSE |
| Vehículo | EXPENSE |
| Mascotas | EXPENSE |
| Impuestos | BOTH |
| Otros | BOTH |
| Sueldo | INCOME |
| Ventas | INCOME |
| Inversiones | INCOME |

#### Listar categorías
```
GET /api/categories/
```
Muestra las categorías del sistema + las categorías personalizadas del usuario.

#### Crear categoría personalizada
```
POST /api/categories/
```
Body:
```json
{
  "name": "Gimnasio",
  "applies_to": "EXPENSE",
  "parent": null
}
```

#### Subcategoría (categoría hija)
```json
{
  "name": "Proteínas",
  "applies_to": "EXPENSE",
  "parent": 5
}
```

---

### 💰 Transacciones — `/api/transactions/`

Tipos (`type`): `INCOME` · `EXPENSE`

Subtipos para **ingresos** (`subtype`): `UNIQUE` · `RECURRENT` · `VARIABLE`

Subtipos para **gastos** (`subtype`): `NORMAL` · `FIXED` · `VARIABLE_FIXED` · `INSTALLMENT`

#### Listar transacciones
```
GET /api/transactions/
```

**Filtros disponibles por query params:**

| Parámetro | Ejemplo | Descripción |
|-----------|---------|-------------|
| `type` | `?type=EXPENSE` | Tipo de movimiento |
| `subtype` | `?subtype=FIXED` | Subtipo |
| `wallet` | `?wallet=1` | ID de la cuenta |
| `category` | `?category=3` | ID de la categoría |
| `date_from` | `?date_from=2026-07-01` | Fecha desde |
| `date_to` | `?date_to=2026-07-31` | Fecha hasta |
| `amount_min` | `?amount_min=10000` | Monto mínimo |
| `amount_max` | `?amount_max=500000` | Monto máximo |
| `description` | `?description=netflix` | Busca en descripción |

**Ejemplo combinado:**
```
GET /api/transactions/?type=EXPENSE&date_from=2026-07-01&date_to=2026-07-31
```

#### Registrar ingreso
```
POST /api/transactions/
```
```json
{
  "wallet": 1,
  "category": 13,
  "type": "INCOME",
  "subtype": "UNIQUE",
  "amount": "3500000.00",
  "date": "2026-07-01",
  "description": "Sueldo julio"
}
```

#### Registrar gasto fijo
```json
{
  "wallet": 1,
  "category": 4,
  "type": "EXPENSE",
  "subtype": "FIXED",
  "amount": "120000.00",
  "date": "2026-07-05",
  "description": "Netflix"
}
```

#### Registrar gasto en cuotas
```json
{
  "wallet": 1,
  "category": 8,
  "type": "EXPENSE",
  "subtype": "INSTALLMENT",
  "amount": "13000.00",
  "date": "2026-07-10",
  "description": "TV — cuota 1/18"
}
```

---

### 📦 Compras en cuotas — `/api/installments/`

Estados (`status`): `ACTIVE` · `COMPLETED` · `CANCELED`

#### Registrar compra en cuotas
```
POST /api/installments/
```
```json
{
  "wallet": 1,
  "category": 8,
  "product_name": "Smart TV 55\"",
  "total_amount": "2340000.00",
  "total_installments": 18,
  "paid_installments": 0,
  "start_date": "2026-07-01"
}
```
El sistema calcula automáticamente:
- `installment_value` → 130.000 Gs por cuota
- `end_date` → fecha estimada de última cuota
- `pending_installments` → cuotas restantes

Respuesta:
```json
{
  "id": 1,
  "product_name": "Smart TV 55\"",
  "total_amount": "2340000.00",
  "total_installments": 18,
  "installment_value": "130000.00",
  "paid_installments": 0,
  "pending_installments": 18,
  "start_date": "2026-07-01",
  "end_date": "2027-12-01",
  "status": "ACTIVE"
}
```

#### Listar compras en cuotas
```
GET /api/installments/
```
Filtros: `?status=ACTIVE` · `?wallet=1` · `?category=3`

---

### 🔁 Movimientos recurrentes — `/api/recurrences/`

Frecuencias (`frequency`): `DAILY` · `WEEKLY` · `BIWEEKLY` · `MONTHLY` · `YEARLY`

#### Registrar movimiento recurrente
```
POST /api/recurrences/
```
```json
{
  "wallet": 1,
  "category": 4,
  "type": "EXPENSE",
  "amount": "350000.00",
  "frequency": "MONTHLY",
  "start_date": "2026-01-01",
  "description": "Alquiler",
  "is_active": true
}
```

#### Listar recurrencias
```
GET /api/recurrences/
```
Filtros: `?type=EXPENSE` · `?frequency=MONTHLY` · `?is_active=true` · `?wallet=1`

---

### 📊 Reportes — `/api/reports/`

#### Dashboard mensual
```
GET /api/reports/dashboard/
GET /api/reports/dashboard/?year=2026&month=7
```
Respuesta:
```json
{
  "period": "2026-07",
  "total_income": 3500000.0,
  "total_expense": 1850000.0,
  "balance": 1650000.0,
  "fixed_expenses": 820000.0,
  "variable_fixed_expenses": 210000.0,
  "installment_expenses": 260000.0,
  "top_expense_category": "Alimentación",
  "top_wallet": "Cuenta banco",
  "recent_transactions": [...],
  "daily_expense_average": 59677.4
}
```

#### Gastos/Ingresos por categoría
```
GET /api/reports/by-category/
GET /api/reports/by-category/?type=EXPENSE&date_from=2026-07-01&date_to=2026-07-31
```

#### Gastos/Ingresos por cuenta
```
GET /api/reports/by-wallet/
```

#### Comparación mensual histórica
```
GET /api/reports/monthly-comparison/
```

#### Comparación anual histórica
```
GET /api/reports/yearly-comparison/
```

#### Resumen por rango de fechas
```
GET /api/reports/summary/?date_from=2026-01-01&date_to=2026-06-30
```
Respuesta:
```json
{
  "total_income": 21000000.0,
  "total_expense": 13500000.0,
  "balance": 7500000.0,
  "transactions_count": 84
}
```

**Filtros disponibles en todos los reportes:**

| Parámetro | Descripción |
|-----------|-------------|
| `date_from` | Fecha desde (YYYY-MM-DD) |
| `date_to` | Fecha hasta (YYYY-MM-DD) |
| `wallet` | ID de cuenta |
| `category` | ID de categoría |
| `type` | `INCOME` o `EXPENSE` |
| `subtype` | Subtipo del movimiento |

---

### 📥 Exportación — `/api/exports/`

#### Descargar transacciones en CSV
```
GET /api/exports/transactions/csv/
GET /api/exports/transactions/csv/?type=EXPENSE&date_from=2026-07-01&date_to=2026-07-31
```

Descarga un archivo `transactions_export.csv` con el formato:

```csv
fecha,tipo,monto,categoria,subcategoria,cuenta,descripcion
2026-07-05,EXPENSE,120000.0,Servicios,,Cuenta banco,Netflix
2026-07-10,EXPENSE,13000.0,Tecnología,,Cuenta banco,TV cuota 1/18
2026-07-01,INCOME,3500000.0,Sueldo,,Cuenta banco,Sueldo julio
```

Acepta los mismos filtros que `/api/transactions/`.

---

## Paginación

Todos los listados están paginados. Respuesta estándar:

```json
{
  "count": 120,
  "next": "http://localhost:25610/api/transactions/?page=2",
  "previous": null,
  "results": [...]
}
```

Tamaño de página: **50 registros**. Cambiar con `?page=2`.

---

## Seguridad

- Cada usuario **solo ve y modifica sus propios datos**.
- No es posible acceder a cuentas, transacciones o categorías de otro usuario.
- Las categorías predeterminadas del sistema son de solo lectura para todos los usuarios.
- Los tokens JWT expiran automáticamente (access: 1 día / refresh: 7 días).

---

## Códigos de respuesta

| Código | Significado |
|--------|-------------|
| `200` | OK |
| `201` | Creado exitosamente |
| `400` | Error de validación en los datos enviados |
| `401` | No autenticado (falta o expiró el token) |
| `403` | Sin permiso para esa acción |
| `404` | Recurso no encontrado |
