# 💰 Mi Control de Finanzas Personales

> **Aplicación web local e inteligente de gestión presupuestaria y finanzas personales.**  
> Diseñada para ser utilizada sin conocimientos previos de programación. Los datos se almacenan siempre en tu propia hoja de cálculo (Excel o Google Sheets).

---

## 🚀 Inicio Rápido en 1 Clic (Para no programadores)

### Si ya tienes Python instalado:
1. Haz **doble clic** sobre el archivo `run.bat`.
2. El sistema verificará e instalará automáticamente los componentes necesarios la primera vez.
3. Se abrirá automáticamente tu navegador web en `http://localhost:8501` con la aplicación lista para usar.

### Si estás en una computadora nueva sin nada instalado:
1. **Descarga Python**: Entra a [python.org/downloads](https://www.python.org/downloads/) y descarga la versión recomendada para Windows.
2. **Instalación (Paso Crítico)**: Al abrir el instalador, **marca obligatoriamente la casilla inferior**:  
   ☑️ **"Add python.exe to PATH"** (o *"Agregar Python al PATH"*).  
   Luego haz clic en *"Install Now"*.
3. **Lanzar la app**: Entra a la carpeta de este proyecto y haz **doble clic en `run.bat`**. ¡Eso es todo!

---

## 🌟 Características Principales

- **Base de Datos en Hoja de Cálculo**: Todos tus registros se guardan en el archivo `finanzas.xlsx` (o en Google Sheets). Puedes abrirlo directamente con Excel, Numbers o Google Drive cuando quieras.
- **Doble Modo Intercambiable**:
  - **Modo Excel Local** (por defecto): Funciona sin internet y sin configurar nada.
  - **Modo Google Sheets**: Sincronización en la nube para registrar y ver tus finanzas también desde tu teléfono móvil.
- **Registro Rápido (<10 segundos)**: Formulario optimizado con atajos, plantillas frecuentes (Café, Súper, Combustible, Taxi) y botón *"Duplicar último movimiento"*.
- **Categorización Inteligente**: Reconoce palabras como *"Uber"*, *"Carrefour"*, *"Netflix"*, *"Farmacity"* y asigna automáticamente la categoría y subcategoría adecuada.
- **Regla 50/30/20**: Diagnóstico automático entre Necesidades (50%), Deseos (30%) y Ahorro (20%).
- **Estrategias de Cancelación de Deudas**: Simulador interactivo que compara el método **Bola de Nieve** (menor saldo primero) vs. **Avalancha** (mayor tasa de interés primero), calculando exactamente cuánto dinero ahorras en intereses.
- **Motor de Insights en Lenguaje Natural**: Explicaciones claras sobre gastos atípicos, compras hormiga y proyecciones a fin de mes.
- **Cierre de Mes en 1 Clic**: Genera y descarga un informe ejecutivo en HTML/PDF con un resumen imprimible de tu desempeño mensual.
- **Importador Bancario**: Sube tus extractos en CSV o Excel provistos por tu banco y mapea las columnas con detección de duplicados.
- **Copias de Seguridad Atómicas**: Cada cambio crítico crea un respaldo fechado en la carpeta `/backups` para proteger tus datos de cualquier imprevisto.

---

## 🧭 Guía de Uso por Secciones

La barra lateral izquierda contiene 8 secciones especializadas:

1. **📊 Dashboard Ejecutivo**:
   - Tarjetas KPI en tiempo real: Ingresos, Gastos Reales, Ahorro/Inversión, Balance Libre y % del Presupuesto Usado.
   - **Índice de Salud Financiera (0 a 100)** con evaluación de 4 pilares: Tasa de ahorro, Cumplimiento presupuestario, Carga de endeudamiento y Fondo de emergencia.
   - Gráfico de Presupuesto vs. Real (barras con colores condicionales) y Dona de distribución del gasto.
   - Semáforo de estados: Verde (OK), Amarillo (Alerta >80%) y Rojo (Excedido >100%).

2. **⚡ Registrar Movimiento (<10s)**:
   - Botones rápidos con plantillas frecuentes de gastos diarios.
   - Botón *"Duplicar último movimiento"* para registros repetitivos.
   - Formulario ágil con fecha de hoy precargada, autocompletado y validación de duplicados.

3. **📑 Movimientos & Filtros**:
   - Historial completo con filtros dinámicos por tipo, categoría, cuenta y buscador de texto libre.
   - Edición y eliminación segura con confirmación.
   - Botón para descargar tu tabla filtrada en CSV.
   - **Pestaña Importar Banco**: Asistente que lee extractos bancarios en CSV o Excel, autodetecta columnas y omite duplicados.

4. **🎯 Presupuesto Mensual**:
   - Asignación de montos presupuestados por categoría.
   - Botón *"Copiar presupuesto del mes anterior"*.
   - Botón *"Sugerir según promedio de 3 meses"*.
   - Asistente de cálculo 50/30/20.

5. **📈 Análisis Visual & Reportes**:
   - Gráfico de **Evolución Temporal de 12 Meses** (Ingresos vs. Gastos vs. Ahorro).
   - Gráfico de **Cascada (Waterfall)** mostrando el recorrido del dinero desde que ingresa hasta el remanente.
   - **Treemap** interactivo con zoom en subcategorías.
   - **Top 10 Comercios** y análisis de gasto por día de la semana.
   - **Matriz Anual** de categorías × meses con escala de color.
   - Botón de descarga para el **Reporte de Cierre de Mes (HTML/PDF)**.

6. **🏆 Metas & Deudas**:
   - **Metas de Ahorro**: Barras de progreso, proyección estimada de cumplimiento mensual y alertas si vas a tiempo o retrasado.
   - **Plan de Pago de Deudas**: Comparativa visual entre Bola de Nieve y Avalancha con simulador de pagos extra mensuales.

7. **🔄 Recurrentes & Calendario**:
   - Cronograma ordenado con los días del mes en que vencen servicios y cobros de nómina.
   - Indicador de estado (✅ Ya registrado / ⏳ Pendiente).
   - Botón de 1 clic para registrar automáticamente todos los gastos fijos del mes.

8. **⚙️ Configuración & Respaldos**:
   - Selector entre **Modo Excel** y **Modo Google Sheets**.
   - Personalización de símbolo de moneda (`$`, `€`, `COP`, `MXN`, `ARS`, `CLP`, etc.) y formatos.
   - Catálogo editable de Categorías, Cuentas y Métodos de pago.
   - Gestor de copias de seguridad: crea respaldos manuales o restaura cualquier versión anterior.

---

## ☁️ Cómo Conectar Google Sheets (Paso a Paso)

Si deseas sincronizar tus datos con Google Drive para usar la app o ver tu hoja desde el celular:

1. **Crear Proyecto en Google Cloud**:
   - Entra a [console.cloud.google.com](https://console.cloud.google.com/) con tu cuenta de Gmail.
   - Crea un proyecto nuevo llamado *"Mis Finanzas"*.
2. **Habilitar APIs**:
   - En la barra de búsqueda de Google Cloud, busca **Google Drive API** y presiona **Habilitar**.
   - Busca **Google Sheets API** y presiona **Habilitar**.
3. **Crear Cuenta de Servicio**:
   - Ve a **IAM y administración** $\rightarrow$ **Cuentas de servicio**.
   - Haz clic en **Crear cuenta de servicio** y nómbrala `finanzas-bot`.
   - Entra a la cuenta creada, ve a la pestaña **Claves** (Keys) $\rightarrow$ **Agregar clave** $\rightarrow$ **Crear nueva clave en JSON**.
   - Descarga el archivo JSON, cámbiale el nombre a `credentials.json` y guárdalo en la carpeta principal de la app.
4. **Compartir tu Hoja de Cálculo**:
   - En Google Drive, crea una hoja con el nombre **Mis Finanzas Personales**.
   - Compártela dándole permisos de **Editor** al correo que termina en `@...iam.gserviceaccount.com` (que aparece dentro del archivo JSON).
5. **Activar en la App**:
   - En la sección **Configuración** de la aplicación, cambia el selector a **Modo Google Sheets** y ¡listo!

---

## 🛡️ Copias de Seguridad y Seguridad de Datos

- **Tus datos son 100% privados**: La base de datos `finanzas.xlsx` y tus claves de acceso `credentials.json` se guardan exclusivamente en tu computadora. El archivo `.gitignore` garantiza que nunca se compartan ni se suban a internet.
- **Respaldos automáticos**: Cada vez que se ejecuta una acción importante o un borrado, el sistema genera una copia de respaldo fechada en la carpeta `backups/`. Puedes restaurar cualquier copia desde la sección de Configuración.
