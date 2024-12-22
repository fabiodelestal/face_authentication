import cv2
import os
from cryptography.fernet import Fernet
import numpy as np
import pickle
from tkinter import Tk
from tkinter import filedialog


# Que se puedan bloquear dos archivos en la misma ejecucion
# que el registro de caras sea más completo ya que a veces luego no te detecta
# que los archivos bloqueados por una persona tenga que ser esa persona la que los desbloquee
# mejorar estructura de archivos
# mejorar seguridad del cifrado

# ------------------- Función para registrar una cara ------------------- #
def registrar_cara(nombre):
    ruta = f"caras_registradas/{nombre}"
    os.makedirs(ruta, exist_ok=True)

    camara = cv2.VideoCapture(0)

    # Reducir la resolución de la cámara para mejorar la velocidad
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    contador = 0

    print(f"[INFO] Registrando cara de: {nombre}. Presiona 'q' para salir.")

    while contador < 10:  # Captura 10 imágenes
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in rostros:
            cara = gris[y:y+h, x:x+w]  # Usar escala de grises para ahorrar procesamiento
            cara = cv2.resize(cara, (200, 200))
            cv2.imwrite(f"{ruta}/{contador}.jpg", cara)
            contador += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Registro de Cara", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Registro completado para: {nombre}.")

# ------------------- Función para generar una clave de cifrado ------------------- #
def generar_clave():
    if not os.path.exists("clave.key"):
        clave = Fernet.generate_key()
        with open("clave.key", "wb") as key_file:
            key_file.write(clave)
        print("[INFO] Clave de cifrado generada y almacenada en 'clave.key'.")
    else:
        print("[INFO] Clave de cifrado cargada desde 'clave.key'.")

# ------------------- Función para cargar la clave ------------------- #
def cargar_clave():
    if os.path.exists("clave.key"):
        return open("clave.key", "rb").read()
    else:
        print("[ERROR] No se encontró la clave de cifrado. Genera una nueva clave primero.")
        return None

# ------------------- Función para cifrar archivos ------------------- #
def cifrar_archivos(archivos):
    generar_clave()
    clave = cargar_clave()
    if clave is None:
        return

    fernet = Fernet(clave)

    for archivo in archivos:
        if os.path.isfile(archivo):
            try:
                with open(archivo, "rb") as file:
                    contenido = file.read()
                contenido_cifrado = fernet.encrypt(contenido)
                with open(archivo, "wb") as file:
                    file.write(contenido_cifrado)
                print(f"[INFO] Archivo cifrado: {archivo}")
            except Exception as e:
                print(f"[ERROR] No se pudo cifrar el archivo {archivo}: {e}")

    print(f"[INFO] Todos los archivos seleccionados han sido cifrados.")

# ------------------- Función para descifrar archivos ------------------- #
def descifrar_archivos(archivos):
    clave = cargar_clave()
    if clave is None:
        return

    fernet = Fernet(clave)

    for archivo in archivos:
        if os.path.isfile(archivo):
            try:
                with open(archivo, "rb") as file:
                    contenido_cifrado = file.read()
                contenido_descifrado = fernet.decrypt(contenido_cifrado)
                with open(archivo, "wb") as file:
                    file.write(contenido_descifrado)
                print(f"[INFO] Archivo descifrado: {archivo}")
            except Exception as e:
                print(f"[ERROR] No se pudo descifrar el archivo {archivo}: {e}")

    print(f"[INFO] Todos los archivos seleccionados han sido descifrados.")

# ------------------- Función para entrenar el modelo de reconocimiento facial ------------------- #
def entrenar_modelo():
    labels = []
    faces = []
    label_dict = {}
    current_label = 0

    for nombre in os.listdir("caras_registradas"):
        ruta_cara = os.path.join("caras_registradas", nombre)
        if os.path.isdir(ruta_cara):
            label_dict[current_label] = nombre
            for imagen in os.listdir(ruta_cara):
                img_path = os.path.join(ruta_cara, imagen)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    faces.append(img)
                    labels.append(current_label)
            current_label += 1

    if len(faces) == 0:
        print("[ERROR] No hay caras registradas para entrenar el modelo.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    recognizer.write("modelo_lbph.yml")
    with open("label_dict.pkl", "wb") as f:
        pickle.dump(label_dict, f)
    print("[INFO] Modelo entrenado y guardado.")

# ------------------- Función para autenticar una cara ------------------- #
def autenticar_cara():
    print("[INFO] Iniciando autenticación facial...")
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    camara = cv2.VideoCapture(0)

    # Reducir la resolución de la cámara para mejorar la velocidad
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Verificar si existe el modelo entrenado
    if not os.path.exists("modelo_lbph.yml") or not os.path.exists("label_dict.pkl"):
        print("[ERROR] No se encontró el modelo entrenado. Por favor, entrena el modelo primero.")
        camara.release()
        cv2.destroyAllWindows()
        return False

    # Cargar el modelo y el diccionario de etiquetas
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("modelo_lbph.yml")
    with open("label_dict.pkl", "rb") as f:
        label_dict = pickle.load(f)

    autenticado = False
    intentos = 0

    while not autenticado and intentos < 100:
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in rostros:
            cara = gris[y:y+h, x:x+w]
            cara = cv2.resize(cara, (200, 200))
            label, confidence = recognizer.predict(cara)
            if confidence < 50:  # Umbral de confianza ajustable
                nombre = label_dict[label]
                print(f"[INFO] Autenticación exitosa: {nombre} (Confianza: {confidence:.2f})")
                autenticado = True
                break
            else:
                print(f"[INFO] Rostro desconocido o confianza baja (Confianza: {confidence:.2f})")

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Autenticación Facial", frame)
        intentos += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()

    if autenticado:
        return True
    else:
        print("[ERROR] No se pudo autenticar la cara. Inténtalo nuevamente.")
        return False

# ------------------- Menú Principal ------------------- #
def menu():
    os.makedirs("caras_registradas", exist_ok=True)
    root = Tk()
    root.withdraw()

    while True:
        print("\n--- Sistema de Autenticación Facial ---")
        print("1. Registrar una nueva cara")
        print("2. Entrenar modelo de reconocimiento")
        print("3. Proteger archivos")
        print("4. Desbloquear archivos")
        print("5. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            nombre = input("Introduce el nombre del usuario: ")
            registrar_cara(nombre)

        elif opcion == "2":
            entrenar_modelo()

        elif opcion == "3":
            print("[INFO] Selecciona los archivos a proteger.")
            archivos = filedialog.askopenfilenames(
                title="Selecciona archivos a proteger",
                filetypes=[("Todos los archivos", "*.*"), ("Archivos de texto", "*.txt"), ("Imágenes", "*.jpg;*.png")]
            )
            if archivos:
                cifrar_archivos(archivos)
            else:
                print("[ERROR] No se seleccionaron archivos.")

        elif opcion == "4":
            if autenticar_cara():
                print("[INFO] Selecciona los archivos a desbloquear.")
                archivos = filedialog.askopenfilenames(
                    title="Selecciona archivos a desbloquear",
                    filetypes=[("Todos los archivos", "*.*"), ("Archivos de texto", "*.txt"), ("Imágenes", "*.jpg;*.png")]
                )
                if archivos:
                    descifrar_archivos(archivos)
                else:
                    print("[ERROR] No se seleccionaron archivos.")
            else:
                print("[ERROR] Autenticación fallida.")

        elif opcion == "5":
            print("Saliendo del sistema...")
            break

        else:
            print("[ERROR] Opción no válida.")

# Ejecutar el menú principal
if __name__ == "__main__":
    menu()