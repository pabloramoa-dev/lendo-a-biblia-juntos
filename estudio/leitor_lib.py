"""leitor_lib — o Leitor do canal "Lendo a Bíblia Explicada" e o cenário do lago.

Mesma filosofia do previsao_lib: tudo desenhado por código, traço grosso,
cabeça grande, personagem SEMPRE idêntico entre os vídeos.

Personagem: O LEITOR — cabelo castanho comprido repartido ao meio, barba,
túnica clara com faixa vinho no ombro. Ele só lê o texto bíblico.

A ordem dos 15 primeiros objetos do grupo é a mesma do ranzinza(), porque o
motor do personagem vivo (sabio_vivo.py) separa corpo e cabeça por posição.
"""
from __future__ import annotations

import math

from manim import *
import numpy as np

PT = "#2b2118"
PELE = "#e6b892"
CAB = "#6b4426"        # cabelo
CAB_ESC = "#4a2e19"    # sobrancelha e bigode
BARBA = "#7d5232"
TUN = "#f7f3ea"        # camisa
TUN_SOMBRA = "#d9cdb4"
FAIXA = "#9c2f2f"


def _contorno(c, pontos, escala=1.0, dy=0.0):
    """Curva fechada e suave passando pelos pontos (x, y) em volta de c."""
    pts = [c + np.array([x * escala, y * escala + dy, 0]) for x, y in pontos]
    return VMobject().set_points_smoothly(pts + [pts[0]])


# formato do rosto: testa mais larga, maçãs, mandíbula afinando até o queixo
_ROSTO_D = [(0, .98), (.42, .93), (.72, .66), (.80, .22), (.76, -.22), (.62, -.60), (.36, -.88), (0, -.99)]
ROSTO = _ROSTO_D + [(-x, y) for x, y in reversed(_ROSTO_D[1:-1])]


