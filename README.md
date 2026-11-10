# Publicar un mensaje en Issues de GitHub

Este proyecto publica el contenido de un archivo de texto como una issue en cada repositorio de una lista. Se ejecuta desde Terminal con Python y utiliza tu sesión de GitHub CLI (`gh`).

## Resultado del envío del 10 de noviembre de 2026

Se procesaron los 61 repositorios únicos extraídos de la columna E de la hoja **Participantes y repos** del Excel. Se crearon **58 issues** con la cuenta `therobertsweb`. Los enlaces están en `issues_enviadas.jsonl`.

No se pudo publicar en estos tres repositorios porque la consulta devolvió un error de acceso:

- `mapluisch/Muse-Maker`
- `tsetse012/60-second-fire-check`
- `sreenathmmenon/doodlume`

Un error 404 puede significar que el repositorio no existe o que tu cuenta no tiene acceso. El script también omite las respuestas 410. Haber terminado la ejecución no significa que se haya podido publicar en todos los destinos.

## Archivos que debes conservar

| Archivo | Para qué sirve |
| --- | --- |
| `enviar_issues.py` | Código que revisa los destinos y publica. |
| `mensaje.txt` | Contenido de la issue; admite Markdown. |
| `repositorios.txt` | Destinatarios, uno por línea. |
| `issues_enviadas.jsonl` | Historial local de publicaciones exitosas, con repositorio, título y enlace. |
| `directorio_repositorios_meta_cerebral_valley.xlsx` | Directorio original del que se extrajo la lista. |

Puedes copiar la carpeta a otra ubicación. Los archivos predeterminados se buscan junto al script. **El script lee `repositorios.txt`, no el Excel directamente**: los cambios posteriores en el Excel no se sincronizan automáticamente.

## 1. Requisitos

