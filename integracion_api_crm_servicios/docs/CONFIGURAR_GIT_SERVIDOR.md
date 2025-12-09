# Configurar Git desde Cero en el Servidor

Esta guía te ayudará a configurar Git completamente en el servidor.

## Paso 1: Configurar Git (nombre y email)

```bash
# Configurar tu nombre
git config --global user.name "Juan Pablo Silva"

# Configurar tu email (el mismo que usas en GitHub)
git config --global user.email "juan.silva@uniacc.cl"
```

Verifica la configuración:
```bash
git config --global --list
```

---

## Paso 2: Verificar o Crear Clave SSH

### Opción A: Si ya tienes una clave SSH en tu computador

Necesitas copiar la clave SSH desde tu computador al servidor:

**Desde tu computador:**
```bash
# Ver el contenido de tu clave pública
cat ~/.ssh/id_ed25519_uniacc.pub
```

**En el servidor:**
```bash
# Crear directorio .ssh si no existe
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Agregar la clave pública (copia el contenido desde tu computador)
nano ~/.ssh/id_ed25519_uniacc.pub
# Pega el contenido de la clave pública y guarda (Ctrl+X, Y, Enter)

# Si también necesitas la clave privada (para hacer push):
nano ~/.ssh/id_ed25519_uniacc
# Pega el contenido de la clave privada y guarda

# Ajustar permisos
chmod 600 ~/.ssh/id_ed25519_uniacc
chmod 644 ~/.ssh/id_ed25519_uniacc.pub
```

### Opción B: Crear una nueva clave SSH en el servidor

```bash
# Generar nueva clave SSH
ssh-keygen -t ed25519 -C "tu.email@uniacc.cl" -f ~/.ssh/id_ed25519_uniacc

# Cuando te pregunte por passphrase, puedes dejarlo vacío o poner una contraseña
```

Luego necesitas agregar la clave pública a tu cuenta de GitHub:
```bash
# Mostrar la clave pública
cat ~/.ssh/id_ed25519_uniacc.pub
```

Copia el contenido y agrégalo en GitHub:
1. Ve a GitHub → Settings → SSH and GPG keys
2. Click en "New SSH key"
3. Pega la clave pública
4. Guarda

---

## Paso 3: Configurar archivo SSH config

```bash
# Crear o editar el archivo config
nano ~/.ssh/config
```

Agrega el siguiente contenido:
```
Host github-uniacc  
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_uniacc
  IdentitiesOnly yes
```

Guarda el archivo (Ctrl+X, Y, Enter) y ajusta permisos:
```bash
chmod 600 ~/.ssh/config
```

---

## Paso 4: Probar la conexión SSH

```bash
ssh -T github-uniacc
```

Deberías ver:
```
Hi jpuniacc! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Paso 5: Configurar el repositorio Git

```bash
# Navegar al directorio del proyecto
cd /home/cl159906175/integracion_nimbi

# Verificar el estado
git status

# Verificar el remote actual
git remote -v
```

Si el remote no está configurado o está mal, configúralo:
```bash
# Eliminar remote si existe
git remote remove origin 2>/dev/null

# Agregar remote correcto
git remote add origin git@github-uniacc:jpuniacc/integracion-nimbi.git

# Verificar
git remote -v
```

---

## Paso 6: Verificar que hay commits

```bash
git log --oneline -5
```

Si no hay commits, necesitas hacer uno:
```bash
git add .
git commit -m "feat: Configuración inicial del proyecto"
```

---

## Paso 7: Hacer push

```bash
# Verificar en qué rama estás
git branch

# Hacer push (usa 'master' o 'main' según corresponda)
git push -u origin master
```

O si la rama se llama `main`:
```bash
git push -u origin main
```

---

## Comandos Rápidos de Referencia

```bash
# Configurar Git
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@uniacc.cl"

# Verificar configuración
git config --global --list

# Verificar conexión SSH
ssh -T github-uniacc

# Ver estado del repositorio
git status

# Ver rama actual
git branch

# Ver remotes
git remote -v

# Agregar cambios
git add .

# Hacer commit
git commit -m "mensaje descriptivo"

# Hacer push
git push
```

---

## Solución de Problemas

### Error: "Permission denied (publickey)"
- Verifica que la clave SSH esté en GitHub
- Verifica los permisos: `chmod 600 ~/.ssh/id_ed25519_uniacc`
- Prueba la conexión: `ssh -T github-uniacc`

### Error: "src refspec main does not match any"
- Verifica que hayas hecho commit: `git log`
- Verifica la rama: `git branch`
- Usa `master` en lugar de `main` si es necesario

### Error: "Could not resolve hostname github-uniacc"
- Verifica que el archivo `~/.ssh/config` exista y esté bien configurado
- Verifica permisos: `chmod 600 ~/.ssh/config`

---

**Última actualización:** Noviembre 2025

