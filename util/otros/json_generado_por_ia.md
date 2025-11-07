{
"category_id": 17,
"defaults": {
"type": "TEXT",
"tags": "clonar_proyecto",
"is_favorite": 1,
"is_sensitive": 0
},
"items": [
{
"label": "Clonar repositorio desde URL",
"content": "git clone https://github.com/usuario/nombre-repo.git",
"description": "Clona el repositorio remoto en tu equipo"
},
{
"label": "Ingresar al directorio del proyecto",
"content": "cd nombre-repo",
"description": "Accede a la carpeta del proyecto recién clonado"
},
{
"label": "Ver estado inicial del repositorio",
"content": "git status",
"description": "Muestra archivos sin seguimiento o cambios locales"
},
{
"label": "Instalar dependencias con npm",
"type": "CODE",
"content": "npm install",
"description": "Descarga e instala todas las dependencias del proyecto Node.js"
},
{
"label": "Instalar dependencias con yarn",
"type": "CODE",
"content": "yarn install",
"description": "Alternativa si el proyecto usa yarn"
},
{
"label": "Crear archivo .env desde plantilla",
"type": "CODE",
"content": "cp .env.example .env",
"description": "Copia el archivo de variables de entorno para configuración local"
},
{
"label": "Actualizar dependencias",
"type": "CODE",
"content": "npm update",
"description": "Actualiza los paquetes del proyecto a versiones más recientes"
},
{
"label": "Compilar y ejecutar proyecto (Angular / Node / React)",
"type": "CODE",
"content": "npm run dev",
"description": "Inicia el entorno de desarrollo del proyecto"
},
{
"label": "Ver ramas disponibles",
"type": "CODE",
"content": "git branch -a",
"description": "Lista todas las ramas locales y remotas"
},
{
"label": "Cambiar a una rama específica",
"type": "CODE",
"content": "git checkout nombre-rama",
"description": "Cambia de rama para trabajar en otra versión del proyecto"
}
]
}
