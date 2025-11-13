nombre = []
cantidad = []
precio = []
bandera = "si"
while bandera == "si":
    n = input("Ingrese el nombre del producto: ")
    p = float(input("Ingrese el precio del producto: "))
    c = int(input("Ingrese la cantidad del producto: "))
    nombre.append(n)
    precio.append(p)
    cantidad.append(c)
    bandera = input("¿Desea ingresar otro producto? (si/no): ")

print("---------------------------------------------------")
print("=           SUPERMERCADO DE JACQUIE               =")
print("---------------------------------------------------")
print("=  Nombre  |   Cantidad   |   Precio   |   Total  =")
print("---------------------------------------------------")
for i in range(len(nombre)):
    print(f"-{nombre[i]:<10}|{cantidad[i]:<14}|{precio[i]:<12}|{cantidad[i] * precio[i]}-")