def leitor():
    """Devolve dict com grupo, cab, oe, od, boca, sobE, sobD, maoE, maoD."""
    c = UP * 1.4
    cab = _contorno(c, ROSTO).set_fill(PELE, 1).set_stroke(PT, 13)

    # --- corpo (mesmas 15 posições do ranzinza) ---
    pesc = Line(c + DOWN * 0.9, c + DOWN * 1.12, stroke_color=PT, stroke_width=1, stroke_opacity=0)
    t = pesc.get_end()

    tunica = Polygon(t + LEFT * 0.26 + UP * 0.04, t + RIGHT * 0.26 + UP * 0.04,
                     t + RIGHT * 0.84 + DOWN * 0.2, t + RIGHT * 1.0 + DOWN * 0.62,
                     t + RIGHT * 1.0 + DOWN * 1.9, t + LEFT * 1.0 + DOWN * 1.9,
                     t + LEFT * 1.0 + DOWN * 0.62, t + LEFT * 0.84 + DOWN * 0.2,
                     fill_color=TUN, fill_opacity=1, stroke_color=PT, stroke_width=10).round_corners(0.14)
    barra = Polygon(t + DOWN * 1.9 + LEFT * 1.0, t + DOWN * 1.9 + RIGHT * 1.0,
                    t + DOWN * 2.6 + RIGHT * 1.0, t + DOWN * 2.6 + LEFT * 1.0,
                    fill_color="#5b6b7a", fill_opacity=1, stroke_color=PT, stroke_width=8)
    pe = Line(t + DOWN * 2.55 + LEFT * 0.34, t + DOWN * 2.9 + LEFT * 0.4, stroke_color=PT, stroke_width=14)
    pd = Line(t + DOWN * 2.55 + RIGHT * 0.34, t + DOWN * 2.9 + RIGHT * 0.4, stroke_color=PT, stroke_width=14)
    chE = Ellipse(width=0.46, height=0.2, fill_color="#8a5a33", fill_opacity=1,
                  stroke_color=PT, stroke_width=5).move_to(pe.get_end() + DOWN * 0.04 + LEFT * 0.08)
    chD = Ellipse(width=0.46, height=0.2, fill_color="#8a5a33", fill_opacity=1,
                  stroke_color=PT, stroke_width=5).move_to(pd.get_end() + DOWN * 0.04 + RIGHT * 0.08)

    # pescoço de verdade (pele), terminando no decote em V
    pescoco = Polygon(t + LEFT * 0.21 + UP * 0.5, t + RIGHT * 0.21 + UP * 0.5,
                      t + RIGHT * 0.25 + UP * 0.02, t + DOWN * 0.34, t + LEFT * 0.25 + UP * 0.02,
                      fill_color=PELE, fill_opacity=1, stroke_color=PT, stroke_width=8)
    sombra_pesc = Polygon(t + LEFT * 0.2 + UP * 0.3, t + RIGHT * 0.2 + UP * 0.3, t + RIGHT * 0.2 + UP * 0.14,
                          t + LEFT * 0.2 + UP * 0.14, fill_color="#c99873", fill_opacity=.55, stroke_width=0)
    gola_pele = VGroup(pescoco, sombra_pesc)
    dobras = VGroup(
        Line(t + DOWN * 0.36, t + DOWN * 1.9, stroke_color=TUN_SOMBRA, stroke_width=6),
        *[Dot(t + DOWN * (0.62 + k * 0.34) + RIGHT * 0.07, radius=0.035, color=PT) for k in range(4)])
    abas = VGroup(
        Polygon(t + LEFT * 0.30 + UP * 0.06, t + LEFT * 0.02 + DOWN * 0.36, t + LEFT * 0.44 + DOWN * 0.40,
                fill_color=TUN, fill_opacity=1, stroke_color=PT, stroke_width=7),
        Polygon(t + RIGHT * 0.30 + UP * 0.06, t + RIGHT * 0.02 + DOWN * 0.36, t + RIGHT * 0.44 + DOWN * 0.40,
                fill_color=TUN, fill_opacity=1, stroke_color=PT, stroke_width=7))

    omb = t + DOWN * 0.3
    be = Line(omb + LEFT * 0.8, omb + DOWN * 0.9 + LEFT * 0.9, stroke_color=PT, stroke_width=15)
    bd = Line(omb + RIGHT * 0.8, omb + DOWN * 0.72 + RIGHT * 0.95, stroke_color=PT, stroke_width=15)
    cajado = VGroup()
    maoE = Dot(be.get_end(), radius=0.13, color=PELE).set_stroke(PT, 5)
    maoD = Dot(bd.get_end(), radius=0.13, color=PELE).set_stroke(PT, 5)

    # --- cabeça ---
    orelhas = VGroup(*[
        VGroup(Ellipse(width=0.26, height=0.42, fill_color=PELE, fill_opacity=1, stroke_color=PT, stroke_width=8),
               Arc(radius=0.07, start_angle=PI / 2, angle=lado * PI).set_stroke("#c99873", 5))
        .move_to(c + RIGHT * lado * 0.84 + DOWN * 0.06) for lado in (-1, 1)])
    bochechas = VGroup(*[
        Ellipse(width=0.34, height=0.2, fill_color="#e79a86", fill_opacity=0.45,
                stroke_width=0).move_to(c + RIGHT * (lado * 0.5) + DOWN * 0.26)
        for lado in (-1, 1)])
    # cabelo curto acompanhando o formato da cabeça, com costeletas
    cabelo = Difference(
        _contorno(c, ROSTO, 1.07, 0.07),
        Ellipse(width=1.74, height=2.3).move_to(c + DOWN * 0.47),
    ).set_fill(CAB, 1).set_stroke(PT, 9)
    topete = Union(
        Ellipse(width=1.36, height=0.72).rotate(0.2).move_to(c + UP * 0.98 + RIGHT * 0.04),
        Ellipse(width=0.7, height=0.46).rotate(0.5).move_to(c + UP * 1.2 + RIGHT * 0.48),
    ).set_fill(CAB, 1).set_stroke(PT, 9)
    fios = VGroup(
        ArcBetweenPoints(c + UP * 0.82 + LEFT * 0.42, c + UP * 1.26 + RIGHT * 0.5, angle=-0.7).set_stroke(CAB_ESC, 5),
        ArcBetweenPoints(c + UP * 0.76 + LEFT * 0.12, c + UP * 1.14 + RIGHT * 0.6, angle=-0.6).set_stroke(CAB_ESC, 5))
    # nariz em traço, de perfil suave, no lugar da bolinha
    nariz = VMobject().set_points_smoothly([c + np.array([-.03, -.02, 0]), c + np.array([.09, -.25, 0]),
                                            c + np.array([-.05, -.31, 0])]).set_stroke(PT, 7)
    queixo = ArcBetweenPoints(c + DOWN * 0.84 + LEFT * 0.12, c + DOWN * 0.84 + RIGHT * 0.12, angle=PI / 3
                              ).set_stroke("#c99873", 5)

    # partes que o motor redesenha a cada quadro (olhos, sobrancelhas, boca)
    sobE = ArcBetweenPoints(c + LEFT * 0.54 + UP * 0.30, c + LEFT * 0.14 + UP * 0.40,
                            angle=-PI / 3.2).set_stroke(CAB_ESC, 13)
    sobD = ArcBetweenPoints(c + RIGHT * 0.14 + UP * 0.40, c + RIGHT * 0.54 + UP * 0.30,
                            angle=-PI / 3.2).set_stroke(CAB_ESC, 13)
    oe = Dot(c + LEFT * 0.32 + UP * 0.04, radius=0.10, color=PT)
    od = Dot(c + RIGHT * 0.32 + UP * 0.04, radius=0.10, color=PT)
    boca = ArcBetweenPoints(c + DOWN * 0.62 + LEFT * 0.27, c + DOWN * 0.62 + RIGHT * 0.27,
                            angle=PI / 2.7).set_stroke(PT, 9)

    grupo = VGroup(pesc, barra, pe, pd, chE, chD, tunica, gola_pele, dobras, abas,
                   be, bd, cajado, maoE, maoD,
                   orelhas, cab, bochechas, cabelo, topete, fios, nariz, queixo,
                   sobE, sobD, oe, od, boca)
    return dict(grupo=grupo, cab=cab, oe=oe, od=od, boca=boca, bigode=VGroup(),
                maoE=maoE, maoD=maoD, sobE=sobE, sobD=sobD)


