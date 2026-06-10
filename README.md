# Mundial FIFA 2026 - Proyecto escolar full stack

Aplicacion simple para simular el Mundial 2026 con backend en Python Flask y frontend en HTML, CSS y JavaScript Vanilla.

## Estructura

```text
backend/
  app.py
  routes/
  services/
  database/
  requirements.txt
frontend/
  index.html
  groups.html
  playoffs.html
  stats.html
  css/
  js/
```

## Como ejecutar

1. Abrir esta carpeta en Visual Studio Code.
2. Crear entorno virtual e instalar dependencias:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

3. Abrir `frontend/index.html` en el navegador.

La API queda funcionando en `http://127.0.0.1:5000/api`.

## Funciones

- 48 selecciones en 12 grupos.
- Fixture de fase de grupos.
- Carga manual de resultados.
- Tabla de posiciones automatica.
- Carga manual de resultados.
- Playoffs desde dieciseisavos hasta final.
- Campeon, MVP, goleadores y promedio de goles.
- Penales cargados manualmente cuando una eliminatoria termina empatada.
- Persistencia en `backend/database/worldcup.json`.

## Nota

Los grupos usados fueron tomados como referencia de una publicacion de U.S. Soccer del 14 de mayo de 2026 sobre los grupos del Mundial 2026.
