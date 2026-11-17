# Colmillo Blanco — Plan de contenido

Página web con el calendario de contenido vigente de Colmillo Blanco (Agencia ERRE).

Se actualiza quincena a quincena: `build_site.py` genera `index.html` a partir del HTML maestro de la quincena activa (en el repo del cliente, carpeta `_Contenido/2026/<Mes>/<Quincena>/`) y de las imágenes/videos finales en `assets/`.

## Actualizar a una quincena nueva

1. Copiar las imágenes y videos finales de la nueva quincena a `assets/img/` y `assets/video/`.
2. Ajustar `build_site.py` (lista `PIECES`) con las fechas y archivos de la nueva quincena.
3. `python3 build_site.py "<ruta al html maestro de la quincena>"`
4. `git add -A && git commit -m "Actualiza a <quincena>" && git push`

GitHub Pages redeploya solo con cada push.
