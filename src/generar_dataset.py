# -*- coding: utf-8 -*-
"""
generar_dataset.py
==================
Genera el dataset de evaluacion de analisis de sentimiento en espanol
utilizado en el proyecto. El conjunto es un corpus curado manualmente por
los autores con fines academicos, balanceado en tres clases:

    POS  -> sentimiento positivo
    NEU  -> sentimiento neutral
    NEG  -> sentimiento negativo

Cada texto es una opinion / resena corta en espanol, similar en estilo a los
comentarios de productos, servicios y redes sociales. El corpus es original
(no se copia de ningun dataset con licencia restrictiva), por lo que puede
redistribuirse libremente junto con el proyecto.

Uso:
    python src/generar_dataset.py --salida data/dataset_sentimiento_es.csv

Reproducibilidad:
    El contenido esta definido de forma deterministica en este script. Ejecutar
    el script siempre produce el mismo CSV (mismo orden, mismos ids).
"""

import argparse
import csv
import os

# ---------------------------------------------------------------------------
# Definicion del corpus: (texto, etiqueta, dominio)
# 40 ejemplos por clase -> 120 ejemplos en total, balanceado.
# ---------------------------------------------------------------------------

POSITIVOS = [
    ("Me encanto este telefono! La bateria dura todo el dia y la camara es excelente.", "electronica"),
    ("El restaurante supero mis expectativas, la comida estaba deliciosa y el servicio fue impecable.", "restaurante"),
    ("Excelente compra, el producto llego antes de lo esperado y en perfecto estado.", "compras"),
    ("La aplicacion es muy intuitiva y me ha ahorrado muchisimo tiempo en el trabajo.", "software"),
    ("Que gran experiencia, el hotel era hermoso y el personal super amable.", "viajes"),
    ("Recomiendo totalmente este libro, no pude dejar de leerlo hasta el final.", "entretenimiento"),
    ("La nueva actualizacion mejoro el rendimiento; ahora todo funciona rapidisimo.", "software"),
    ("Estoy feliz con mi compra, la calidad de la tela es increible y muy comoda.", "ropa"),
    ("El soporte tecnico resolvio mi problema en minutos, quede muy satisfecho.", "servicio"),
    ("Una pelicula maravillosa, me emociono de principio a fin.", "entretenimiento"),
    ("La laptop es ligera, potente y la pantalla se ve espectacular.", "electronica"),
    ("El viaje fue perfecto, todo estuvo bien organizado y sin contratiempos.", "viajes"),
    ("Los audifonos tienen un sonido brutal y la cancelacion de ruido funciona de maravilla.", "electronica"),
    ("Mil gracias al repartidor, super rapido y muy atento.", "servicio"),
    ("Este curso me cambio la forma de programar, lo volveria a tomar sin dudarlo.", "educacion"),
    ("El cafe estaba delicioso y el ambiente del local es acogedor.", "restaurante"),
    ("La verdad, el mejor servicio al cliente que he recibido en anos.", "servicio"),
    ("Me sorprendio lo bien que funciona, vale cada peso que pague.", "compras"),
    ("La camara captura fotos nitidas incluso de noche, estoy encantada.", "electronica"),
    ("Excelente relacion calidad-precio, lo recomiendo a ojos cerrados.", "compras"),
    ("El sofa es comodisimo y se ve elegante en la sala.", "hogar"),
    ("La pizza llego caliente y riquisima, repetire sin duda.", "restaurante"),
    ("Gran atencion del personal, me senti muy bien atendido todo el tiempo.", "servicio"),
    ("La app de banca por fin es facil de usar, felicidades al equipo!", "software"),
    ("Increible concierto, la banda sono espectacular y la energia fue contagiosa.", "entretenimiento"),
    ("El medicamento me alivio rapido, muy contento con los resultados.", "salud"),
    ("La bicicleta es resistente y muy comoda para los trayectos largos.", "transporte"),
    ("Servicio puntual y chofer muy amable, llegue tranquilo a mi destino.", "transporte"),
    ("Las zapatillas son comodisimas, perfectas para correr largas distancias.", "ropa"),
    ("El tutorial fue clarisimo, aprendi a usar la herramienta en una tarde.", "educacion"),
    ("Que buen detalle, incluyeron una nota y un regalo con el pedido.", "compras"),
    ("La serie esta espectacular, cada capitulo te deja con ganas de mas.", "entretenimiento"),
    ("El hotel tenia una vista preciosa y desayuno buenisimo incluido.", "viajes"),
    ("Funciona perfecto con mi consola, la instalacion fue rapidisima.", "electronica"),
    ("La maestra explica muy bien, mi hijo mejoro muchisimo en matematicas.", "educacion"),
    ("Compre la aspiradora y limpia increible, supero mis expectativas.", "hogar"),
    ("El equipo de soporte fue paciente y resolvio todas mis dudas.", "servicio"),
    ("Comida fresca, porciones generosas y precios justos, volvere pronto.", "restaurante"),
    ("La actualizacion trajo funciones nuevas geniales, me encanta la app ahora.", "software"),
    ("Excelente calidad de imagen en la tele, los colores son vivos y reales.", "electronica"),
]

