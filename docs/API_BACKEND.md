# PiraPire — Documentación del Backend y APIs

Esta documentación describe cómo funciona el backend de **PiraPire**, sus módulos principales, el flujo de autenticación y los endpoints REST disponibles.

> Base estimada de API en desarrollo local: `http://localhost:25610/api/`

---

## 1. Resumen del backend

PiraPire es un backend Django orientado al control de finanzas personales. Permite a cada usuario administrar:

- cuentas o billeteras;
- categorías de ingresos y gastos;
- transacciones;
- compras en cuotas;
- movimientos recurrentes o gastos fijos;
- reportes financieros;
- exportación CSV de movimientos.

El backend usa Django REST Framework para las APIs y JWT para autenticación. También mantiene vistas web con Django Templates para el frontend web.

---

## 2. Stack técnico

- Python 3.12
- Django
- Django REST Framework
- Simple JWT
- django-filter
- PostgreSQL
- WhiteNoise para archivos estáticos
- Django Templates para vistas web

---

## 3. Configuración general

### Apps instaladas principales

El proyecto registra estas apps propias:

- `accounts`
- `wallets`
- `categories`
- `transactions`
- `installments`
- `recurrences`
- `reports`
- `exports`

### Base de datos

La configuración actual usa PostgreSQL:

```env
POSTGRES_DB=postgres
POSTGRES_USER=jdg24g
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Autenticación DRF

El backend acepta:

- `JWTAuthentication`
- `SessionAuthentication`

La mayoría de endpoints requiere usuario autenticado.

Header requerido para consumir la API con JWT:

```http
Authorization: Bearer <access_token>
```

### Paginación

Los listados REST usan paginación por página con tamaño por defecto de 50 registros.

Respuesta típica:

```json
{
  "count": 120,
  "next": "http://localhost:25610/api/transactions/?page=2",
  "previous": null,
  "results": []
}
```

---

## 4. Rutas principales del proyecto

### Frontend web

| Ruta | Uso |
|---|---|
| `/` | Redirige a dashboard si el usuario está autenticado o a login si no lo está |
| `/login/` | Login web |
| `/register/` | Registro web |
| `/logout/` | Cierre de sesión web |
| `/dashboard/` | Dashboard web |
| `/movements/` | Listado de movimientos |
| `/wallets/` | Listado de cuentas |
| `/categories/` | Listado de categorías |
| `/installments/` | Compras en cuotas |
| `/reports/` | Reportes web |
| `/admin/` | Admin de Django |

### API

Todo lo REST entra por:

```http
/api/
```

Módulos registrados:

| Prefijo | App |
|---|---|
| `/api/auth/` | Autenticación y perfil |
| `/api/wallets/` | Cuentas / billeteras |
| `/api/categories/` | Categorías |
| `/api/transactions/` | Transacciones |
| `/api/installments/` | Compras en cuotas |
| `/api/recurrences/` | Movimientos recurrentes / gastos fijos |
| `/api/reports/` | Reportes |
| `/api/exports/` | Exportaciones |

---

## 5. Autenticación — `/api/auth/`

### 5.1 Registrar usuario

```http
POST /api/auth/register/
```

No requiere token.

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

Respuesta esperada:

```json
{
  "username": "juan",
  "email": "juan@ejemplo.com",
  "first_name": "Juan",
  "last_name": "García"
}
```

La contraseña es de solo escritura y se guarda usando el método seguro `create_user` de Django.

### 5.2 Login JWT

```http
POST /api/auth/login/
```

Body:

```json
{
  "username": "juan",
  "password": "contraseña123"
}
```

Respuesta:

```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

### 5.3 Renovar token

```http
POST /api/auth/token/refresh/
```

Body:

```json
{
  "refresh": "<jwt_refresh_token>"
}
```

Respuesta:

```json
{
  "access": "<nuevo_access_token>"
}
```

### 5.4 Mi perfil

```http
GET /api/auth/me/
```

Requiere JWT.

Respuesta:

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

## 6. Cuentas / Wallets — `/api/wallets/`

Representa las cuentas financieras del usuario: efectivo, banco, tarjeta, billetera electrónica, etc.

### Tipos disponibles

| Código | Significado |
|---|---|
| `CASH` | Efectivo |
| `BANK` | Cuenta bancaria |
| `DEBIT` | Tarjeta de débito |
| `CREDIT` | Tarjeta de crédito |
| `E_WALLET` | Billetera electrónica |
| `OTHER` | Otro |

