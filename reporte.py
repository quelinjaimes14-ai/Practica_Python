import pandas as pd
import sweetviz as sv

# Cargar datos
df = pd.read_csv('comportamientos.csv')

# Generar reporte automático
reporte = sv.analyze(df)

# Mostrar
reporte.show_html("reporte_automatico_sweetviz.html")