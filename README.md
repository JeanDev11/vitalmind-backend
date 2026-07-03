# VitalMind — Backend

Ecosistema integral de monitoreo y gestión del bienestar psicopedagógico para la Facultad de Ingeniería de Sistemas e Informática (FISI) — UNMSM. Backend del MVP que digitaliza el flujo de tamizaje psicológico (Cuestionario Caracterológico de Gastón Berger) y la gestión de citas de la Unidad de Apoyo y Orientación al Estudiante (UNAYOE).

---

## Stack

| Componente | Tecnología |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migraciones | Alembic |
| Base de datos | PostgreSQL (Neon) |
| IA | Google Gemini (`gemini-1.5-flash`) |
| Auth | JWT (personal) + token efímero hash (alumnos) |
| Email | SMTP |

---

## Arquitectura

El dominio se organiza en dos subdominios conectados por `resultado_tamizaje`:

- **Tamizaje** — creación de evaluaciones masivas, generación de tokens de acceso, cuestionario, cálculo de perfil.
- **Agenda** — disponibilidad de la psicóloga y gestión de citas.

```text
app/
├── models/                  # 14 tablas SQLAlchemy
├── schemas/                 # Validación Pydantic (request/response)
├── services/                # Lógica de negocio (incluye motor de calificación)
│   └── calificacion/        # ICalculadorPerfil + implementaciones (Berger / IA)
├── routers/                 # Endpoints agrupados por dominio
└── utils/                   # Seguridad (JWT, hash, tokens) y email

seeds/                       # Carga del instrumento Gastón Berger (30 preguntas, 8 perfiles)
migrations/                  # Alembic
```

### Decisión clave: modelo genérico de respuestas

Las respuestas del cuestionario se almacenan en `respuesta_item`, una tabla genérica vinculada a `pregunta` por FK, y no una tabla por instrumento. Esto permite agregar nuevos tests (la batería clínica completa contempla hasta ocho) sin requerir migraciones del esquema de base de datos.

### Decisión clave: acceso efímero del alumno

El alumno no posee una cuenta. Su única credencial es un token de un solo uso (`token_acceso`), almacenado como hash SHA-256 y nunca en texto plano. El flujo de envío del cuestionario es una transacción atómica que:

1. Persiste las respuestas.
2. Invalida el token.
3. Marca la sesión como enviada.
4. Calcula el perfil.

Todo el proceso se ejecuta bajo el principio **todo o nada**.

### Motor de calificación

Se implementa mediante la interfaz `ICalculadorPerfil`, con dos estrategias intercambiables según `instrumento.tipo_calificacion`:

- **CalculadorBergerInterno**: algoritmo propio basado en la matriz de decisión de Vicuña Peri (3 ejes bipolares, umbrales E ≥ 54 / A ≥ 52 / R ≥ 52 → 8 perfiles).
- **CalculadorViaIA**: delega la interpretación cualitativa (diagnóstico, características y recomendaciones) a Gemini, sin bloquear el resultado numérico si la API falla.

---

## Instalación

```bash
git clone https://github.com/JeanDev11/vitalmind-backend.git
cd vitalmind-backend

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Completar con credenciales reales
```

### Variables de entorno requeridas (`.env`)

```env
DATABASE_URL=postgresql://usuario:password@host:5432/vitalmind
SECRET_KEY=clave_segura_de_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

GEMINI_API_KEY=tu_api_key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=correo@gmail.com
SMTP_PASSWORD=app_password
EMAIL_FROM=VitalMind FISI <correo@gmail.com>
```

### Migraciones y carga inicial

```bash
alembic upgrade head
python -m seeds.run_all
```

El proceso de *seed* carga:

- Instrumento Gastón Berger.
- 30 preguntas (actualmente con enunciados *placeholder*, pendientes de reemplazo por el cuestionario físico de Vicuña Peri).
- Los ocho perfiles caracterológicos.

### Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

Servicios disponibles:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

## Flujo funcional (resumen para el frontend)

1. **Psicóloga**
   - `POST /auth/login`
   - Obtiene un JWT.

2. Crea un tamizaje en estado **borrador**.

3. Activa el tamizaje e invita alumnos (genera tokens y envía correos electrónicos).

4. **Alumno**
   - Accede sin cuenta mediante:
     ```
     GET /cuestionario/iniciar?token=...
     ```
   - Responde el cuestionario.
   - Envía:
     ```
     POST /cuestionario/enviar
     ```
     Se ejecuta la transacción atómica de respuestas + cálculo del perfil.

5. **Psicóloga**
   - Consulta resultados:
     ```
     GET /resultados/tamizaje/{id}
     ```
     con filtrado por `nivel_riesgo`.
   - Agenda citas:
     ```
     POST /citas/
     ```
     utilizando sus propios horarios disponibles.

### Interpretación mediante IA

- Riesgo **crítico** (Nervioso): interpretación automática.
- Riesgo **monitoreo** (Sentimental y Colérico): interpretación bajo demanda mediante:

```text
POST /resultados/interpretar-ia
```

---

## Notas para el equipo de frontend

- El **portal del alumno** utiliza únicamente un token recibido por parámetro de consulta (`query param`); no requiere autenticación ni JWT.
- El **panel administrativo** requiere:

```http
Authorization: Bearer <token>
```

en cada solicitud posterior al inicio de sesión.

- Los endpoints de catálogo (`/cuestionario/iniciar`) ya devuelven preguntas y opciones ordenadas.
- Swagger (`/docs`) funciona como contrato vivo de la API mientras se completa la documentación formal.

---

## Equipo

Proyecto académico — FISI, UNMSM.