NEUTRALES = [
    ("El paquete llego en la fecha estimada y venia en su caja original.", "compras"),
    ("El telefono cumple con lo basico, ni me sorprende ni me decepciona.", "electronica"),
    ("La reunion se reprogramo para el proximo martes a las diez.", "servicio"),
    ("El producto es de color azul y mide veinte centimetros de largo.", "compras"),
    ("La aplicacion se actualizo automaticamente durante la noche.", "software"),
    ("El restaurante abre de lunes a sabado de nueve a seis.", "restaurante"),
    ("Recibi el correo con la confirmacion de mi pedido esta manana.", "compras"),
    ("El hotel esta ubicado a dos cuadras de la estacion de metro.", "viajes"),
    ("La bateria dura lo que indica el fabricante, nada fuera de lo comun.", "electronica"),
    ("El libro tiene trescientas paginas y esta dividido en diez capitulos.", "entretenimiento"),
    ("El tecnico vendra a revisar el equipo entre las dos y las cuatro.", "servicio"),
    ("La camiseta es talla mediana y de algodon, como aparece en la foto.", "ropa"),
    ("El curso consta de cinco modulos y un examen final.", "educacion"),
    ("El pedido incluye dos articulos y un instructivo de uso.", "compras"),
    ("La pelicula dura aproximadamente dos horas con creditos incluidos.", "entretenimiento"),
    ("El pago se proceso con tarjeta y recibi el comprobante.", "servicio"),
    ("El producto requiere dos pilas AA que no vienen incluidas.", "electronica"),
    ("La tienda cambio su horario por la temporada de fin de ano.", "compras"),
    ("El envio se realiza mediante paqueteria estandar en cinco dias habiles.", "compras"),
    ("La app esta disponible para Android y iOS por igual.", "software"),
    ("El modelo nuevo es similar al anterior, con cambios menores.", "electronica"),
    ("El vuelo hace una escala de una hora en la ciudad de Panama.", "viajes"),
    ("Me entregaron la factura impresa junto con el producto.", "servicio"),
    ("El monitor tiene dos puertos HDMI y uno de tipo USB-C.", "electronica"),
    ("El plato lleva arroz, pollo y verduras al vapor.", "restaurante"),
    ("La contrasena debe tener al menos ocho caracteres.", "software"),
    ("El evento se llevara a cabo en el salon principal del segundo piso.", "servicio"),
    ("Cambiaron el empaque, pero el contenido es el mismo de siempre.", "compras"),
    ("El servicio incluye instalacion, pero no la configuracion avanzada.", "servicio"),
    ("La garantia cubre doce meses a partir de la fecha de compra.", "compras"),
    ("El autobus pasa cada quince minutos por esta parada.", "transporte"),
    ("El documento esta en formato PDF y pesa dos megabytes.", "software"),
    ("La habitacion tiene una cama matrimonial y un escritorio.", "viajes"),
    ("El supermercado reabastece sus estantes los dias miercoles.", "compras"),
    ("La actualizacion ocupa quinientos megabytes de espacio.", "software"),
    ("El producto se fabrica en Mexico y se distribuye en la region.", "compras"),
    ("La cita medica quedo agendada para el jueves por la tarde.", "salud"),
    ("El cargador es compatible con varios modelos de la marca.", "electronica"),
    ("El informe resume las ventas del primer trimestre del ano.", "servicio"),
    ("El paquete contiene el manual en espanol y en ingles.", "compras"),
]