# =====================================================================
#  CENÁRIO DA MANHÃ: beira do lago ao nascer do sol
# =====================================================================
def _suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _gradiente(w, h, cores, centro):
    r = Rectangle(width=w, height=h, stroke_width=0).move_to(centro)
    r.set_fill(color=cores, opacity=1)
    r.set_sheen_direction(UP)
    return r


def _nuvem(escala=1.0, cor="#fffaf0"):
    partes = [(0, 0, .42), (.42, .08, .34), (-.42, .02, .32), (.18, .3, .3), (-.2, .26, .28)]
    n = VGroup(*[Circle(radius=r, fill_color=cor, fill_opacity=.95, stroke_width=0).move_to([x, y, 0])
                 for x, y, r in partes])
    base = RoundedRectangle(width=1.5, height=.38, corner_radius=.19, fill_color=cor,
                            fill_opacity=.95, stroke_width=0).move_to([0, -.16, 0])
    return VGroup(n, base).scale(escala)


def cenario_lago(scene, dur, chao_y):
    """Fundo: céu, sol nascendo, morros, lago com barco. Devolve o relógio T."""
    W, H = config.frame_width, config.frame_height
    t0 = {'t': 0.0}

    def relogio(m, dt):
        t0['t'] += dt
    clock = Dot(fill_opacity=0, stroke_width=0)
    clock.add_updater(relogio)
    scene.add(clock)
    T = lambda: t0['t']  # noqa: E731

    horizonte = -1.25
    ceu = _gradiente(W * 1.3, H * .75, ["#ffd9a6", "#ffc9a8", "#b5d9e6", "#86c0dc"], [0, horizonte + H * .375 - .4, 0])
    sol_c = np.array([2.95, horizonte + 1.75, 0])
    halos = VGroup(*[Circle(radius=r, fill_color="#fff1c2", fill_opacity=o, stroke_width=0).move_to(sol_c)
                     for r, o in ((2.3, .14), (1.6, .22), (1.1, .36))])
    sol = Circle(radius=.78, fill_color="#ffe08a", fill_opacity=1, stroke_color="#f6b94a",
                 stroke_width=6).move_to(sol_c)

    nuvens = []
    grupo_nuvens = VGroup()
    for y, esc, vel, x0 in ((5.6, 1.25, .10, -2.2), (4.3, .9, .16, 2.4), (6.3, .8, .07, .6), (3.4, .7, .12, -3.0)):
        n = _nuvem(esc).move_to([x0, y, 0])
        nuvens.append((n, vel, x0, y))
        grupo_nuvens.add(n)

    passaros = VGroup(*[VMobject() for _ in range(3)])

    serra = Polygon([-5.2, horizonte - .2, 0], [-3.6, horizonte + 1.0, 0], [-2.2, horizonte + .45, 0],
                    [-.8, horizonte + 1.25, 0], [.9, horizonte + .5, 0], [2.6, horizonte + .95, 0],
                    [5.2, horizonte + .1, 0], [5.2, horizonte - .4, 0],
                    fill_color="#b7cdbd", fill_opacity=1, stroke_width=0)
    morro1 = Ellipse(width=7.0, height=1.7, fill_color="#9cc59a", fill_opacity=1, stroke_width=0
                     ).move_to([-2.2, horizonte - .15, 0])
    morro2 = Ellipse(width=6.4, height=1.4, fill_color="#7fb184", fill_opacity=1, stroke_width=0
                     ).move_to([2.6, horizonte - .25, 0])
    arvores = VGroup(*[VGroup(Rectangle(width=.06, height=.3, fill_color="#6b4a2f", fill_opacity=1, stroke_width=0),
                              Circle(radius=.2, fill_color="#5e9a6a", fill_opacity=1, stroke_width=0).shift(UP * .26))
                       .move_to([x, horizonte + .58 + .08 * math.sin(x * 3), 0]) for x in (-3.3, -2.8, -1.2, 3.1, 3.55)])

    lago = _gradiente(W * 1.3, 3.6, ["#4f9cc6", "#8fcbe2"], [0, horizonte - 2.0, 0])
    margem = Line([-W, horizonte - .22, 0], [W, horizonte - .22, 0], stroke_color="#e9f6fb", stroke_width=5,
                  stroke_opacity=.7)
    reflexo = VGroup(*[Line(LEFT * (.55 - k * .04), RIGHT * (.55 - k * .04), stroke_color="#ffe9a8",
                            stroke_width=9).move_to([sol_c[0], horizonte - .5 - k * .27, 0]) for k in range(7)])
    ondas = VGroup(*[ArcBetweenPoints(LEFT * .28, RIGHT * .28, angle=-PI / 3).set_stroke("#e9f6fb", 5)
                     for _ in range(9)])
    onda_pos = [(-3.2, -.6), (-1.9, -1.2), (-.4, -.75), (1.1, -1.45), (3.2, -.9), (-2.7, -1.8), (.3, -1.95),
                (2.3, -2.2), (-1.0, -2.3)]

    casco = Polygon([-.62, 0, 0], [.62, 0, 0], [.42, -.26, 0], [-.42, -.26, 0], fill_color="#8a5a33",
                    fill_opacity=1, stroke_color=PT, stroke_width=5)
    mastro = Line([0, 0, 0], [0, .95, 0], stroke_color=PT, stroke_width=5)
    vela = Polygon([.04, .12, 0], [.04, .92, 0], [.55, .16, 0], fill_color="#fff8e6", fill_opacity=1,
                   stroke_color=PT, stroke_width=4)
    barco_ref = VGroup(casco, mastro, vela).scale(.8)
    barco = barco_ref.copy()

    def _vida(m, dt):
        t = T()
        sobe = .45 * _suave(t / max(dur, 1))
        for i, h in enumerate(halos):
            h.move_to(sol_c + UP * sobe)
            h.set_fill(opacity=[.14, .22, .36][i] * (.85 + .25 * math.sin(t * 1.3 + i)))
        sol.move_to(sol_c + UP * sobe)
        for n, vel, x0, y in nuvens:
            x = ((x0 + vel * t + 5.2) % 10.4) - 5.2
            n.move_to([x, y + .04 * math.sin(t * .7 + x0), 0])
        for k, b in enumerate(passaros):
            f = ((t + k * .8) % 10.0) / 10.0
            x = -4.4 + 8.8 * f
            y = 2.9 + k * .4 + .3 * math.sin(f * PI * 2)
            bat = math.sin(t * 11 + k)
            b.become(VGroup(
                ArcBetweenPoints(LEFT * .2, ORIGIN, angle=-PI / 2.4 * bat).set_stroke("#3a3442", 5),
                ArcBetweenPoints(ORIGIN, RIGHT * .2, angle=-PI / 2.4 * bat).set_stroke("#3a3442", 5),
            ).scale(1 - k * .15).move_to([x, y, 0]).set_opacity(1 if .04 < f < .96 else 0))
        for k, r in enumerate(reflexo):
            r.set_stroke(opacity=.35 + .4 * (.5 + .5 * math.sin(t * 2.2 + k * 1.1)))
            r.move_to([sol_c[0] + .06 * math.sin(t * 1.5 + k), horizonte - .5 - k * .27, 0])
        for k, o in enumerate(ondas):
            x0, dy = onda_pos[k]
            x = ((x0 + .12 * t + 4.6) % 9.2) - 4.6
            o.move_to([x, horizonte + dy, 0])
            o.set_stroke(opacity=.25 + .45 * (.5 + .5 * math.sin(t * 1.7 + k * 2.1)))
        bx = -2.75 + .22 * t / max(dur, 1) * 3
        barco.become(barco_ref.copy().rotate(.05 * math.sin(t * 1.4)).move_to(
            [bx, horizonte - .55 + .04 * math.sin(t * 1.9), 0]))

    motor = Dot(fill_opacity=0, stroke_width=0)
    motor.add_updater(_vida)
    scene.add(ceu, halos, sol, grupo_nuvens, passaros, serra, morro1, morro2, arvores,
              lago, margem, reflexo, ondas, barco, motor)
    _vida(motor, 0)
    return T