### Campos principales

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | number | ID de la cuenta |
| `user` | number | Usuario dueño, solo lectura |
| `name` | string | Nombre de la cuenta |
| `type` | string | Tipo de cuenta |
| `initial_balance` | decimal | Saldo inicial |
| `current_balance` | decimal | Saldo calculado automáticamente |
| `currency` | string | Moneda, por defecto `PYG` |
| `is_active` | boolean | Si la cuenta está activa |
| `created_at` | datetime | Fecha de creación |
| `updated_at` | datetime | Fecha de actualización |

### Cómo se calcula el saldo actual

`current_balance` no se guarda manualmente. Se calcula así:

```text
saldo actual = saldo inicial + ingresos - gastos
```

### Endpoints CRUD

```http
GET    /api/wallets/
POST   /api/wallets/
GET    /api/wallets/{id}/
PUT    /api/wallets/{id}/
PATCH  /api/wallets/{id}/
DELETE /api/wallets/{id}/
```

### Crear cuenta

```http
POST /api/wallets/
```

Body:

```json
{
  "name": "Efectivo",
  "type": "CASH",
  "initial_balance": "100000.00",
  "currency": "PYG",
  "is_active": true
}
```

Reglas importantes:

- El backend fuerza `user=request.user`, no acepta que el frontend elija otro usuario.
- Cada usuario solo lista sus propias cuentas.
- No se permiten nombres duplicados de cuenta para el mismo usuario.

---

## 7. Categorías — `/api/categories/`

Las categorías clasifican ingresos y gastos. Pueden ser predeterminadas del sistema o personalizadas del usuario.

### Valores de `applies_to`

| Código | Uso |
|---|---|
| `INCOME` | Solo ingresos |
| `EXPENSE` | Solo gastos |
| `BOTH` | Ingresos y gastos |

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | number | ID |
| `user` | number/null | Dueño si es categoría personalizada |
| `name` | string | Nombre |
| `applies_to` | string | Tipo de uso |
| `parent` | number/null | Categoría padre |
| `parent_name` | string | Nombre de categoría padre, solo lectura |
| `is_default` | boolean | Indica si es del sistema |
| `is_active` | boolean | Activa o no |

### Endpoints CRUD

```http
GET    /api/categories/
POST   /api/categories/
GET    /api/categories/{id}/
PUT    /api/categories/{id}/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/
```

### Crear categoría personalizada

```json
{
  "name": "Gimnasio",
  "applies_to": "EXPENSE",
  "parent": null,
  "is_active": true
}
```

### Subcategoría

```json
{
  "name": "Suplementos",
  "applies_to": "EXPENSE",
  "parent": 5
}
```

Reglas importantes:

- El listado devuelve categorías predeterminadas del sistema más categorías del usuario autenticado.
- Las categorías predeterminadas no se pueden editar ni eliminar.
- Una categoría no puede ser su propio padre.
- El backend marca las categorías creadas por API como `is_default=false` y `user=request.user`.

---

## 8. Transacciones — `/api/transactions/`

Representa ingresos y gastos cargados por el usuario.

### Tipos

| Código | Significado |
|---|---|
| `INCOME` | Ingreso |
| `EXPENSE` | Gasto |

### Subtipos

Para ingresos:

| Código | Significado |
|---|---|
| `UNIQUE` | Ingreso único |
| `RECURRENT` | Ingreso recurrente |
| `VARIABLE` | Ingreso variable |

Para gastos:

| Código | Significado |
|---|---|
| `NORMAL` | Gasto normal |
| `FIXED` | Gasto fijo |
| `VARIABLE_FIXED` | Gasto fijo variable |
| `INSTALLMENT` | Compra en cuotas |

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | number | ID |
| `user` | number | Usuario dueño, solo lectura |
| `wallet` | number | Cuenta afectada |
| `wallet_name` | string | Nombre de cuenta, solo lectura |
| `category` | number | Categoría |
| `category_name` | string | Nombre de categoría, solo lectura |
| `type` | string | `INCOME` o `EXPENSE` |
| `subtype` | string | Subtipo |
| `amount` | decimal | Monto |
| `date` | date | Fecha |
| `description` | string | Descripción |
| `created_at` | datetime | Creación |
| `updated_at` | datetime | Actualización |

### Endpoints CRUD

