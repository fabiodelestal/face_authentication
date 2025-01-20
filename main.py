import cv2
import os
from cryptography.fernet import Fernet
import numpy as np
import pickle
from tkinter import Tk
from tkinter import filedialog
from tkinter import Tk, Button, Label, Entry, filedialog, messagebox
from functools import partial



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
            cara = gris[y:y + h, x:x + w]
            cara = cv2.resize(cara, (200, 200))
            cv2.imwrite(f"{ruta}/{contador}.jpg", cara)
            contador += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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


# ------------------- Función para cifrar archivos y carpetas ------------------- #
def cifrar_archivos_o_carpetas(ruta, nombre):
    clave = cargar_clave(nombre) or generar_clave(nombre)
    fernet = Fernet(clave)

    if os.path.isfile(ruta):
        # Cifrar un único archivo
        try:
            with open(ruta, "rb") as file:
                contenido = file.read()
            contenido_cifrado = fernet.encrypt(contenido)
            with open(ruta, "wb") as file:
                file.write(contenido_cifrado)
            print(f"[INFO] Archivo cifrado: {ruta}")
        except Exception as e:
            print(f"[ERROR] No se pudo cifrar el archivo {ruta}: {e}")

    elif os.path.isdir(ruta):
        # Cifrar todos los archivos dentro de la carpeta
        for root, _, files in os.walk(ruta):
            for file in files:
                archivo_path = os.path.join(root, file)
                try:
                    with open(archivo_path, "rb") as file:
                        contenido = file.read()
                    contenido_cifrado = fernet.encrypt(contenido)
                    with open(archivo_path, "wb") as file:
                        file.write(contenido_cifrado)
                    print(f"[INFO] Archivo cifrado: {archivo_path}")
                except Exception as e:
                    print(f"[ERROR] No se pudo cifrar el archivo {archivo_path}: {e}")

    print(f"[INFO] Cifrado completado para: {ruta}")


# ------------------- Función para descifrar archivos y carpetas ------------------- #
def descifrar_archivos_o_carpetas(ruta, nombre):
    clave = cargar_clave(nombre)
    if clave is None:
        return

    fernet = Fernet(clave)

    if os.path.isfile(ruta):
        # Descifrar un único archivo
        try:
            with open(ruta, "rb") as file:
                contenido_cifrado = file.read()
            contenido_descifrado = fernet.decrypt(contenido_cifrado)
            with open(ruta, "wb") as file:
                file.write(contenido_descifrado)
            print(f"[INFO] Archivo descifrado: {ruta}")
        except Exception as e:
            print(f"[ERROR] No se pudo descifrar el archivo {ruta}: {e}")

    elif os.path.isdir(ruta):
        # Descifrar todos los archivos dentro de la carpeta
        for root, _, files in os.walk(ruta):
            for file in files:
                archivo_path = os.path.join(root, file)
                try:
                    with open(archivo_path, "rb") as file:
                        contenido_cifrado = file.read()
                    contenido_descifrado = fernet.decrypt(contenido_cifrado)
                    with open(archivo_path, "wb") as file:
                        file.write(contenido_descifrado)
                    print(f"[INFO] Archivo descifrado: {archivo_path}")
                except Exception as e:
                    print(f"[ERROR] No se pudo descifrar el archivo {archivo_path}: {e}")

    print(f"[INFO] Descifrado completado para: {ruta}")


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
    intentos = 0  # Contador de intentos fallidos
    max_intentos = 20  # Máximo número de intentos

    print("[INFO] Buscando rostro en la cámara. Asegúrate de estar frente a la cámara...")
    while not autenticado:
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5)

        if len(rostros) == 0:
            print(f"[INFO] No se detectaron rostros. Intentos fallidos: {intentos + 1}/{max_intentos}")
            intentos += 1
            if intentos >= max_intentos:
                print("[ERROR] No se detectó ningún rostro después de varios intentos. Saliendo del programa...")
                break
        else:
            for (x, y, w, h) in rostros:
                print("[INFO] Rostro detectado. Procesando...")
                cara = gris[y:y + h, x:x + w]
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
            print("[INFO] Saliendo del programa manualmente...")
            break

    camara.release()
    cv2.destroyAllWindows()
    return nombre_usuario

# ------------------- Función auxiliar para seleccionar archivos o carpetas ------------------- #

def seleccionar_archivo_o_carpeta_con_autenticacion(accion):
    nombre = autenticar_cara()
    if not nombre:
        messagebox.showerror("Error", "Autenticación facial fallida. No se puede continuar.")
        return

    ruta = filedialog.askopenfilename(title="Selecciona un archivo") or \
           filedialog.askdirectory(title="Selecciona una carpeta")

    if ruta:
        try:
            accion(ruta, nombre)
            messagebox.showinfo("Éxito", f"Operación completada para {ruta}.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar la operación: {e}")
    else:
        messagebox.showerror("Error", "No se seleccionó ninguna ruta.")



# ------------------- Interfaz Gráfica Principal ------------------- #
def iniciar_aplicacion():
    os.makedirs("datos/caras_registradas", exist_ok=True)

    root = Tk()
    root.title("Sistema de Autenticación Facial")
    root.geometry("400x400")

    Label(root, text="Sistema de Autenticación Facial", font=("Arial", 14)).pack(pady=20)

    Label(root, text="Nombre de usuario (solo para registrar o entrenar):").pack(pady=5)
    nombre_entry = Entry(root, width=30)
    nombre_entry.pack(pady=5)

    Button(root, text="Registrar Nueva Cara",
           command=lambda: registrar_cara(nombre_entry.get()),
           width=30).pack(pady=5)

    Button(root, text="Entrenar Modelo",
           command=entrenar_modelo,
           width=30).pack(pady=5)

    Button(root, text="Proteger Archivos",
           command=lambda: seleccionar_archivo_o_carpeta_con_autenticacion(cifrar_archivos_o_carpetas),
           width=30).pack(pady=5)

    Button(root, text="Desbloquear Archivos",
           command=lambda: seleccionar_archivo_o_carpeta_con_autenticacion(descifrar_archivos_o_carpetas),
           width=30).pack(pady=5)

    Button(root, text="Salir", command=root.quit, width=30).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()