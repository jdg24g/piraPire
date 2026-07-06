# PiraPire Android Design Rules

Estas reglas definen como debe verse y sentirse la app Android nativa para mantener continuidad visual con la version web de PiraPire.

## Objetivo Visual

La app Android debe sentirse como la misma marca que la web:

- Oscura, moderna y enfocada en finanzas personales.
- Fondo con gradiente oscuro entre negro, slate y violeta/indigo.
- Superficies tipo glassmorphism oscuro.
- Acciones principales en violeta/indigo.
- Estados financieros con colores consistentes: verde para pagado/ingreso, rose para gasto/eliminar, amber para pendiente.
- Layout claro, compacto y util para uso diario.

No usar una apariencia Material 3 default clara. La app debe ser nativa Android, pero con identidad PiraPire.

## Tecnologia Recomendada

- Kotlin
- Jetpack Compose
- Material 3
- Navigation Compose
- ViewModel + StateFlow
- Retrofit/OkHttp
- DataStore para sesion/token

No usar WebView como solucion principal.

## Paleta

Usar estos colores base como tokens:

```kotlin
val PiraBackground = Color(0xFF080B11)
val PiraSurface = Color(0xFF0F172A)
val PiraSurfaceSoft = Color(0x1AFFFFFF)
val PiraBorder = Color(0x1AFFFFFF)

val PiraText = Color(0xFFF8FAFC)
val PiraTextMuted = Color(0xFF94A3B8)
val PiraTextSoft = Color(0xFFCBD5E1)

val PiraPurple = Color(0xFF9333EA)
val PiraPurpleSoft = Color(0x269333EA)
val PiraIndigo = Color(0xFF4F46E5)

val PiraEmerald = Color(0xFF34D399)
val PiraEmeraldSoft = Color(0x2634D399)

val PiraRose = Color(0xFFFB7185)
val PiraRoseSoft = Color(0x26FB7185)

val PiraAmber = Color(0xFFFBBF24)
val PiraAmberSoft = Color(0x26FBBF24)
```

## Fondo

Todas las pantallas autenticadas deben usar un fondo oscuro con gradiente sutil:

- Inicio: `#080B11`
- Medio: `#0F172A`
- Final: `#1E1B4B`

En Compose, usar `Brush.linearGradient` o `Brush.radialGradient` muy suave. No usar fondos blancos.

## Tipografia

- Usar Roboto o Inter si se agrega fuente custom.
- Titulos de pantalla: 28sp a 32sp, bold.
- Titulos de seccion: 18sp a 22sp, bold.
- Texto normal: 14sp a 16sp.
- Labels y badges: 11sp a 13sp.
- Evitar texto enorme dentro de cards compactas.

## Espaciado

- Padding de pantalla: 16dp.
- Separacion entre secciones: 20dp a 24dp.
- Separacion interna de cards: 14dp a 18dp.
- Gap entre controles: 8dp a 12dp.
- En pantallas chicas, los botones principales deben ocupar ancho completo.

## Cards

Crear componente base `PiraCard`.

Reglas:

- Fondo: blanco con alpha entre 5% y 8%.
- Borde: blanco con alpha 10%.
- Radius: 20dp a 24dp para cards grandes.
- Radius: 12dp a 16dp para controles pequenos.
- Elevacion discreta, nunca sombras pesadas.
- No poner cards dentro de cards salvo modales o listas realmente repetidas.

Ejemplo Compose:

```kotlin
@Composable
fun PiraCard(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier,
        color = Color.White.copy(alpha = 0.06f),
        shape = RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.10f)),
        tonalElevation = 0.dp,
        shadowElevation = 8.dp,
        content = {
            Column(
                modifier = Modifier.padding(16.dp),
                content = content
            )
        }
    )
}
```

## Botones

Crear variantes:

- `PiraPrimaryButton`: gradiente purple -> indigo.
- `PiraSecondaryButton`: fondo blanco 5%, borde blanco 10%.
- `PiraSuccessButton`: emerald soft, texto emerald.
- `PiraDangerButton`: rose soft, texto rose.

Reglas:

- Altura minima: 44dp.
- Radius: 14dp a 16dp.
- Texto semibold.
- En mobile, botones de formularios en ancho completo.
- Acciones destructivas siempre con confirmacion.

## Inputs

Crear `PiraTextField`, `PiraMoneyField`, `PiraSelectField`.

Reglas:

- Fondo: blanco 8% o surface oscuro.
- Borde: blanco 12%.
- Focus: purple.
- Texto: blanco.
- Placeholder: slate muted.
- Radius: 14dp.
- Altura minima: 48dp.
- Labels arriba del input, no dentro cuando el formulario sea denso.

## Navegacion

Usar bottom navigation nativa en Android.

Items:

- Dashboard
- Movimientos
- Cuentas
- Cuotas
- Reportes

Reglas:

- Fondo: `#080B11` con alpha alto.
- Borde superior blanco 10%.
- Item activo: fondo blanco 10% y texto/icono purple.
- Item inactivo: slate muted.
- Icono arriba, texto pequeno abajo.

## Modales y Bottom Sheets

Para Android, usar `ModalBottomSheet`.

