# Selector Interactivo de Tuberías y Accesorios

Aplicación educativa en Streamlit basada en `Selector Interactivo de Tuberías y Accesorios.pdf`.

## Ejecutar localmente

1. Instala Python 3.10 o posterior.
2. Abre una terminal en esta carpeta.
3. Ejecuta:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit abrirá la aplicación en el navegador.

## Publicar para compartir con el equipo

1. Crea un repositorio en GitHub.
2. Sube `app.py` y `requirements.txt`.
3. Entra a https://share.streamlit.io/ e inicia sesión con GitHub.
4. Crea una app seleccionando el repositorio, la rama y `app.py`.
5. Comparte el enlace generado con el equipo.

## Alcance y seguridad

- Los datos de los tres casos están transcritos del PDF.
- Los campos que el PDF no especifica se mantienen como no especificados.
- El orden de candidatos y las alertas de temperatura son heurísticas de cribado, no resultados certificados.
- La compatibilidad química no se considera validada para ninguna mezcla real. Confirmar concentraciones, temperatura, presión, juntas y uniones con fichas de fabricantes.
- No usar como única base para diseñar, construir u operar una instalación real.
