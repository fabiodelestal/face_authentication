import cv2
import os
from cryptography.fernet import Fernet
import numpy as np
import pickle
from tkinter import Tk
from tkinter import filedialog

# ------------------- Función para registrar una cara ------------------- #
def registrar_cara(nombre):
    ruta = f"datos/caras_registradas/{nombre}"
    os.makedirs(ruta, exist_ok=True)

    camara = cv2.VideoCapture(0)
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    contador = 0

    print(f"[INFO] Registrando cara de: {nombre}. Presiona 'q' para salir.")

    while contador < 20:  # Captura 20 imágenes para mejorar el modelo
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in rostros:
            cara = gris[y:y+h, x:x+w]
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

# ------------------- Función para generar una clave por usuario ------------------- #
def generar_clave(nombre):
    ruta_clave = f"datos/claves/{nombre}.key"
    os.makedirs("datos/claves", exist_ok=True)
    clave = Fernet.generate_key()
    with open(ruta_clave, "wb") as key_file:
        key_file.write(clave)
    print(f"[INFO] Clave de cifrado generada para {nombre}.")
    return clave

# ------------------- Función para cargar la clave ------------------- #
def cargar_clave(nombre):
    ruta_clave = f"datos/claves/{nombre}.key"
    if os.path.exists(ruta_clave):
        return open(ruta_clave, "rb").read()
    else:
        print(f"[ERROR] No se encontró la clave para {nombre}. Registra primero la cara.")
        return None

# ------------------- Función para cifrar archivos ------------------- #
def cifrar_archivos(archivos, nombre):
    clave = cargar_clave(nombre) or generar_clave(nombre)
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

    print(f"[INFO] Archivos cifrados correctamente.")

# ------------------- Función para descifrar archivos ------------------- #
def descifrar_archivos(archivos, nombre):
    clave = cargar_clave(nombre)
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

    print(f"[INFO] Archivos descifrados correctamente.")

# ------------------- Función para entrenar el modelo de reconocimiento facial ------------------- #
def entrenar_modelo():
    labels = []
    faces = []
    label_dict = {}
    current_label = 0

    for nombre in os.listdir("datos/caras_registradas"):
        ruta_cara = os.path.join("datos/caras_registradas", nombre)
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

    os.makedirs("datos/modelos", exist_ok=True)
    recognizer.write("datos/modelos/modelo_lbph.yml")
    with open("datos/modelos/label_dict.pkl", "wb") as f:
        pickle.dump(label_dict, f)
    print("[INFO] Modelo entrenado y guardado.")

# ------------------- Función para autenticar una cara ------------------- #
def autenticar_cara():
    print("[INFO] Iniciando autenticación facial...")
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    camara = cv2.VideoCapture(0)

    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not os.path.exists("datos/modelos/modelo_lbph.yml") or not os.path.exists("datos/modelos/label_dict.pkl"):
        print("[ERROR] No se encontró el modelo entrenado.")
        camara.release()
        cv2.destroyAllWindows()
        return None

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("datos/modelos/modelo_lbph.yml")
    with open("datos/modelos/label_dict.pkl", "rb") as f:
        label_dict = pickle.load(f)

    autenticado = False
    nombre_usuario = None

    print("[INFO] Buscando rostro en la cámara. Asegúrate de estar frente a la cámara...")
    while not autenticado:
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)

        if len(rostros) == 0:
            print("[INFO] No se detectaron rostros. Por favor, ajusta tu posición.")
        
        for (x, y, w, h) in rostros:
            print("[INFO] Rostro detectado. Procesando...")
            cara = gris[y:y+h, x:x+w]
            cara = cv2.resize(cara, (200, 200))
            label, confidence = recognizer.predict(cara)
            if confidence < 50:
                nombre_usuario = label_dict[label]
                print(f"[INFO] Autenticación exitosa: {nombre_usuario} (Confianza: {confidence:.2f})")
                autenticado = True
                break
            else:
                print(f"[INFO] Rostro no reconocido. Confianza: {confidence:.2f}. Intentando nuevamente...")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()
    return nombre_usuario

# ------------------- Menú Principal ------------------- #
def menu():
    os.makedirs("datos/caras_registradas", exist_ok=True)
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
            nombre = autenticar_cara()
            if nombre:
                print("[INFO] Selecciona los archivos a proteger.")
                archivos = filedialog.askopenfilenames(
                    title="Selecciona archivos a proteger",
                    filetypes=[("Todos los archivos", "*.*")]
                )
                if archivos:
                    cifrar_archivos(archivos, nombre)
                else:
                    print("[ERROR] No se seleccionaron archivos.")

        elif opcion == "4":
            nombre = autenticar_cara()
            if nombre:
                print("[INFO] Selecciona los archivos a desbloquear.")
                try:
                    archivos = filedialog.askopenfilenames(
                        title="Selecciona archivos a desbloquear",
                        filetypes=[("Todos los archivos", "*.*")]
                    )
                    if archivos:
                        descifrar_archivos(archivos, nombre)
                    else:
                        print("[ERROR] No se seleccionaron archivos.")
                except Exception as e:
                    print(f"[ERROR] Error al seleccionar archivos: {e}")

        elif opcion == "5":
            print("Saliendo del sistema...")
            break

        else:
            print("[ERROR] Opción no válida.")

if __name__ == "__main__":
    menu()
