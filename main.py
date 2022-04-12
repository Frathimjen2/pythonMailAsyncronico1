import multiprocessing
import sqlite3
import os

CSP_STYLE_SRC = ["'self'", "cdn.jsdelivr.net"]

wsgi_app = "project.wsgi:application"
workers = multiprocessing.cpu_count() * 2 + 1
bind = "0.0.0.0:8000"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
capture_output = True
pidfile = "/var/run/gunicorn/prod.pid"
daemon = True
NOMBRE_BASE_DE_DATOS = "diccionario.db"


def obtener_conexion():
    return sqlite3.connect(NOMBRE_BASE_DE_DATOS)

from celery import Celery

os.environ.setdefault('DJANGO_MODULO_SETTINGS', 'django_project.settings')
os.environ.setdefault('AHORQUILLADO_POR_MULTIPROCESADOR', '1')
app = Celery('django_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
def crear_tablas():
    tablas = [
        """
        CREATE TABLE IF NOT EXISTS diccionario(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palabra TEXT NOT NULL,
            significado TEXT NOT NULL
        );
        """
    ]
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    for tabla in tablas:
        cursor.execute(tabla)


def principal():
    crear_tablas()
    menu = """
a) Agregar nueva palabra
b) Editar palabra existente
c) Eliminar palabra existente
d) Ver listado de palabras
e) Buscar significado de palabra
f) Salir
Elige: """
    eleccion = ""
    while eleccion != "f":
        eleccion = input(menu)
        if eleccion == "a":
            palabra = input("Ingresa la palabra: ")
            # Comprobar si no existe
            posible_significado = buscar_significado_palabra(palabra)
            if posible_significado:
                print(f"La palabra '{palabra}' ya existe")
            else:
                significado = input("Ingresa el significado: ")
                agregar_palabra(palabra, significado)
                print("Palabra agregada")
        if eleccion == "b":
            palabra = input("Ingresa la palabra que quieres editar: ")
            nuevo_significado = input("Ingresa el nuevo significado: ")
            editar_palabra(palabra, nuevo_significado)
            print("Palabra actualizada")
        if eleccion == "c":
            palabra = input("Ingresa la palabra a eliminar: ")
            eliminar_palabra(palabra)
        if eleccion == "d":
            palabras = obtener_palabras()
            print("=== Lista de palabras ===")
            for palabra in palabras:
                # Al leer desde la base de datos se devuelven los datos como arreglo, por
                # lo que hay que imprimir el primer elemento
                print(palabra[0])
        if eleccion == "e":
            palabra = input(
                "Ingresa la palabra de la cual quieres saber el significado: ")
            significado = buscar_significado_palabra(palabra)
            if significado:
                print(f"El significado de '{palabra}' es:\n{significado[0]}")
            else:
                print(f"Palabra '{palabra}' no encontrada")


def agregar_palabra(palabra, significado):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sentencia = "INSERT INTO diccionario(palabra, significado) VALUES (?, ?)"
    cursor.execute(sentencia, [palabra, significado])
    conexion.commit()


def editar_palabra(palabra, nuevo_significado):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sentencia = "UPDATE diccionario SET significado = ? WHERE palabra = ?"
    cursor.execute(sentencia, [nuevo_significado, palabra])
    conexion.commit()


def eliminar_palabra(palabra):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sentencia = "DELETE FROM diccionario WHERE palabra = ?"
    cursor.execute(sentencia, [palabra])
    conexion.commit()


def obtener_palabras():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT palabra FROM diccionario"
    cursor.execute(consulta)
    return cursor.fetchall()


def buscar_significado_palabra(palabra):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    consulta = "SELECT significado FROM diccionario WHERE palabra = ?"
    cursor.execute(consulta, [palabra])
    return cursor.fetchone()


if __name__ == '__main__':
    principal()