```http
GET    /api/transactions/
POST   /api/transactions/
GET    /api/transactions/{id}/
PUT    /api/transactions/{id}/
PATCH  /api/transactions/{id}/
DELETE /api/transactions/{id}/
```

### Filtros disponibles

```http
GET /api/transactions/?type=EXPENSE
GET /api/transactions/?subtype=FIXED
GET /api/transactions/?wallet=1
GET /api/transactions/?category=3
GET /api/transactions/?date_from=2026-07-01&date_to=2026-07-31
GET /api/transactions/?amount_min=10000&amount_max=500000
GET /api/transactions/?description=netflix
```

### Crear ingreso

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

### Crear gasto

```json
{
  "wallet": 1,
  "category": 4,
  "type": "EXPENSE",
  "subtype": "NORMAL",
  "amount": "120000.00",
  "date": "2026-07-05",
  "description": "Supermercado"
}
```

### Reglas de validación

- `amount` debe ser mayor a cero.
- La cuenta debe pertenecer al usuario autenticado.
- La categoría debe ser predeterminada o pertenecer al usuario.
- Si `type=INCOME`, el `subtype` debe ser `UNIQUE`, `RECURRENT` o `VARIABLE`.
- Si `type=EXPENSE`, el `subtype` debe ser `NORMAL`, `FIXED`, `VARIABLE_FIXED` o `INSTALLMENT`.

---

## 9. Compras en cuotas — `/api/installments/`

Representa una compra financiada o en cuotas, por ejemplo una TV a 18 cuotas.

### Estados

| Código | Significado |
|---|---|
| `ACTIVE` | Activa |
| `COMPLETED` | Completada |
| `CANCELED` | Cancelada |

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | number | ID |
| `user` | number | Usuario dueño |
| `wallet` | number | Cuenta asociada |
| `wallet_name` | string | Nombre de cuenta |
| `category` | number | Categoría |
| `category_name` | string | Nombre de categoría |
| `product_name` | string | Producto comprado |
| `total_amount` | decimal | Monto total |
| `total_installments` | number | Total de cuotas |
| `installment_value` | decimal | Valor de cada cuota |
| `paid_installments` | number | Cuotas pagadas |
| `pending_installments` | number | Cuotas pendientes, calculado |
| `start_date` | date | Inicio |
| `end_date` | date | Fin calculado |
| `status` | string | Estado |

### Endpoints CRUD

```http
GET    /api/installments/
POST   /api/installments/
GET    /api/installments/{id}/
PUT    /api/installments/{id}/
PATCH  /api/installments/{id}/
DELETE /api/installments/{id}/
```

### Filtros

```http
GET /api/installments/?status=ACTIVE
GET /api/installments/?wallet=1
GET /api/installments/?category=3
```

### Crear compra indicando monto total

```json
{
  "wallet": 1,
  "category": 8,
  "product_name": "Smart TV 55",
  "total_amount": "2340000.00",
  "total_installments": 18,
  "paid_installments": 0,
  "start_date": "2026-07-01"
}
```

El backend calcula:

```text
installment_value = total_amount / total_installments
end_date = start_date + total_installments - 1 meses
pending_installments = total_installments - paid_installments
```

### Crear compra indicando valor de cuota

```json
{
  "wallet": 1,
  "category": 8,
  "product_name": "Celular",
  "installment_value": "150000.00",
  "total_installments": 12,
  "paid_installments": 0,
  "start_date": "2026-07-01"
}
```

El backend calcula:

```text
total_amount = installment_value * total_installments
```

### Reglas de validación

- La cuenta debe pertenecer al usuario.
- La categoría debe ser predeterminada o del usuario.
- `total_installments` debe ser mayor a cero.
- `paid_installments` no puede superar `total_installments`.
- Debe existir `total_amount` o `installment_value`.
- Si se pagan todas las cuotas, el estado pasa a `COMPLETED`.

---

## 10. Movimientos recurrentes / gastos fijos — `/api/recurrences/`

Representa ingresos o gastos repetitivos. También se usa para gastos fijos mensuales pagables.

### Frecuencias

| Código | Significado |
|---|---|
| `DAILY` | Diario |
| `WEEKLY` | Semanal |
| `BIWEEKLY` | Quincenal |
| `MONTHLY` | Mensual |
| `YEARLY` | Anual |

### Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | number | ID |
| `user` | number | Usuario dueño |
| `wallet` | number | Cuenta |
| `wallet_name` | string | Nombre de cuenta |
| `category` | number | Categoría |
| `category_name` | string | Nombre de categoría |
| `type` | string | `INCOME` o `EXPENSE` |
| `amount` | decimal | Monto base |
| `amount_is_variable` | boolean | Si el monto cambia cada mes |
| `start_date` | date | Inicio |
| `end_date` | date/null | Fin opcional |
| `due_day` | number | Día de vencimiento del mes |
| `frequency` | string | Frecuencia |
| `description` | string | Descripción |
| `is_active` | boolean | Activo o no |
| `current_period` | object/null | Estado del período actual |
| `current_period_is_paid` | boolean/null | Si el período actual está pagado |
| `current_period_status` | string/null | Estado actual |
| `next_pending_period` | object/null | Próximo período pendiente |
| `latest_paid_period` | object/null | Último período pagado |

### Endpoints CRUD

```http
GET    /api/recurrences/
POST   /api/recurrences/
GET    /api/recurrences/{id}/
PUT    /api/recurrences/{id}/
PATCH  /api/recurrences/{id}/
DELETE /api/recurrences/{id}/
```

### Filtros

```http
GET /api/recurrences/?wallet=1
GET /api/recurrences/?category=4
GET /api/recurrences/?type=EXPENSE
GET /api/recurrences/?frequency=MONTHLY
GET /api/recurrences/?is_active=true
```

### Crear gasto fijo mensual

```json
{
  "wallet": 1,
  "category": 4,
  "type": "EXPENSE",
  "amount": "350000.00",
  "amount_is_variable": false,
  "frequency": "MONTHLY",
  "start_date": "2026-01-01",
  "due_day": 10,
  "description": "Alquiler",
  "is_active": true
}
```

### Crear gasto fijo de monto variable

Ejemplo: ANDE, agua, combustible fijo mensual variable.

```json
{
  "wallet": 1,
  "category": 4,
  "type": "EXPENSE",
  "amount": "0.00",
  "amount_is_variable": true,
  "frequency": "MONTHLY",
  "start_date": "2026-01-01",
  "due_day": 15,
  "description": "ANDE",
  "is_active": true
}
```

### Marcar como pagado

Endpoint adicional del ViewSet:

```http
POST /api/recurrences/{id}/pay/
```

Solo aplica para:

- `type=EXPENSE`
- `frequency=MONTHLY`
- `is_active=true`

#### Pago con monto fijo

```json
{
  "period_year": 2026,
  "period_month": 7
}
```

#### Pago con monto variable

```json
{
  "period_year": 2026,
  "period_month": 7,
  "amount": "285000.00"
}
```

Al pagar, el backend crea automáticamente una `Transaction` de tipo `EXPENSE`:

- `subtype=FIXED` si el monto no es variable;
- `subtype=VARIABLE_FIXED` si `amount_is_variable=true`.

También registra un `RecurrentPayment` para evitar pagar dos veces el mismo período.

Respuesta esperada:

```json
{
  "detail": "Gasto fijo de 2026-07 marcado como pagado.",
  "payment": {
    "id": 1,
    "period_year": 2026,
    "period_month": 7,
    "transaction_id": 25
  },
  "recurrence": {}
}
```

### Reglas de validación

- `due_day` debe estar entre 1 y 31.
- Si `amount_is_variable=false`, `amount` debe ser mayor a cero.
- La cuenta debe pertenecer al usuario.
- La categoría debe ser predeterminada o del usuario.
- `end_date` no puede ser anterior a `start_date`.
- No se permite pagar dos veces el mismo año/mes para la misma recurrencia.

---

## 11. Reportes — `/api/reports/`

Los reportes son endpoints de lectura. Todos requieren autenticación.

### 11.1 Dashboard mensual

```http
GET /api/reports/dashboard/
GET /api/reports/dashboard/?year=2026&month=7
```

Valida que `month` esté entre 1 y 12. Si `year` o `month` no son enteros, responde `400`.

Respuesta típica:

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
  "recent_transactions": [],
  "daily_expense_average": 59677.4
}
```

### 11.2 Por categoría

```http
GET /api/reports/by-category/
```

### 11.3 Por cuenta

```http
GET /api/reports/by-wallet/
```

### 11.4 Comparación mensual

```http
GET /api/reports/monthly-comparison/
```

### 11.5 Comparación anual

```http
GET /api/reports/yearly-comparison/
```

### 11.6 Resumen por rango

```http
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