NEGATIVOS = [
    ("Pesima experiencia, el producto llego roto y nadie responde mis mensajes.", "compras"),
    ("La comida estaba fria y el servicio fue lentisimo, no vuelvo.", "restaurante"),
    ("La bateria se descarga en un par de horas, una verdadera decepcion.", "electronica"),
    ("La aplicacion se cierra sola constantemente, es imposible usarla.", "software"),
    ("El hotel estaba sucio y el personal fue grosero, no lo recomiendo.", "viajes"),
    ("Me cobraron de mas y todavia no me devuelven el dinero.", "servicio"),
    ("El libro es aburridisimo, no pude pasar del primer capitulo.", "entretenimiento"),
    ("La actualizacion arruino el telefono, ahora va lentisimo.", "software"),
    ("Pesima calidad, la tela se rompio a la primera lavada.", "ropa"),
    ("Llevo una semana esperando el reembolso y nadie me da respuesta.", "servicio"),
    ("La pelicula es un desastre, perdi dos horas de mi vida.", "entretenimiento"),
    ("La laptop se sobrecalienta y se apaga sola, que frustracion.", "electronica"),
    ("El paquete nunca llego y la paqueteria no da explicaciones.", "compras"),
    ("Los audifonos dejaron de funcionar a la semana, dinero tirado.", "electronica"),
    ("El repartidor fue muy grosero y dejo el pedido tirado en la puerta.", "servicio"),
    ("Este curso es una estafa, el contenido esta desactualizado.", "educacion"),
    ("El cafe sabia a quemado y lo cobraron carisimo.", "restaurante"),
    ("El peor servicio al cliente, me dejaron en espera una hora.", "servicio"),
    ("No funciona como prometen, me siento totalmente enganado.", "compras"),
    ("La camara toma fotos borrosas, una pesima compra.", "electronica"),
    ("Carisimo para lo poco que ofrece, no lo vale en absoluto.", "compras"),
    ("El sofa llego con manchas y huele horrible, lo quiero devolver.", "hogar"),
    ("La pizza llego fria y con ingredientes que no pedi.", "restaurante"),
    ("Nadie en el local nos atendio, terminamos yendonos molestos.", "restaurante"),
    ("La app del banco falla justo cuando necesitas pagar, indignante.", "software"),
    ("El concierto fue una decepcion, el sonido era pesimo.", "entretenimiento"),
    ("El medicamento no sirvio de nada y encima me cayo mal.", "salud"),
    ("La bicicleta se descompuso a la semana, mala calidad.", "transporte"),
    ("El chofer manejo imprudente y llego tardisimo, terrible.", "transporte"),
    ("Las zapatillas se despegaron al mes, que perdida de dinero.", "ropa"),
    ("El tutorial es confuso y esta lleno de errores, no sirve.", "educacion"),
    ("Faltaban piezas en el pedido y nadie soluciona el problema.", "compras"),
    ("La serie es predecible y mal actuada, no la recomiendo.", "entretenimiento"),
    ("La habitacion del hotel tenia cucarachas, una asquerosidad.", "viajes"),
    ("El producto es incompatible con mi equipo, perdi mi dinero.", "electronica"),
    ("La maestra nunca responde dudas y las clases son un caos.", "educacion"),
    ("La aspiradora hace un ruido insoportable y no aspira bien.", "hogar"),
    ("Soporte tecnico inutil, llevo dias sin que resuelvan nada.", "servicio"),
    ("Comida en mal estado, termine con dolor de estomago.", "restaurante"),
    ("La nueva version elimino funciones utiles, un retroceso total.", "software"),
]


def construir_filas():
    """Devuelve la lista de filas (dict) del dataset en orden deterministico."""
    filas = []
    bloques = [("POS", POSITIVOS), ("NEU", NEUTRALES), ("NEG", NEGATIVOS)]
    idx = 1
    for etiqueta, ejemplos in bloques:
        for texto, dominio in ejemplos:
            filas.append({
                "id": f"es-{idx:03d}",
                "texto": texto,
                "etiqueta": etiqueta,
                "dominio": dominio,
                "longitud_caracteres": len(texto),
                "num_palabras": len(texto.split()),
            })
            idx += 1
    return filas


def main():
    parser = argparse.ArgumentParser(description="Genera el dataset de sentimiento en espanol (CSV).")
    parser.add_argument(
        "--salida",
        default="data/dataset_sentimiento_es.csv",
        help="Ruta de salida del archivo CSV.",
    )
    args = parser.parse_args()

    filas = construir_filas()
    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)

    campos = ["id", "texto", "etiqueta", "dominio", "longitud_caracteres", "num_palabras"]
    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)

    # Resumen por consola (util para validar reproducibilidad)
    total = len(filas)
    conteo = {}
    for fila in filas:
        conteo[fila["etiqueta"]] = conteo.get(fila["etiqueta"], 0) + 1
    print(f"Dataset generado en: {args.salida}")
    print(f"Total de ejemplos: {total}")
    for etiqueta in ("POS", "NEU", "NEG"):
        print(f"  {etiqueta}: {conteo.get(etiqueta, 0)}")
    longitudes = [fila["longitud_caracteres"] for fila in filas]
    print(f"Longitud (caracteres): min={min(longitudes)} max={max(longitudes)} "
          f"promedio={sum(longitudes) / total:.1f}")


if __name__ == "__main__":
    main()
