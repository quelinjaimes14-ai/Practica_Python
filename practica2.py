#declaracion de variables
bandera = 0
numbero1 = 0
numero2 = 0  
#funciones de operaciones 
def sumar():
    print("El resultado de la suma es:", numbero1 + numero2)
def restar():
    print("El resultado de la resta es:", numbero1 - numero2)
def multiplicar():
    print("El resultado de la multiplicacion es:", numbero1 * numero2)
def dividir():
    print("El resultado de la division es:", numbero1 / numero2)
print("Bienvenido a tu calculadora favorita")
while bandera != 5:
    print("listado de opciones:")
    print("1. Suma")
    print("2. Resta") 
    print("3. Multiplicacion")
    print("4. Division")
    print("5. Salir")
    bandera = int(input("Seleciona del 1 al 5: "))
    if bandera >= 1 or bandera <= 4:
        numero1 = int(input("Ingrese el primer numero: "))
        numero2 = int(input("Ingrese el segundo numero: "))
    if (bandera == 1):
        sumar()
    elif (bandera == 2):
        restar()
    elif (bandera == 3):
        multiplicar()
    elif (bandera == 4):
        dividir()
    elif (bandera == 5):
        print("Gracias por usar la calculadora")
    else:
        print("Opcion no valida, por favor seleccione una opcion del 1 al 5")
   

#int(input se usa para castear de string a entero)
#>mayor que >
#<menor que <
#!= diferente que !=
#== igual que ==
#and tabla Y
#or tabla o