lista_frutas = []
bandera = "si"
while bandera == "si":
    n = input("Ingrese el nombre del producto: ")
    p = float(input("Ingrese el precio del producto: "))
    c = int(input("Ingrese la cantidad del producto: "))
    fruta ={
        "nombre": n,
        "precio": p,
        "cantidad": c
    }
    lista_frutas.append(fruta)
    bandera = input("¿Desea ingresar otro producto? (si/no): ")

print("---------------------------------------------------")
print("=           SUPERMERCADO DE JACQUIE               =")
print("---------------------------------------------------")
print("=  Nombre  |   Cantidad   |   Precio   |   Total  =")
print("---------------------------------------------------")
for fruta in lista_frutas:
    print(f"-{fruta['nombre']:<10}|{fruta['cantidad']:<14}|{fruta['precio']:<12}|{ fruta['cantidad'] * fruta['precio']:<10}-")