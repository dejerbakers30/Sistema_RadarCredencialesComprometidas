# Mejora profesional del frontend

## Objetivo

Se actualizó la interfaz de `Radar de Credenciales Comprometidas` para que funcione como un centro de operaciones de ciberseguridad empresarial, manteniendo los contratos backend y la funcionalidad previamente validada.

## Diseño adoptado

- Paleta clara basada en azul oscuro, azul y celeste; rojo, ámbar y verde se reservan para estados y riesgo.
- Layout con sidebar agrupado por operación, análisis, administración y cuenta.
- Header con breadcrumbs, usuario, rol, acceso a perfil y logout.
- Tarjetas blancas, bordes suaves, sombras discretas y estados vacíos/carga/error reutilizables.
- Carga diferida mediante `React.lazy` y `Suspense` para las rutas protegidas.

## Pantallas modificadas

- Dashboard: KPIs reales, gráficas con estados sin datos, reincidencias y tarjetas operacionales.
- Filtraciones: búsqueda con debounce, filtro de estado, limpieza, paginación y tabla responsive.
- Detalle de filtración: secciones de identificación, exposición, evaluación y respuesta; confirmación de acciones.
- Contenciones: estados con icono, texto y color, además de acción manual confirmada.
- Reportes: tipos Operacional/PDF, Gestión/DOCX y Ejecutivo/XLSX con formato derivado automáticamente.
- Auditoría: estado de integridad, verificación explícita, filtros soportados por API y hash completo bajo diálogo.
- Notificaciones: filtros, paginación, estados y empty state consumiendo la API real.
- Usuarios: búsqueda, rol, estado, MFA y acciones autorizadas.
- Roles: permisos y usuarios asociados desde backend, sin matrices estáticas.
- Perfil: identidad, rol, MFA y secreto TOTP oculto por defecto.
- Login: presentación profesional y validación accesible existente.

## Componentes reutilizables

- `PageHeader`, `SectionCard`, `EmptyState`, `ErrorState` y `LoadingState`.
- `FilterBar` para búsquedas y limpieza de filtros.
- `StatusIndicator` para comunicar estado con icono, texto y color.
- `ConfirmDialog` para acciones sensibles.
- `KpiCard` para indicadores ejecutivos.

## Endpoints consumidos

Se conservaron los endpoints existentes: `/dashboard/summary`, `/leaks`, `/leaks/kpis`, `/leaks/{id}`, `/resets`, `/reports`, `/reports/{id}/download`, `/audit`, `/audit/verify`, `/notifications`, `/users`, `/roles`, `/sources`, `/auth/me`, `/auth/logout` y los endpoints de MFA del perfil.

No se añadieron filtros visuales que el backend no soporte. En particular, auditoría utiliza módulo y rango temporal; filtraciones utiliza estado, correo y paginación; notificaciones utiliza estado, canal y paginación.

## Responsive y accesibilidad

- Sidebar convertido en drawer en pantallas menores a `md`.
- Tablas con scroll horizontal controlado.
- Gráficas dentro de contenedores adaptables.
- Focus visible, labels asociados, roles de alerta/estado y botones con nombres accesibles.
- Los mensajes de validación del login permanecen asociados a sus campos.

## Tests ejecutados

Se ejecutaron los binarios locales instalados equivalentes a los scripts del proyecto:

```text
./node_modules/.bin/tsc --noEmit       PASS
./node_modules/.bin/eslint . --ext .ts,.tsx  PASS (0 errores, 6 warnings)
./node_modules/.bin/vitest run         PASS (6 archivos, 9 tests)
./node_modules/.bin/vite build         PASS
```

Se añadieron pruebas de comportamiento para Reportes, Auditoría y Notificaciones, además de conservar Dashboard, Filtraciones y Login.

## Resultado del build

El build generó chunks por ruta. Los principales tamaños sin comprimir fueron:

| Chunk | Tamaño | Gzip |
|---|---:|---:|
| `index-CxpTsMlA.js` | 451.17 kB | 144.06 kB |
| `Dashboard-DKLb4D_R.js` | 430.24 kB | 115.70 kB |
| `Reports-DqeD0ovM.js` | 5.21 kB | 2.04 kB |
| `Users-BKqZd0ao.js` | 4.52 kB | 1.94 kB |
| `Notifications-C3sEEKA3.js` | 4.28 kB | 1.83 kB |

## Limitaciones

- La validación realizada es automatizada; no sustituye una revisión visual manual en 1440, 1366, 1024, 768 y 390 px.
- ESLint conserva seis warnings previos/no bloqueantes relacionados con `any` y Fast Refresh.
- No se inventó historial de reportes ni actividad reciente porque no existe un endpoint real para esos datos.
- No se modificaron contratos backend, workflows n8n ni dependencias principales.

## Capturas recomendadas para la entrega

Realizar manualmente, con datos controlados y sin secretos:

1. Login en 1440 px y 390 px, incluyendo estado de validación.
2. Dashboard en 1440 px con KPIs y gráficas.
3. Dashboard en 390 px verificando drawer y adaptación de tarjetas.
4. Filtraciones con filtros aplicados y paginación.
5. Detalle de filtración con diálogo de confirmación.
6. Contenciones con estados diferenciados.
7. Reportes mostrando las tres tarjetas y el formato derivado.
8. Auditoría con cadena íntegra y diálogo de hash.
9. Notificaciones con estado enviado/fallido o empty state.
10. Usuarios, Roles y Perfil para documentar RBAC y MFA.
