import tensorflow as tf
import numpy as np
import os
import pyttsx3
import sys
import threading
from tkinter import *
from PIL import ImageGrab
from PIL import Image
from PIL import ImageOps

def get_image():
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_help = os.path.abspath(os.path.join(bundle_dir,'icon.ico'))
    return path_to_help

def getModels():
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_help = os.path.abspath(os.path.join(bundle_dir,'model'))
    return path_to_help

model = tf.keras.models.load_model(getModels())

def getClasses():
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_help = os.path.abspath(os.path.join(bundle_dir,'classes.txt'))
    return path_to_help

def clear():
    canvas.delete("all")
    predictionPercentages.configure(text="")
    predictionText.configure(text="...")

root = Tk()
root.title("Doodle Guesser")
root.geometry("400x350")
root.state('zoomed')
root.iconbitmap(get_image())

topics = []

class_names = open(getClasses(), "r").read().replace("_", " ").splitlines()

canvas = Canvas(root, width=400, height=350, bg="white")
canvas.pack()

def paint(event):
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    canvas.create_line(x1, y1, x2, y2, fill="black", width=10, capstyle=ROUND, smooth=TRUE, splinesteps=36)

canvas.bind("<B1-Motion>", paint)

def main(event):
    def process_image():
        global resized_image
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save("image.png")
        if Image.open("image.png").getextrema() == (0, 0):
            predictionText.configure(text="I can't see anything!")
            return
        img = Image.open("image.png")
        img = img.resize((28, 28))
        img = ImageOps.invert(img)
        img.save("image.png")
        resized_image = img
        img = ImageOps.grayscale(img)
        img = np.array(img)
        img = img.reshape(1, 28, 28, 1)
        img = img / 255.0
        pred = model.predict(img)[0]
        pred2 = pred
        ind = (-pred2).argsort()[:5]
        latex = [class_names[x] for x in ind]
        allpreds = ""
        print(latex)
        allpreds += latex[0]
        predictionText.configure(text="Predicting...")
        predictionText.configure(text="I see " + allpreds + "!")
        predictionPercentages.configure(text="Calculating percentages...")
        pyttsx3.speak("I see " + allpreds + "!")
        percentages = ""
        total_percentage = sum(pred2[ind]) * 100
        for i in range(5):
            percentage = round(pred2[ind[i]] * 100 / total_percentage * 100)
            percentages += latex[i] + ": " + str(percentage) + "%\n"
        
        predictionPercentages.configure(text= percentages)

    thread = threading.Thread(target=process_image)
    thread.start()
    

canvas.bind("<Button-1>", paint)
canvas.bind("<ButtonRelease-1>", main)

predictionText = Label(root, text="...", font=("Helvetica", 16))
predictionText.pack()

predictionPercentages = Label(root, text="", font=("Helvetica", 16))
predictionPercentages.pack()

clearButton = Button(root, text="Clear", command=clear)
clearButton.pack()

predictionText.configure(bg=root['bg'])
predictionPercentages.configure(bg=root['bg'])
clearButton.configure(bg=root['bg'])

root.mainloop()