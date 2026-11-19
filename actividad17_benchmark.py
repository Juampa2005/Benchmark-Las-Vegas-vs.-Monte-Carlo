"""
Actividad 17 - Benchmark Las Vegas vs. Monte Carlo
Opcion B: factorizacion exacta por division de prueba vs. primalidad Miller-Rabin.

Ejecutar:
    pip install matplotlib pandas
    python actividad17_benchmark.py

El programa genera:
    - resultados_benchmark.csv
    - benchmark_tiempos.png
    - benchmark_error.png

Nota metodologica:
Los dos algoritmos resuelven tareas relacionadas, pero no identicas:
Las Vegas devuelve la factorizacion prima exacta; Miller-Rabin clasifica
un numero como probablemente primo o compuesto. Por ello se comparan
sobre los mismos enteros y se valida cada resultado contra una referencia
determinista (criba de Eratostenes).
"""

import math
import random
import time
import tracemalloc
from statistics import mean

import pandas as pd
import matplotlib.pyplot as plt


TAMANOS = [10**2, 10**3, 10**4, 10**5]
RONDA_K = [1, 5, 10, 20, 50]
SEMILLA = 202617
MUESTRAS_POR_TAMANO = 80
REPETICIONES_ERROR = 30


def criba_eratostenes(limite):
    """Devuelve los primos hasta limite; se usa solo para preparar/verificar datos."""
    if limite < 2:
        return []
    es_primo = [True] * (limite + 1)
    es_primo[0:2] = [False, False]
    for p in range(2, math.isqrt(limite) + 1):
        if es_primo[p]:
            for multiplo in range(p * p, limite + 1, p):
                es_primo[multiplo] = False
    return [n for n, estado in enumerate(es_primo) if estado]


def factorizar_las_vegas(n, rng=None):
    """
    Factorizacion exacta con orden aleatorio de candidatos.
    Siempre devuelve factores primos cuyo producto es n (cero error).
    El orden aleatorio cambia el trabajo realizado y, por tanto, el tiempo.
    """
    if n < 2:
        raise ValueError("n debe ser un entero mayor o igual que 2")
    if rng is None:
        rng = random.Random()

    factores = []
    candidatos = criba_eratostenes(math.isqrt(n))
    rng.shuffle(candidatos)

    residual = n
    # No se usa un corte por p*p > residual: el orden esta aleatorizado,
    # por lo que aun podria quedar un divisor primo pequeno sin probar.
    for divisor in candidatos:
        while residual % divisor == 0:
            factores.append(divisor)
            residual //= divisor

    if residual > 1:
        factores.append(residual)

    return factores


def es_primo_miller_rabin(n, k=1, rng=None):
    """
    Test probabilista Miller-Rabin.
    Para un compuesto impar, la probabilidad teorica de falso positivo
    despues de k bases independientes es como maximo (1/4)**k.
    Los numeros pares y casos pequenos se resuelven directamente.
    """
    if k < 1:
        raise ValueError("k debe ser >= 1")
    if n < 2:
        return False
    primos_pequenos = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if n in primos_pequenos:
        return True
    for p in primos_pequenos:
        if n % p == 0:
            return False
    if n % 2 == 0:
        return False

    # Escribir n - 1 = d * 2**s, con d impar.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    if rng is None:
        rng = random.Random()

    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        testigo_compuesto = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                testigo_compuesto = False
                break

        if testigo_compuesto:
            return False

    return True


def medir_tiempo_memoria(funcion, *args):
    """Mide tiempo en ms con perf_counter y pico de memoria con tracemalloc."""
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcion(*args)
    tiempo_ms = (time.perf_counter() - inicio) * 1000
    _, pico_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, tiempo_ms, pico_bytes / 1024


