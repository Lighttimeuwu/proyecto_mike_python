import random

# Generar un número aleatorio entre 1 y 10
numero_secreto = random.randint(1, 10)

print("🎯 ¡Bienvenido al juego de adivinar el número!")
print("Tienes 3 intentos para adivinar un número del 1 al 10.")

intentos = 0
max_intentos = 3

while intentos < max_intentos:
    intento = int(input("👉 Ingresa tu número: "))
    intentos += 1

    if intento == numero_secreto:
        print(f"🎉 ¡Correcto! El número secreto era {numero_secreto}.")
        break
    elif intento < numero_secreto:
        print("🔼 El número secreto es más grande.")
    else:
        print("🔽 El número secreto es más pequeño.")
    
    if intentos < max_intentos:
        print(f"Te quedan {max_intentos - intentos} intentos.\n")
    else:
        print(f"😢 ¡Se acabaron tus intentos! El número secreto era {numero_secreto}.")