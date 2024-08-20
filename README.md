# Parser Delta
Parser para los comprobantes de rescate FFMM de Delta

## Instrucciones de uso

1) Crear una carpeta con la fecha de proceso actual, en el formato YYYYMMDD. Nos referimos a ella como **carpeta de proceso**.
2) Guardar en la carpeta de proceso los archivos de operaciones (formato pdf, estructura del nombre: **OPER_75990_{codigo_boleta}_{fecha_emisión}.pdf**).
3) Crear en la carpeta de proceso un archivo con nombre **pass.txt**, donde se deben guardar las contraseñas de los archivos de operaciones, y el cual debe seguir el siguiente formato, donde el ``codigo_boleta`` es el código presente en el nombre de cada archivo, y la ``contraseña_boleta`` es la contraseña utilizada para abrir el mismo:
    ```
    codigo_boleta:contraseña_boleta
    ```
4) Ejecutar el programa con Python: 
    ```
    python main.py
    ```
5) Tanto la tabla con los resultados como los archivos de texto en bruto se encontraran en la carpeta de proceso, la primera con el nombre **{fecha_proceso}_results.txt** y el resto con el mismo nombre que el de su archivo original.