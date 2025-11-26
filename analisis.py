import argparse
import sys
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np

#!/usr/bin/env python3
# analisis.py
# Script para analizar el CSV "comportamientos.csv" con pandas
# Uso: python analisis.py [ruta_al_csv]
# Si no se especifica ruta, busca "comportamientos.csv" en la misma carpeta.




TIPO_MAP = {
    1: "ingreso",
    2: "click",
    3: "consulta",
    4: "descarga",
    # agregar más según sea necesario
}


def try_read_csv(path: Path) -> pd.DataFrame:
    # intenta diferentes codificaciones y lectura robusta
    read_kwargs = dict(parse_dates=["fecha_hora"], infer_datetime_format=True, on_bad_lines="skip")
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=encoding, **read_kwargs)
            return df
        except Exception as e:
            # continuar con siguiente encoding
            last_exc = e
    raise last_exc


def map_tipo_movimiento(df: pd.DataFrame) -> pd.DataFrame:
    if "tipo_movimiento" in df.columns:
        # Intentar convertir a numérico si vienen como strings
        df["tipo_movimiento_raw"] = df["tipo_movimiento"]
        df["tipo_movimiento"] = pd.to_numeric(df["tipo_movimiento"], errors="coerce").astype("Int64")
        df["tipo_movimiento_label"] = df["tipo_movimiento"].map(TIPO_MAP).fillna("otro")
    return df


def basic_report(df: pd.DataFrame, path: Path):
    print("=" * 80)
    print(f"Archivo: {path}")
    print(f"Filas: {len(df):,}   Columnas: {df.shape[1]}")
    print("-" * 80)
    print("Columnas y tipos:")
    print(df.dtypes)
    print("-" * 80)
    print("Primeras 5 filas:")
    print(df.head(5).to_string(index=False))
    print("-" * 80)
    print("Valores faltantes por columna:")
    print(df.isna().sum())
    print("-" * 80)
    print("Duplicados (filas exactamente iguales):", df.duplicated().sum())
    print("=" * 80)


def frequency_report(df: pd.DataFrame):
    print("Frecuencia de tipo_movimiento (número -> etiqueta):")
    if "tipo_movimiento" in df.columns:
        freq = df["tipo_movimiento"].value_counts(dropna=False).rename_axis("tipo").reset_index(name="count")
        # mostrar etiqueta cuando exista
        def label(v):
            try:
                return TIPO_MAP.get(int(v), "otro")
            except Exception:
                return "NaN"
        freq["label"] = freq["tipo"].apply(label)
        print(freq.to_string(index=False))
    else:
        print("No se encontró la columna 'tipo_movimiento'.")
    print("-" * 80)

    if "origen" in df.columns:
        print("Top orígenes (fuentes de tráfico):")
        print(df["origen"].value_counts(dropna=False).head(10).to_string())
    else:
        print("No se encontró la columna 'origen'.")
    print("-" * 80)

    if "elementos_involucrados" in df.columns:
        print("Top elementos_involucrados:")
        print(df["elementos_involucrados"].value_counts(dropna=False).head(15).to_string())
    else:
        print("No se encontró la columna 'elementos_involucrados'.")
    print("-" * 80)


def user_and_ip_report(df: pd.DataFrame):
    if "ip_usuario" in df.columns:
        unique_ips = df["ip_usuario"].nunique(dropna=True)
        print(f"Ips únicas: {unique_ips:,}")
        print("Top 10 IPs por número de eventos:")
        print(df["ip_usuario"].value_counts().head(10).to_string())
        print("-" * 80)
    else:
        print("No se encontró la columna 'ip_usuario'.")

    if "ip_usuario" in df.columns and "tipo_movimiento_label" in df.columns:
        # Ejemplo: ver qué IPs tienen más descargas
        descargas = df[df["tipo_movimiento_label"] == "descarga"]
        if not descargas.empty:
            print("Top IPs por descargas:")
            print(descargas["ip_usuario"].value_counts().head(10).to_string())
        else:
            print("No se encontraron eventos de 'descarga'.")
    print("-" * 80)