def construir_muestras(limite, cantidad, rng):
    """Muestra enteros del rango y garantiza presencia de primos/compuestos."""
    primos = criba_eratostenes(limite)
    if limite < 10:
        return list(range(2, limite + 1))

    candidatos = list(range(2, limite + 1))
    seleccion = rng.sample(candidatos, min(cantidad, len(candidatos)))

    # Agregar algunos casos de ambas clases para que la evaluacion no dependa
    # de una muestra accidentalmente desequilibrada.
    primos_muestra = [x for x in seleccion if x in set(primos)]
    compuestos_muestra = [x for x in seleccion if x not in set(primos)]
    if not primos_muestra:
        primos_muestra = [primos[-1]]
    if not compuestos_muestra:
        compuestos_muestra = [4]
    return primos_muestra[:cantidad // 2] + compuestos_muestra[:cantidad // 2]


def ejecutar_benchmark():
    rng = random.Random(SEMILLA)
    filas = []
    filas_error = []

    for limite in TAMANOS:
        muestras = construir_muestras(limite, MUESTRAS_POR_TAMANO, rng)
        conjunto_primos = set(criba_eratostenes(limite))

        tiempos_lv = []
        memorias_lv = []
        tiempos_mr = []
        memorias_mr = []
        errores_mr_k5 = 0

        for n in muestras:
            factores, t_lv, m_lv = medir_tiempo_memoria(
                factorizar_las_vegas, n, random.Random(rng.randrange(10**9))
            )
            # Validacion de cero error: factores primos y producto original.
            correcto_lv = math.prod(factores) == n and all(
                p in conjunto_primos for p in factores
            )
            if not correcto_lv:
                raise AssertionError(f"Factorizacion incorrecta para n={n}")
            tiempos_lv.append(t_lv)
            memorias_lv.append(m_lv)

            resultado_mr, t_mr, m_mr = medir_tiempo_memoria(
                es_primo_miller_rabin, n, 5, random.Random(rng.randrange(10**9))
            )
            referencia = n in conjunto_primos
            if resultado_mr != referencia:
                # Un error de MR es posible en teoria; se registra, no se oculta.
                errores_mr_k5 += 1
            tiempos_mr.append(t_mr)
            memorias_mr.append(m_mr)

        filas.append({
            "N_maximo": limite,
            "muestras": len(muestras),
            "Las_Vegas_tiempo_promedio_ms": mean(tiempos_lv),
            "Las_Vegas_memoria_pico_KB": max(memorias_lv),
            "Las_Vegas_error_pct": 0.0,
            "Monte_Carlo_k5_tiempo_promedio_ms": mean(tiempos_mr),
            "Monte_Carlo_k5_memoria_pico_KB": max(memorias_mr),
            "Monte_Carlo_k5_error_pct": 100 * errores_mr_k5 / len(muestras),
        })

        # Estimar tasa empírica de falso positivo para cada k.
        # Se concentra el experimento en compuestos impares: son los unicos
        # que pueden ser aceptados erroneamente como "probablemente primos".
        compuestos = [n for n in muestras if n not in conjunto_primos and n % 2 == 1]
        if not compuestos:
            compuestos = [9] if limite >= 9 else []
        for k in RONDA_K:
            errores = 0
            pruebas = 0
            for n in compuestos:
                for _ in range(REPETICIONES_ERROR):
                    pruebas += 1
                    prueba_rng = random.Random(rng.randrange(1, 2**63))
                    if es_primo_miller_rabin(n, k, prueba_rng):
                        errores += 1
            error_pct = (100 * errores / pruebas) if pruebas else 0.0
            filas_error.append({
                "N_maximo": limite,
                "k_rondas": k,
                "pruebas": pruebas,
                "falsos_positivos": errores,
                "error_empirico_pct": error_pct,
                "cota_teorica_pct": 100 * (0.25 ** k),
            })

    df = pd.DataFrame(filas)
    df_error = pd.DataFrame(filas_error)
    df_error.to_csv("resultados_error_miller_rabin.csv", index=False)
    df.to_csv("resultados_benchmark.csv", index=False)

    # Grafica 1: tiempo promedio contra tamaño maximo.
    plt.figure(figsize=(9, 5.5))
    plt.plot(df["N_maximo"], df["Las_Vegas_tiempo_promedio_ms"],
             marker="o", label="Las Vegas: factorizacion exacta")
    plt.plot(df["N_maximo"], df["Monte_Carlo_k5_tiempo_promedio_ms"],
             marker="s", label="Monte Carlo: Miller-Rabin (k=5)")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Tamaño maximo de entrada N")
    plt.ylabel("Tiempo promedio (ms, escala log)")
    plt.title("Tiempo de ejecucion vs. tamaño de entrada")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("benchmark_tiempos.png", dpi=160)
    plt.close()

    # Grafica 2: error empírico por k, una curva por tamaño.
    plt.figure(figsize=(9, 5.5))
    for limite in TAMANOS:
        parte = df_error[df_error["N_maximo"] == limite]
        plt.plot(parte["k_rondas"], parte["error_empirico_pct"],
                 marker="o", label=f"N maximo={limite}")
    plt.plot(RONDA_K, [100 * (0.25 ** k) for k in RONDA_K],
             linestyle="--", color="black", label="Cota teorica 100*(1/4)^k")
    plt.xlabel("Numero de rondas independientes k")
    plt.ylabel("Probabilidad / tasa de error (%)")
    plt.title("Amplificacion del exito en Miller-Rabin")
    plt.xticks(RONDA_K)
    plt.yscale("symlog", linthresh=0.000001)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("benchmark_error.png", dpi=160)
    plt.close()

    print("\n=== TABLA COMPARATIVA ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("\n=== ERROR EMPIRICO DE MILLER-RABIN ===")
    print(df_error.to_string(index=False, float_format=lambda x: f"{x:.8f}"))

    print("\n=== CONCLUSION ===")
    print(
        "La factorizacion por division de prueba es exacta: nunca entrega "
        "factores incorrectos, aunque su tiempo crece al aumentar el numero. "
        "Miller-Rabin responde mucho mas rapido para decidir si un numero es "
        "primo, pero su respuesta es probabilistica cuando declara que un "
        "numero es probablemente primo. Cada ronda independiente reduce "
        "la cota superior del error de un compuesto a (1/4)^k. En criptografia "
        "y sistemas que procesan numeros grandes, Miller-Rabin es conveniente "
        "para filtrar candidatos rapidamente; para una verificacion critica "
        "pueden aumentarse las rondas o combinarse con metodos deterministas. "
        "La tasa empirica puede ser 0% en una muestra finita sin significar "
        "que la probabilidad teorica sea exactamente cero."
    )

    print("\nArchivos generados:")
    print("- resultados_benchmark.csv")
    print("- resultados_error_miller_rabin.csv")
    print("- benchmark_tiempos.png")
    print("- benchmark_error.png")


if __name__ == "__main__":
    ejecutar_benchmark()
