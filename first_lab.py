from tkinter import *
from math import *

# главное окно
window = Tk()
size = 600
canvas = Canvas(window, width=size, height=size)  # Установка размеров
canvas.pack()

radius = 200
center = 300, 300

# рисуем окружность
canvas.create_oval(center[0] - radius, center[1] - radius,
                   center[0] + radius, center[1] + radius)

angle = 0
speed = 10
direction = 1  # по часовой против 0

def move():
    global angle
    r_angle = radians(angle)  # угол в радианы
    # вычисление координат точки на окружности
    point_x = center[0] + radius * cos(r_angle)
    point_y = center[1] + radius * sin(r_angle)
    canvas.delete("point")  # удаляем предыдущую точку
    # рисуем точку
    canvas.create_oval(point_x - 5, point_y - 5, point_x + 5, point_y + 5, fill="pink", tag="point")
    angle += direction * speed  # увеличиваем угол для создания движения точки
    if angle >= 360:  # убеждаемся, что угол остается в пределах 0-360
        angle -= 360
    window.after(60, move)

# запускаем анимацию
move()
window.mainloop()