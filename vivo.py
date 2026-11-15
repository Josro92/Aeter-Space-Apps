"""Fragmentos que se refrescan solos, pero que se pausan mientras Aéter está respondiendo.

Un fragmento con run_every pide una nueva ejecución cada pocos segundos; si eso ocurre mientras
la respuesta del chat se está escribiendo, la ejecución se corta a la mitad (el mensaje no aparece
y el protocolo nunca se activa). Por eso, durante la respuesta se registran sin temporizador.
"""
from __future__ import annotations

import functools
import time

import streamlit as st

MAX_OCUPADO_SEG = 90  # por si una respuesta se corta: pasado este tiempo todo vuelve a la normalidad


def marcar_ocupado() -> None:
    st.session_state["ocupado_ts"] = time.time()


def liberar() -> None:
    st.session_state.pop("ocupado_ts", None)


def ocupado() -> bool:
    return time.time() - st.session_state.get("ocupado_ts", 0) < MAX_OCUPADO_SEG


def fragmento(cada_seg: float):
    def decorador(fn):
        @functools.wraps(fn)
        def envoltura(*args, **kwargs):
            return st.fragment(run_every=None if ocupado() else cada_seg)(fn)(*args, **kwargs)
        return envoltura
    return decorador
