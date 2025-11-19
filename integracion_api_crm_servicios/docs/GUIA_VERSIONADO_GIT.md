# Guía de Versionado con Git - Integración Nimbi

Esta guía explica paso a paso cómo versionar el código en el repositorio Git.

## Configuración SSH

Ya tienes configurado el host SSH personalizado en `~/.ssh/config`:
```
Host github-uniacc  
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_uniacc
  IdentitiesOnly yes
```

**Repositorio:** `git@github.com:jpuniacc/integracion-nimbi.git`

---

## Pasos para Versionar el Código

### Paso 1: Verificar la conexión SSH

Primero, verifica que la conexión SSH funciona correctamente:

```bash
ssh -T github-uniacc
```

Deberías ver un mensaje como:
```
Hi jpuniacc! You've successfully authenticated, but GitHub does not provide shell access.
```

Si ves un error, verifica:
- Que la clave SSH esté agregada al agente: `ssh-add ~/.ssh/id_ed25519_uniacc`
- Que la clave esté agregada a tu cuenta de GitHub

---

### Paso 2: Navegar al directorio del proyecto

```bash
cd /home/cl159906175/integracion_nimbi
```

---

### Paso 3: Inicializar el repositorio Git (si no existe)

Si el repositorio no está inicializado:

```bash
git init
```

---

### Paso 4: Configurar el repositorio remoto

Agrega el repositorio remoto usando el host SSH personalizado:

```bash
git remote add origin git@github-uniacc:jpuniacc/integracion-nimbi.git
```

Si ya existe un remote, puedes actualizarlo:

```bash
git remote set-url origin git@github-uniacc:jpuniacc/integracion-nimbi.git
```

Verifica que el remote esté configurado correctamente:

```bash
git remote -v
```

Deberías ver:
```
origin  git@github-uniacc:jpuniacc/integracion-nimbi.git (fetch)
origin  git@github-uniacc:jpuniacc/integracion-nimbi.git (push)
```

---

### Paso 5: Crear archivo .gitignore

Crea un archivo `.gitignore` en la raíz del proyecto para excluir archivos que no deben versionarse:

```bash
cat > /home/cl159906175/integracion_nimbi/.gitignore << 'EOF'
# Entornos virtuales
.venv/
.venv-crm/
venv/
env/
ENV/

# Variables de entorno
.env
.env.local
.env.*.local

# Archivos CSV temporales
integracion_api_crm_servicios/temp_csv/*.csv

# Logs
integracion_api_crm_servicios/scripts/logs/*.log

# Backups
integracion_api_crm_servicios/scripts/backups/*.json

# Archivos de Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Sistema operativo
.DS_Store
Thumbs.db

# Archivos temporales
*.tmp
*.bak
*.swp
EOF
```

---

### Paso 6: Agregar archivos al staging

Agrega todos los archivos que quieres versionar:

```bash
git add .
```

O si prefieres agregar archivos específicos:

```bash
# Agregar solo scripts
git add integracion_api_crm_servicios/scripts/*.py

# Agregar solo SQL
git add sql/*.sql

# Agregar documentación
git add integracion_api_crm_servicios/docs/*.md

# Agregar configuración
git add integracion_api_crm_servicios/requirement.txt
```

Verifica qué archivos se agregaron:

```bash
git status
```

---

### Paso 7: Hacer commit de los cambios

Crea un commit con un mensaje descriptivo:

```bash
git commit -m "feat: Agregar funcionalidad de generación CSV y subida SFTP

- Agregar generación de CSV a actualizar_datos_identificadores_y_data_operacional.py
- Agregar generación de CSV a actualizar_beneficios_alumnos.py
- Agregar script actualizar_notas_y_asistencia.py con generación CSV y SFTP
- Actualizar ejecutar_actualizaciones_diarias.sh para incluir nuevo script
- Agregar documentación RESUMEN_TABLAS_Y_CAMPOS.md
- Configurar SFTP con manejo de chroot jail"
```

O un mensaje más simple:

```bash
git commit -m "feat: Agregar generación CSV y subida SFTP para scripts de integración"
```

---

### Paso 8: Verificar la rama actual

Verifica en qué rama estás:

```bash
git branch
```

Si no hay ramas, Git creará automáticamente `main` o `master` en el primer push.

---

### Paso 9: Hacer push al repositorio remoto

Si es la primera vez que haces push:

```bash
git push -u origin main
```

O si la rama se llama `master`:

```bash
git push -u origin master
```

Si ya has hecho push antes:

```bash
git push
```

---

### Paso 10: Verificar que el push fue exitoso

Verifica en GitHub que los archivos se hayan subido correctamente, o ejecuta:

```bash
git log --oneline -5
```

---

## Comandos Útiles para el Futuro

### Ver el estado del repositorio
```bash
git status
```

### Ver los cambios realizados
```bash
git diff
```

### Ver el historial de commits
```bash
git log --oneline
```

### Agregar cambios y hacer commit
```bash
git add .
git commit -m "mensaje descriptivo"
git push
```

### Ver los remotes configurados
```bash
git remote -v
```

### Actualizar desde el repositorio remoto
```bash
git pull origin main
```

---

## Estructura Recomendada de Commits

Usa mensajes de commit descriptivos siguiendo el formato:

```
tipo: descripción corta

Descripción detallada (opcional)
```

Tipos comunes:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bugs
- `docs`: Cambios en documentación
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

Ejemplos:
```bash
git commit -m "feat: Agregar generación CSV para notas y asistencia"
git commit -m "fix: Corregir manejo de chroot jail en SFTP"
git commit -m "docs: Actualizar documentación de tablas"
```

---

## Solución de Problemas

### Error: "Permission denied (publickey)"
- Verifica que la clave SSH esté agregada: `ssh-add ~/.ssh/id_ed25519_uniacc`
- Verifica la conexión: `ssh -T github-uniacc`

### Error: "remote origin already exists"
- Actualiza el remote: `git remote set-url origin git@github-uniacc:jpuniacc/integracion-nimbi.git`

### Error: "failed to push some refs"
- Primero haz pull: `git pull origin main --rebase`
- Luego intenta push nuevamente: `git push`

### Deshacer cambios no commiteados
```bash
git restore <archivo>
# o para todos los archivos
git restore .
```

### Deshacer el último commit (manteniendo cambios)
```bash
git reset --soft HEAD~1
```

---

## Notas Importantes

1. **Nunca versiones archivos sensibles**: El archivo `.env` con contraseñas NO debe estar en Git
2. **Revisa el .gitignore**: Asegúrate de que archivos temporales, logs y backups no se suban
3. **Commits frecuentes**: Haz commits pequeños y frecuentes con mensajes descriptivos
4. **Pull antes de push**: Si trabajas en equipo, siempre haz `git pull` antes de `git push`

---

**Última actualización:** Noviembre 2025

