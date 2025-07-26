
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 10:31:59 2025

@author: utp
"""
#Codigo de integración (Diagloflow)

import time
from collections import defaultdict, Counter
import os
from google.cloud import dialogflow_v2 as dialogflow
from flask import Flask, request, jsonify
from google.cloud import dialogflow_v2 as dialogflow
import tkinter as tk
from tkinter import scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk




 #Configuración del entorno
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\utp\Desktop\Mariana\sustained-tree-449212-v3-a3c3819306fc.json"
PROJECT_ID = "sustained-tree-449212-v3"

# Variables de métricas
total_conversaciones = 0
preguntas_contadas = Counter()
tiempos_respuesta = []
escalamientos = 0

def obtener_respuesta(texto_usuario, session_id="123456"):
    global total_conversaciones, preguntas_contadas, tiempos_respuesta, escalamientos

    start_time = time.time()
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)

    texto_input = dialogflow.types.TextInput(text=texto_usuario, language_code="es")
    query_input = dialogflow.types.QueryInput(text=texto_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    end_time = time.time()

    fulfillment_text = response.query_result.fulfillment_text
    intent_name = response.query_result.intent.display_name

    total_conversaciones += 1
    preguntas_contadas[intent_name] += 1
    tiempos_respuesta.append(end_time - start_time)

    if "asesor" in texto_usuario.lower() or "humano" in fulfillment_text.lower():
        escalamientos += 1

    return fulfillment_text

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Carolina - Asistente Virtual IngeLean")
        self.root.geometry("600x750")
        self.root.configure(bg="#f0f4f7")

        # Imagen decorativa (ajusta la ruta a tu imagen)
        try:
            image = Image.open(r"C:\Users\utp\Desktop\Chatbot\Carolina.png")  # Asegúrate de tener esta imagen en la misma carpeta
            image = image.resize((100, 150))
            self.bot_image = ImageTk.PhotoImage(image)
            label_img = tk.Label(root, image=self.bot_image, bg="#f0f4f7")
            label_img.pack(pady=10)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")

        # Área del chat
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, font=("Segoe UI", 11), bg="#ffffff")
        self.chat_area.pack(fill=tk.BOTH, padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)

        self.entry = tk.Entry(root, font=("Segoe UI", 12), bg="#e0e0e0")
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.send_message)

        frame = tk.Frame(root, bg="#f0f4f7")
        frame.pack()

        tk.Button(frame, text="📩 Enviar", font=("Segoe UI", 10), command=self.send_message, bg="#5dade2", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(frame, text="📊 Métricas", font=("Segoe UI", 10), command=self.mostrar_metricas, bg="#58d68d", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(frame, text="🧹 Limpiar", font=("Segoe UI", 10), command=self.limpiar_chat, bg="#f5b041", fg="white").grid(row=0, column=2, padx=5)

        # Área para gráficas
        self.metric_frame = tk.LabelFrame(root, text="📈 Métricas del Chatbot", bg="#f0f4f7", font=("Segoe UI", 10, "bold"))
        self.metric_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = None

        self.append_message("Carolina", "¡Hola! Soy Carolina, tu asistente virtual de IngeLean. ¿En qué puedo ayudarte hoy?")

    def append_message(self, sender, text):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {text}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.append_message("Tú", user_text)
        self.entry.delete(0, tk.END)

        try:
            respuesta = obtener_respuesta(user_text)
        except Exception as e:
            respuesta = f"Error al conectar con Dialogflow: {e}"

        self.append_message("Carolina", respuesta)

    def limpiar_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.append_message("Carolina", "¡Hola de nuevo! ¿Qué necesitas ahora?")

    def mostrar_metricas(self):
        global total_conversaciones, tiempos_respuesta, preguntas_contadas, escalamientos

        for widget in self.metric_frame.winfo_children():
            widget.destroy()

        fig, axs = plt.subplots(1, 3, figsize=(13, 3))
        fig.subplots_adjust(wspace=0.5)

        # Frecuencia de intenciones
        if preguntas_contadas:
            intents = list(preguntas_contadas.keys())
            counts = list(preguntas_contadas.values())
            axs[0].barh(intents, counts, color="#5dade2")
            axs[0].set_title("Intenciones Detectadas")
            axs[0].set_xlabel("Frecuencia")
        else:
            axs[0].set_title("Sin intenciones aún")

        # Tiempos de respuesta
        if tiempos_respuesta:
            axs[1].hist(tiempos_respuesta, bins=10, color="#58d68d", edgecolor="black")
            axs[1].set_title("⏱ Tiempos de Respuesta")
            axs[1].set_xlabel("Segundos")
        else:
            axs[1].set_title("Sin datos de respuesta")

        # Escalamientos
        if total_conversaciones > 0:
            sizes = [escalamientos, total_conversaciones - escalamientos]
            labels = ["Escalados", "Resueltos"]
            axs[2].pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#f1948a", "#d5f5e3"], startangle=90)
            axs[2].set_title("Escalamientos")
        else:
            axs[2].set_title("Sin conversaciones")

        self.canvas = FigureCanvasTkAgg(fig, master=self.metric_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()