def frente_lago(scene, T, chao_y):
    """Primeiro plano: a margem de areia, pedras, jarro e capim."""
    W = config.frame_width
    areia = Ellipse(width=W * 1.9, height=9.0, fill_color="#e4c792", fill_opacity=1, stroke_color=PT,
                    stroke_width=9).move_to([0, chao_y - 4.25, 0])
    base = Rectangle(width=W * 1.3, height=5.0, fill_color="#d6b57c", fill_opacity=1, stroke_width=0
                     ).move_to([0, chao_y - 3.2, 0])
    riscos = VGroup(*[ArcBetweenPoints([-W * .55, chao_y - .75 - k * .5, 0], [W * .55, chao_y - .8 - k * .5, 0],
                                       angle=.06 * (-1) ** k).set_stroke("#c9a86e", 4, opacity=.7)
                      for k in range(5)])
    pedras = VGroup(
        Ellipse(width=1.25, height=.72, fill_color="#a9a39a", fill_opacity=1, stroke_color=PT, stroke_width=7
                ).move_to([-3.0, chao_y + .3, 0]),
        Ellipse(width=.7, height=.44, fill_color="#bdb7ad", fill_opacity=1, stroke_color=PT, stroke_width=6
                ).move_to([-2.15, chao_y + .12, 0]))
    jarro = VGroup(
        Ellipse(width=.72, height=.9, fill_color="#c97b4a", fill_opacity=1, stroke_color=PT, stroke_width=7),
        Rectangle(width=.36, height=.22, fill_color="#c97b4a", fill_opacity=1, stroke_color=PT, stroke_width=6
                  ).shift(UP * .5),
        Line(LEFT * .3, RIGHT * .3, stroke_color="#f4c55b", stroke_width=5).shift(UP * .1),
    ).move_to([2.7, chao_y + .52, 0])
    capim_ref = VGroup(*[ArcBetweenPoints([3.45 + k * .12, chao_y + .05, 0],
                                          [3.35 + k * .2, chao_y + .85 + .1 * (k % 2), 0],
                                          angle=.5 - k * .25).set_stroke("#5b9469", 7) for k in range(5)])
    capim = capim_ref.copy()
    piv = np.array([3.6, chao_y + .05, 0])

    def _capim(m, dt):
        m.become(capim_ref.copy().rotate(.07 * math.sin(T() * 1.7), about_point=piv))
    capim.add_updater(_capim)
    scene.add(base, areia, riscos, pedras, jarro, capim)
