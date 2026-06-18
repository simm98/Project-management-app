# Project-management-app
Service to create, update, share, and delete projects information (details, attached documents)/Servicio para crear, actualziar, compartir y borrar projectos y su información (detalles y documentos adjuntados)

# Instalación de app

- Instalar docker-desktop última versión: https://www.docker.com/products/docker-desktop/

- Instalar git última versión: https://git-scm.com/install/

# Clonar repositorio y variables de entorno

- Clonar repo con git clone

- Configurar variables de entorno en archivo .env en ruta: Project-management-app/.env

# Comandos para construir imagen y correr contenedor de manera local:

- docker compose -f docker-compose.yml build --no-cache

- docker compose -f docker-compose.yml up -d

# URL de revision: 

http://localhost:8000/docs → Swagger UI.


# Intrucciones curl:

1. Crear usuario: curl -X POST http://127.0.0.1:8000/auth -H "Content-Type: application/json" -d "{\"login\":\"name\",\"password\":\"1234\",\"repeat_password\":\"1234\"}"


2. Login: curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=name&password=1234"
(genera token que se requerirá para todas las operaciones)


3. Create project: curl -X POST http://127.0.0.1:8000/projects -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d "{\"name\":\"Project EPAM\",\"description\":\"Testing web app\"}"


4. Get projects: curl -X GET http://127.0.0.1:8000/projects -H "Authorization: Bearer TOKEN"


5. Get Project by id: curl -X GET "http://localhost:8000/projects/16/info" -H "Authorization: Bearer TOKEN"                                


6. Update Project by id: curl -X PUT "http://127.0.0.1:8000/projects/2/info" -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -d "{\"name\":\"Nuevo nombre\",\"description\":\"Descripción actualizada\"}"


7. Delete Project by id: curl -X DELETE "http://127.0.0.1:8000/projects/2" -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN"


8. Get documents in Project by id: curl -X GET "http://localhost:8000/projects/16/documents" -H "Authorization: Bearer TOKEN"


9. Add files: curl -X POST "http://127.0.0.1:8000/projects/18/documents" -H "Authorization: Bearer TOKEN" -F "file=@I:/Prueba1.odt"


10. Get documents available for user: curl -X GET "http://127.0.0.1:8000/document/1" -H "Authorization: Bearer TOKEN" --output Prueba1_download.odt


11. Update documents available for user by id : curl -X PUT "http://127.0.0.1:8000/document/1" -H "Authorization: Bearer TOKEN" -F "file=@I:/Prueba1_update.odt" (seleccionar ruta de archivo)


12. Delete documents available for user by id : curl -X DELETE "http://127.0.0.1:8000/document/2" -H "Authorization: Bearer TOKEN"


13. Grant acces to user: curl -X POST "http://127.0.0.1:8000/project/16/invite?user=pancho" -H "Authorization: Bearer TOKEN"