### Filtros comunes de reportes

```http
date_from=YYYY-MM-DD
date_to=YYYY-MM-DD
wallet=<id>
category=<id>
type=INCOME|EXPENSE
subtype=<subtipo>
```

Ejemplo:

```http
GET /api/reports/by-category/?type=EXPENSE&date_from=2026-07-01&date_to=2026-07-31
```

---

## 12. Exportaciones — `/api/exports/`

### Descargar transacciones en CSV

```http
GET /api/exports/transactions/csv/
```

Acepta filtros similares a reportes:

```http
GET /api/exports/transactions/csv/?type=EXPENSE&date_from=2026-07-01&date_to=2026-07-31
```

Respuesta HTTP:

```http
Content-Type: text/csv
Content-Disposition: attachment; filename="transactions_export.csv"
```

Formato esperado:

```csv
fecha,tipo,monto,categoria,subcategoria,cuenta,descripcion
2026-07-05,EXPENSE,120000.0,Servicios,,Cuenta banco,Netflix
```

---

## 13. Seguridad y aislamiento por usuario

El backend aplica aislamiento por usuario en los módulos principales.

### Wallets

Cada usuario solo ve sus propias cuentas. Al crear una cuenta, el backend guarda automáticamente `user=request.user`.

### Categories

El usuario ve:

- categorías predeterminadas del sistema;
- categorías creadas por él.

No puede editar ni eliminar categorías predeterminadas.

### Transactions

Cada usuario solo ve sus propias transacciones. Además, el serializer valida que la cuenta pertenezca al usuario y que la categoría sea predeterminada o propia.

### Installments

Cada usuario solo ve sus compras en cuotas. Se valida que la cuenta sea propia y la categoría permitida.

### Recurrences

Cada usuario solo ve sus movimientos recurrentes. También se valida propiedad de cuenta y categoría.

---

## 14. Códigos de respuesta comunes

| Código | Significado |
|---|---|
| `200` | OK |
| `201` | Creado correctamente |
| `204` | Eliminado correctamente |
| `400` | Error de validación |
| `401` | No autenticado |
| `403` | Sin permiso |
| `404` | No encontrado |

---

## 15. Ejemplos de consumo con cURL

### Login

```bash
curl -X POST http://localhost:25610/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Guardar token en variable

```bash
TOKEN="PEGAR_ACCESS_TOKEN"
```

### Listar cuentas

```bash
curl http://localhost:25610/api/wallets/ \
  -H "Authorization: Bearer $TOKEN"
```

### Crear cuenta

```bash
curl -X POST http://localhost:25610/api/wallets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Efectivo",
    "type": "CASH",
    "initial_balance": "100000.00",
    "currency": "PYG"
  }'
```

### Crear transacción

```bash
curl -X POST http://localhost:25610/api/transactions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": 1,
    "category": 4,
    "type": "EXPENSE",
    "subtype": "NORMAL",
    "amount": "50000.00",
    "date": "2026-07-06",
    "description": "Compra de prueba"
  }'
```

### Pagar gasto fijo mensual

```bash
curl -X POST http://localhost:25610/api/recurrences/1/pay/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "period_year": 2026,
    "period_month": 7,
    "amount": "285000.00"
  }'
```

---

## 16. Notas importantes para el frontend móvil

Para la app móvil o frontend separado:

1. Hacer login en `/api/auth/login/`.
2. Guardar `access` y `refresh` de forma segura.
3. Enviar `Authorization: Bearer <access>` en cada petición.
4. Si el token vence, usar `/api/auth/token/refresh/`.
5. Consumir endpoints paginados usando `results`.
6. No enviar `user`; el backend lo asigna automáticamente.
7. Para gastos fijos variables, pedir el monto al usuario antes de llamar a `/api/recurrences/{id}/pay/`.
8. Para compras en cuotas, se puede enviar `total_amount` o `installment_value`; el backend calcula el valor faltante.

---

## 17. Posibles mejoras futuras

- Agregar OpenAPI/Swagger con `drf-spectacular`.
- Agregar tests automáticos por endpoint.
- Agregar permisos personalizados más explícitos por objeto.
- Agregar endpoint específico para pagar cuotas de `InstallmentPurchase` y crear la transacción automáticamente.
- Agregar endpoint de estadísticas rápidas para pantalla inicial móvil.
- Documentar errores exactos por serializer en formato estándar.
- Versionar API como `/api/v1/` antes de producción.
