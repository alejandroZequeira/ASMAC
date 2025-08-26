# 📚 Tests de Algoritmos como Objetos Activos con Axo

---

## 🎯 Objetivo

Los tests implementados en la carpeta `tests/` tienen como propósito validar que cada algoritmo de optimización, convertido a un Objeto Activo usando Axo, funciona correctamente en términos de ejecución y resultados esperados.

---

## 🧩 Estructura de los Tests

- 📄 Cada algoritmo tiene un archivo dedicado con el nombre `test_{nombre_del_algoritmo}.py`.

- ✅ En cada archivo de prueba se realizan al menos dos tipos de validaciones:

  - ▶️ **Ejecución básica:** Se invoca el método principal del algoritmo para asegurar que el objeto activo se ejecuta sin errores.

  - ✔️ **Validación de resultados:** Se comprueba que los resultados obtenidos estén dentro de rangos o condiciones esperadas, garantizando que la lógica del algoritmo se mantiene tras la conversión.

---

## 🚀 Uso

- 🧪 Los tests están escritos para ejecutarse con `pytest`.

- Para ejecutar todas las pruebas, desde la raíz del proyecto se usa:

  ```bash
  pytest tests/
  ```
- Para ejecutar las pruebas de un algoritmo específico:

  ```bash
  pytest tests/test_{nombre_del_algoritmo}.py
  ```