Reglas:

- El modal de `Registrar compra` debe salir desde abajo.
- Fondo externo oscuro con scrim.
- Sheet con fondo slate oscuro, borde superior suave y radius superior 24dp.
- Opciones en lista vertical, no en 3 columnas.
- Cada opcion debe tener titulo y descripcion:
  - Gasto Fijo Mensual
  - Gasto Variable Mensual
  - Compra en Cuotas

## Formularios Dinamicos

El formulario `Registrar compra` cambia segun tipo.

### Compra en Cuotas

Campos:

- Producto / Servicio
- Cuenta
- Categoria
- Monto Total opcional
- Valor de Cuota opcional
- Cantidad de Cuotas obligatoria
- Cuotas Pagadas
- Fecha de Inicio
- Estado

Reglas:

- No aplicar validacion nativa requerida a `Monto Total`.
- Si `Monto Total` esta vacio y existen `Valor de Cuota + Cantidad`, calcular total.
- Si `Valor de Cuota` esta vacio y existen `Monto Total + Cantidad`, calcular cuota.
- Si faltan ambos, mostrar error claro.

Texto de ayuda:

> Si conoces el valor de la cuota, el monto total se calculara automaticamente.

### Gasto Fijo Mensual

Campos:

- Nombre del gasto
- Cuenta
- Categoria
- Monto mensual
- Dia de vencimiento

Regla:

- Es recurrente infinito hasta que el usuario lo desactive.
- No mostrar barra de progreso de cuotas.
- Mostrar si el mes correspondiente esta pagado o pendiente.

### Gasto Fijo Variable

Campos:

- Nombre del gasto
- Cuenta
- Categoria
- Dia de vencimiento

Regla:

- Al marcar pagado, abrir bottom sheet/dialog para ingresar monto real del mes.

## Estados Visuales

Badges:

- Pendiente: amber soft + texto amber.
- Vencido: rose soft + texto rose.
- Pagado: emerald soft + texto emerald.
- Activo: purple soft + texto purple.
- Cancelado/inactivo: slate soft + texto slate.

## Movimientos

Lista mobile:

- Usar cards compactas.
- Monto visible arriba a la derecha o debajo de fecha si no entra.
- Descripcion con maximo 2 lineas.
- Chips para categoria, cuenta y subtipo.
- Acciones: editar y borrar.

No usar tablas en pantallas pequenas para movimientos.

## Cuotas y Gastos Fijos

Vista principal:

- Cards para gastos fijos activos.
- Cards para compras en cuotas.
- Cada card debe tener accion principal visible:
  - Pagar cuota
  - Marcar pagado
  - Pagar ahora con monto si es variable
- Acciones secundarias:
  - Editar
  - Eliminar
  - Desactivar

En mobile, las acciones se apilan si no entran.

## Planilla de Cuotas

Crear pantalla `Planilla de cuotas`.

Columnas:

- Empresa
- Tipo
- Mensual
- Pagado
- Cuotas
- Faltante
- Pagado
- Total
- Restante
- Acciones

Reglas Android:

- En telefonos, usar scroll horizontal para la tabla.
- Mantener header sticky si es viable.
- Filas alternadas con fondo blanco 5% y fijo mensual con indigo 10%.
- Acciones por fila: Editar, Pagar.
- Para gasto variable, input de monto antes de pagar o bottom sheet para ingresar monto.
- Mostrar cards resumen arriba:
  - Mensual estimado
  - Ya pagado
  - Faltante

## Dashboard

Reglas:

- Cards compactas de resumen.
- Graficos con colores de la paleta.
- Evitar hero/landing.
- La pantalla debe empezar con datos utiles, no texto promocional.

## Animacion

Usar animaciones suaves:

- Transiciones de pantalla: fade + slide vertical leve.
- Bottom sheets: animacion nativa.
- Cards: fade/slide corto al cargar.
- Duracion: 180ms a 280ms.

Respetar `reduce motion` si se implementa accesibilidad.

## Accesibilidad

- Contraste suficiente sobre fondo oscuro.
- Touch targets minimo 44dp.
- No depender solo del color para estados: usar texto como Pendiente, Vencido, Pagado.
- Labels claros en formularios.
- Confirmacion para eliminar.

## Equivalencias Web a Android

| Web/Tailwind | Android Compose |
| --- | --- |
| `glass-card` | `PiraCard` con alpha y border |
| `bg-gradient-to-r from-purple-600 to-indigo-600` | `Brush.horizontalGradient(PiraPurple, PiraIndigo)` |
| Modal registrar compra | `ModalBottomSheet` |
| Mobile bottom nav HTML | `NavigationBar` Material 3 |
| Cards mobile | `LazyColumn` + `PiraCard` |
| Tabla planilla | `Row horizontalScroll` o tabla custom |
| Badges | `PiraStatusBadge` |
| Forms dinamicos | Compose state + AnimatedVisibility |

## Regla Principal

Cada pantalla debe priorizar uso real antes que decoracion. PiraPire es una app financiera: debe sentirse clara, rapida y confiable, manteniendo el estilo oscuro/glass de la web sin sacrificar legibilidad.
