# -*- encoding: utf-8 -*-
# Pilas engine - A video game framework.
#
# Copyright 2010 - Hugo Ruscitti
# License: LGPLv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# Website - http://www.pilas-engine.com.ar

from pilas.actores import Actor
from pilas.grupo import Grupo
import pilas

DEMORA = 14

class Menu(Actor):
    """Una lista de Opciones que se pueden seleccionar
        :param opciones: Tupla con al menos dos elementos obligatorios (:texto:, :funcion:) y :argumentos: opcionales
        :param x: Posicion en el eje x
        :param y: Posicion en el eje y
    """

    def __init__(self, opciones, x=0, y=0):
        self.opciones_como_actores = []
        self.demora_al_responder = 0
        Actor.__init__(self, "invisible.png", x=x, y=y)
        self._verificar_opciones(opciones)
        self.crear_texto_de_las_opciones(opciones)
        self.opciones = opciones
        self.seleccionar_primer_opcion()
        self.opcion_actual = 0
        # contador para evitar la repeticion de teclas
        self.activar()

        # Mapeamos unas teclas para mover el menu
        teclas = {pilas.simbolos.IZQUIERDA: 'izquierda',
                              pilas.simbolos.DERECHA: 'derecha',
                              pilas.simbolos.ARRIBA: 'arriba',
                              pilas.simbolos.ABAJO: 'abajo',
                              pilas.simbolos.SELECCION: 'boton'}

        # Creamos un control personalizado
        self.control_menu = pilas.control.Control(pilas.escena_actual(), teclas)


    def activar(self):
        self.escena.mueve_mouse.conectar(self.cuando_mueve_el_mouse)
        self.escena.click_de_mouse.conectar(self.cuando_hace_click_con_el_mouse)

    def desactivar(self):
        self.escena.mueve_mouse.desconectar(self.cuando_mueve_el_mouse)
        self.escena.click_de_mouse.desconectar(self.cuando_hace_click_con_el_mouse)

    def crear_texto_de_las_opciones(self, opciones):
        "Genera un actor por cada opcion del menu."

        for indice, opcion in enumerate(opciones):
            y = self.y - indice * 50
            texto, funcion, argumentos = opcion[0],opcion[1],opcion[2:]
            opciones = pilas.actores.Opcion(texto, x=0, y=y, funcion_a_invocar=funcion, argumentos=argumentos)

            self.opciones_como_actores.append(opciones)

    def seleccionar_primer_opcion(self):
        if self.opciones_como_actores:
            self.opciones_como_actores[0].resaltar()

    def _verificar_opciones(self, opciones):
        "Se asegura de que la lista este bien definida."

        
        for x in opciones:

            if not isinstance(x, tuple) or len(x)<2:
                raise Exception("Opciones incorrectas, cada opcion tiene que ser una tupla.")

    def actualizar(self):
        "Se ejecuta de manera periodica."

        if self.demora_al_responder < 0:
            if self.control_menu.boton:
                self.control_menu.limpiar()
                self.seleccionar_opcion_actual()
                self.demora_al_responder = DEMORA

            if self.control_menu.abajo:
                self.mover_cursor(1)
                self.demora_al_responder = DEMORA
            elif self.control_menu.arriba:
                self.mover_cursor(-1)
                self.demora_al_responder = DEMORA

        self.demora_al_responder -= 1

    def seleccionar_opcion_actual(self):
        opcion = self.opciones_como_actores[self.opcion_actual]
        opcion.seleccionar()

    def mover_cursor(self, delta):
        # Deja como no-seleccionada la opcion actual.
        self._deshabilitar_opcion_actual()
        
        # Se asegura que las opciones esten entre 0 y 'cantidad de opciones'.
        self.opcion_actual += delta
        self.opcion_actual %= len(self.opciones_como_actores)

        # Selecciona la opcion nueva.
        self.opciones_como_actores[self.opcion_actual].resaltar()
    
    def __setattr__(self, atributo, valor):
        # Intenta propagar la accion a los actores del grupo.
        try:
            for x in self.opciones_como_actores:
                setattr(x, atributo, valor)
        except AttributeError:
            pass

        Actor.__setattr__(self, atributo, valor)

    def cuando_mueve_el_mouse(self, evento):
        "Permite cambiar la opcion actual moviendo el mouse. Retorna True si el mouse esta sobre alguna opcion."
        for indice, opcion in enumerate(self.opciones_como_actores):
            if opcion.colisiona_con_un_punto(evento.x, evento.y):
                if indice != self.opcion_actual:
                    self._deshabilitar_opcion_actual()
                    self.opcion_actual = indice
                    self.opciones_como_actores[indice].resaltar()
                return True
                    
    def _deshabilitar_opcion_actual(self):
        self.opciones_como_actores[self.opcion_actual].resaltar(False)

    def cuando_hace_click_con_el_mouse(self, evento):
        if self.cuando_mueve_el_mouse(evento):
            self.seleccionar_opcion_actual()