def time_report(df: pd.DataFrame):
    if "fecha_hora" not in df.columns:
        print("No se encontró la columna 'fecha_hora'. No se puede hacer análisis temporal.")
        print("-" * 80)
        return

    # Asegurar datetime
    df = df.copy()
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce", infer_datetime_format=True)
    n_missing_dates = df["fecha_hora"].isna().sum()
    print(f"Fechas inválidas/missing: {n_missing_dates}")
    df_time = df.dropna(subset=["fecha_hora"])
    if df_time.empty:
        print("No hay fechas válidas para analizar.")
        print("-" * 80)
        return

    fecha_min = df_time["fecha_hora"].min()
    fecha_max = df_time["fecha_hora"].max()
    print(f"Rango temporal: {fecha_min}  ->  {fecha_max}")
    print("-" * 80)

    # Actividad por día
    by_day = df_time["fecha_hora"].dt.date.value_counts().sort_index()
    print("Eventos por día (últimos 15 días mostrados si hay muchos):")
    print(by_day.tail(15).to_string())
    print("-" * 80)

    # Actividad por hora del día
    by_hour = df_time["fecha_hora"].dt.hour.value_counts().sort_index()
    print("Distribución por hora del día (0-23):")
    print(by_hour.to_string())
    print("-" * 80)

    # Movimientos por día y tipo
    if "tipo_movimiento_label" in df_time.columns:
        pivot = (df_time
                 .groupby([df_time["fecha_hora"].dt.date, "tipo_movimiento_label"])
                 .size()
                 .unstack(fill_value=0))
        print("Resumen por día y tipo (filas: fecha, columnas: tipo):")
        print(pivot.tail(7).to_string())
    print("-" * 80)


def estimate_sessions(df: pd.DataFrame, gap_minutes: int = 30):
    # Estima sesiones por ip usando un umbral de inactividad (por defecto 30 min)
    if "ip_usuario" not in df.columns or "fecha_hora" not in df.columns:
        print("Falta 'ip_usuario' o 'fecha_hora' para estimar sesiones.")
        print("-" * 80)
        return

    df_s = df.dropna(subset=["ip_usuario", "fecha_hora"]).copy()
    df_s["fecha_hora"] = pd.to_datetime(df_s["fecha_hora"], errors="coerce")
    df_s = df_s.dropna(subset=["fecha_hora"])
    df_s = df_s.sort_values(["ip_usuario", "fecha_hora"])

    # calcular diff por ip
    df_s["prev_time"] = df_s.groupby("ip_usuario")["fecha_hora"].shift(1)
    df_s["diff_min"] = (df_s["fecha_hora"] - df_s["prev_time"]).dt.total_seconds() / 60.0
    # inicio de sesión cuando diff es mayor que gap o primera acción (NaN)
    df_s["new_session"] = (df_s["diff_min"].isna()) | (df_s["diff_min"] > gap_minutes)
    sessions_per_ip = df_s.groupby("ip_usuario")["new_session"].sum().sort_values(ascending=False)
    total_sessions = int(sessions_per_ip.sum())
    avg_events_per_session = len(df_s) / total_sessions if total_sessions > 0 else np.nan

    print(f"Estimación de sesiones (umbral {gap_minutes} minutos):")
    print(f"Sesiones estimadas totales: {total_sessions:,}")
    print(f"Sesiones por IP - top 10:")
    print(sessions_per_ip.head(10).to_string())
    print(f"Promedio de eventos por sesión: {avg_events_per_session:.2f}")
    print("-" * 80)


def inspect_comments(df: pd.DataFrame, n: int = 5):
    if "comenario" in df.columns:
        print(f"Ejemplos de comentarios (hasta {n}):")
        sample_comments = df["comenario"].dropna().astype(str).sample(min(n, df["comenario"].dropna().shape[0]))
        for i, c in enumerate(sample_comments, 1):
            print(f"{i}. {c[:200]}")
    else:
        print("No se encontró la columna 'comenario'.")
    print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Analizador de comportamientos CSV")
    parser.add_argument("csv_path", nargs="?", default="comportamientos.csv", help="Ruta al CSV (por defecto: comportamientos.csv)")
    parser.add_argument("--session-gap", type=int, default=30, help="Minutos para separar sesiones (por defecto 30)")
    args = parser.parse_args()

    path = Path(args.csv_path)
    if not path.exists():
        print(f"No se encontró el archivo: {path}")
        sys.exit(1)

    try:
        df = try_read_csv(path)
    except Exception as e:
        print("Error leyendo CSV:", e)
        sys.exit(1)

    # Normalizaciones rápidas
    df.columns = [c.strip() for c in df.columns]
    # nombres esperados en la descripción original
    # ip_usuario, tipo_movimiento, origen, elementos_involucrados, fecha_hora, comenario

    df = map_tipo_movimiento(df)

    basic_report(df, path)
    frequency_report(df)
    user_and_ip_report(df)
    time_report(df)
    estimate_sessions(df, gap_minutes=args.session_gap)
    inspect_comments(df, n=8)

    print("Análisis completado.")


if __name__ == "__main__":
    main()