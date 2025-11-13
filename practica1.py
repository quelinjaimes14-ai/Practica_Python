#declaracion de variables
numero_tabla = 0
#entrada de datos
print("Bienvenido al sistema que calcula cuaquier tabla de multiplicar")
numero_tabla = int(input("Ingrese el numero de la tabla que desea calcular: "))
#validacion de datos y proceso !=
if (numero_tabla < 1 or numero_tabla > 10):
    print("El numero ingresado no es valido, por favor ingrese un numero entre 1 y 10")
elif (numero_tabla == 1):
    print("Apoco no te la sabes?")
elif (numero_tabla > 7):
    print("Wow, esa si que es una tabla dificil")
else:
    print("Tabla de multiplicar del numero:", numero_tabla)
    #Imprision de la tabla de multiplicar
    for i in range(1, 11):
        print("numero_tabla x", i, "=", numero_tabla * i)
print("Gracias por usar el sistema de tablas de multiplicar")


#for se usa cuando se sabe cuantas veces se va a repetir un bloque de codigo
#while se usa cuando no se sabe cuantas veces se va a repetir un bloque de codigo