import turtle
import math

# Configurações iniciais
screen = turtle.Screen()
screen.setup(800, 600)
screen.title("Coração Pulsante do TikTok")
screen.bgcolor("black")

# Criar a tartaruga
heart = turtle.Turtle()
heart.speed(0)  # Velocidade máxima
heart.hideturtle()


# Função para desenhar o coração
def draw_heart(size, color):
    heart.pendown()
    heart.color(color)
    heart.begin_fill()

    # Algoritmo para desenhar coração
    for i in range(200):
        heart.right(1)
        heart.forward(size)
        heart.right(4.5)
        heart.forward(size)

    heart.end_fill()


# Função de animação de pulsação
def pulse_animation():
    # Tamanhos e cores para a animação
    sizes = [100, 120, 140, 160, 180, 200, 180, 160, 140, 120]
    colors = [
        "#FF1493",  # Rosa choque
        "#FF69B4",  # Rosa quente
        "#FF00FF",  # Magenta
        "#FF1493",  # Rosa choque novamente
    ]

    # Loop de animação
    for size in sizes:
        heart.clear()
        draw_heart(size / 10, colors[sizes.index(size) % len(colors)])
        screen.update()
        turtle.delay(50)  # Pequeno delay entre os frames


# Configurar a tela
screen.tracer(0)  # Desliga a animação automática

# Posicionar o coração no centro
heart.penup()
heart.goto(0, -50)

# Executar animação
pulse_animation()

# Manter a janela aberta
screen.mainloop()