- Python **3.9 o posterior**. No necesitas instalar paquetes con `pip`.
- [GitHub CLI](https://cli.github.com/), que proporciona el comando `gh`.
- Una cuenta de GitHub con acceso a los repositorios y permiso para crear issues.
- Conexión a Internet para publicar.

Comprueba las instalaciones en Terminal:

```bash
python3 --version
gh --version
```

Si falta Python, instálalo desde [python.org](https://www.python.org/downloads/). Si falta `gh`, sigue las instrucciones de instalación en su web oficial.

## 2. Abrir la carpeta

```bash
cd /Users/Guest/Desktop/github
```

Si mueves la carpeta, cambia esa ruta. Usa comillas si la ruta contiene espacios.

## 3. Iniciar sesión en GitHub

```bash
gh auth login --hostname github.com
```

Sigue las instrucciones de GitHub CLI para autenticarte. Después comprueba la cuenta activa:

```bash
gh auth status --hostname github.com
```

Las issues se publican con esa cuenta. No guardes contraseñas ni tokens en el script ni en el mensaje.

## 4. Preparar el mensaje y los destinatarios

Edita `mensaje.txt` con un editor de texto y guárdalo como texto UTF-8. El script publica su contenido tal como está.

Edita `repositorios.txt` para elegir los destinos. Admite estos dos formatos:

```text
propietario/repositorio
https://github.com/propietario/otro-repositorio
```

Las líneas vacías y las que comienzan con `#` se ignoran. Puedes quitar una línea o comentarla con `#` para excluir un repositorio. Las entradas repetidas se procesan una sola vez.

## 5. Revisar sin publicar

```bash
python3 enviar_issues.py
```

Muestra el título, el mensaje y los destinatarios. No necesita autenticación ni hace consultas a GitHub: esta vista previa no comprueba si los repositorios están accesibles.

El título predeterminado es:

```text
Questions about originality criteria — Meta AI Developer Hackathon 2026
```

Para elegir otro título:

```bash
python3 enviar_issues.py --titulo "Título de mi nuevo mensaje"
```

## 6. Publicar

Para enviar el mensaje con el título predeterminado:

```bash
python3 -u enviar_issues.py --enviar
```

**`--enviar` publica inmediatamente; no hay otra pregunta de confirmación.** La opción `-u` permite ver el progreso de Python sin retrasos de almacenamiento de salida.

Para publicar un mensaje nuevo con otro título:

```bash
python3 -u enviar_issues.py --titulo "Título de mi nuevo mensaje" --enviar
```

Usa el mismo título en la vista previa y en el envío. El script espera tres segundos después de cada publicación.

También puedes usar otros archivos sin cambiar los originales:

```bash
python3 enviar_issues.py --repos otros_repos.txt --mensaje otro_mensaje.txt --titulo "Nueva consulta"
python3 -u enviar_issues.py --repos otros_repos.txt --mensaje otro_mensaje.txt --titulo "Nueva consulta" --enviar
```

Las rutas que pases con `--repos` y `--mensaje` son relativas a la carpeta de Terminal, salvo que uses rutas absolutas. El historial siempre se guarda junto al script.

## 7. Entender los resultados

- **`Creada: https://...`**: GitHub confirmó la creación; el enlace se guardó en el historial.
- **`Omitido (ya registrado)`**: el historial local ya contiene ese repositorio y título.
- **`Omitido (título existente)`**: GitHub ya tiene una issue con exactamente ese título, abierta o cerrada, aunque la haya creado otra persona.
- **`Omitido (repositorio no accesible o Issues desactivadas)`**: la consulta devolvió 404 o 410; continúa con el siguiente destino.
- **`Envío detenido`**: ocurrió otro error; la ejecución se detiene y las publicaciones anteriores permanecen en GitHub.

Para ver el historial:

```bash
cat issues_enviadas.jsonl
```

Cada línea es un objeto JSON con los campos `repo`, `titulo` y `url`. Las omisiones no se guardan en ese archivo; se muestran en Terminal.

## 8. Reanudar y evitar duplicados

Si se interrumpe el envío, vuelve a ejecutar **el mismo comando con el mismo título**. El script omitirá los éxitos registrados y consultará las issues abiertas y cerradas de los demás repositorios antes de crear una nueva.

Conserva `issues_enviadas.jsonl`. Cambiar únicamente el contenido de `mensaje.txt` no vuelve a enviar una issue con el mismo título ni modifica una existente. Para una comunicación distinta, usa un título distinto; para corregir una issue ya publicada, edítala en GitHub.

Ejecuta una sola instancia del script a la vez: la comprobación y la creación son operaciones separadas y dos ejecuciones simultáneas podrían crear duplicados.

Para detenerlo manualmente, pulsa **Ctrl+C**. Si lo interrumpes justo durante una publicación, revisa GitHub antes de reanudar para comprobar su resultado.

## Solución de problemas

### `gh` o `python3`: comando no encontrado

Instala la herramienta correspondiente y vuelve a abrir Terminal.

### Sesión inválida o token caducado

```bash
gh auth login --hostname github.com
gh auth status --hostname github.com
```

Si funciona en Terminal pero falla dentro de un entorno restringido, puede faltar acceso a la red o al llavero de credenciales de macOS.

### Error 403, permisos o límite de GitHub

Lee el error de Terminal. Comprueba que tu cuenta puede crear issues en ese repositorio. Si GitHub indica un límite de solicitudes, espera el plazo indicado antes de reanudar. El script no reintenta automáticamente estos errores.

### Error 404 o 410

Comprueba la dirección del repositorio y su pestaña Issues con la misma cuenta. Si el repositorio está privado, eliminado o no admite issues, el script no puede publicar allí.

### No se encuentra un archivo o el historial tiene JSON inválido

Comprueba que existen los archivos indicados. Si editaste el historial manualmente, restaura una copia válida: cada línea debe contener un objeto JSON completo. No borres el historial como método habitual para repetir envíos.

## Ayuda y documentación

```bash
python3 enviar_issues.py --help
```

Documentación oficial del comando usado para publicar: [gh issue create](https://cli.github.com/manual/gh_issue_create).
# publica_issuse_github
