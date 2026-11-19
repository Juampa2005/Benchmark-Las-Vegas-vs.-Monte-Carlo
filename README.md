# Actividad 17. Benchmark Las Vegas vs. Monte Carlo

## Descripción

Este proyecto implementa y compara experimentalmente dos algoritmos probabilistas: **Las Vegas** y **Monte Carlo**, aplicados al problema de la factorización y primalidad de números enteros dentro del área de teoría de números y criptografía.

El objetivo es analizar las diferencias entre ambos modelos en términos de tiempo de ejecución, precisión y comportamiento probabilístico.

## Objetivos

- Implementar un algoritmo de tipo Las Vegas que garantice resultados correctos mediante búsqueda exacta de factores.
- Implementar el algoritmo Monte Carlo Miller-Rabin para comprobar la primalidad de números enteros.
- Medir los tiempos de ejecución de ambos algoritmos.
- Evaluar el comportamiento del algoritmo Monte Carlo utilizando diferentes cantidades de rondas.
- Comparar experimentalmente la precisión y el rendimiento de ambos modelos.

## Algoritmos implementados

### 1. Las Vegas – Búsqueda exacta de factores primos

Este algoritmo realiza una búsqueda exacta para encontrar factores primos de un número entero.

Sus principales características son:

- Garantiza que el resultado obtenido sea correcto.
- Su tiempo de ejecución puede variar dependiendo del número analizado.
- No sacrifica precisión a cambio de velocidad.

### 2. Monte Carlo – Miller-Rabin

Miller-Rabin es un algoritmo probabilista utilizado para determinar si un número es primo o compuesto.

Sus características principales son:

- Utiliza pruebas probabilísticas para evaluar la primalidad.
- Su precisión depende de la cantidad de rondas ejecutadas.
- Puede existir una probabilidad de error al identificar un número compuesto como probablemente primo.
- Incrementar el número de rondas reduce considerablemente la probabilidad de error.

## Parámetros del experimento

Para realizar el benchmark se utilizan los siguientes parámetros:

| Parámetro | Valores |
|---|---|
| Tamaños de entrada (N) | 100, 1,000, 10,000 y 100,000 |
| Rondas de Miller-Rabin (k) | 1, 5, 10, 20 y 50 |
| Medición de tiempo | `time.perf_counter()` |
| Unidad de tiempo | Milisegundos |
| Precisión | Porcentaje de error |
| Memoria | Consumo de memoria durante las pruebas |

## Métricas evaluadas

Se consideran las siguientes métricas:

- **Tiempo de ejecución:** tiempo necesario para completar cada algoritmo.
- **Consumo de memoria:** recursos utilizados durante la ejecución.
- **Tasa de error:** porcentaje de resultados incorrectos obtenidos.
- **Cantidad de rondas:** influencia de k en la precisión de Miller-Rabin.

## Visualización de resultados

El programa genera gráficas para facilitar la interpretación de los resultados:

1. **Tiempo de ejecución vs. tamaño de entrada (N):** permite observar cómo escala el rendimiento de ambos algoritmos.
2. **Tasa de error vs. cantidad de rondas (k):** permite analizar cómo mejora la precisión de Miller-Rabin al incrementar las rondas de prueba.

También se genera una tabla comparativa con los resultados experimentales.

## Tecnologías utilizadas

- Python 3
- Matplotlib
- NumPy
- Pandas
- `time.perf_counter()`

## Ejecución del proyecto

1. Clonar o descargar el repositorio.
2. Instalar las dependencias necesarias:

```bash
pip install numpy pandas matplotlib
```

3. Ejecutar el programa:

```bash
python actividad17_benchmark.py
```

4. Consultar los archivos generados con las mediciones, tablas y gráficas.

## Conclusiones

La comparación entre los modelos Las Vegas y Monte Carlo permite comprender el compromiso entre precisión y rendimiento en los algoritmos probabilistas.

El modelo Las Vegas garantiza resultados correctos, aunque su tiempo de ejecución puede variar. Por otro lado, Monte Carlo ofrece una ejecución basada en pruebas probabilísticas, donde el nivel de confianza puede incrementarse mediante más rondas de Miller-Rabin.

En conclusión, ambos modelos tienen aplicaciones importantes en computación y criptografía. La elección depende de las necesidades del problema, especialmente del equilibrio entre tiempo de ejecución y certeza del resultado.

---

**Actividad:** 17 – Benchmark Las Vegas vs. Monte Carlo  
**Área:** Teoría de números y criptografía  
**Modelo seleccionado:** Opción B
