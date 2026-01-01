import pygame as pg
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_a, K_d, K_w, K_s
import random

# Initialiser pygame
pg.init()

# Konstanter for spillet
VINDU_BREDDE = 300
VINDU_HØYDE = 600
RUTESTØRRELSE = 30
RADER = VINDU_HØYDE // RUTESTØRRELSE
KOLONNER = VINDU_BREDDE // RUTESTØRRELSE

# Definer farger
SVART = (0, 0, 0)
HVIT = (255, 255, 255)
BLÅ = (0, 0, 255)

# Tetromino-former
tetrominoer = {
    'I': [(0, 0), (-1, 0), (1, 0), (2, 0)],
    'J': [(0, 0), (-1, 0), (-1, 1), (1, 0)],
    'L': [(0, 0), (-1, 0), (1, 0), (1, 1)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'S': [(0, 0), (0, 1), (-1, 1), (1, 0)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, 1)],
    'Z': [(0, 0), (0, 1), (1, 1), (-1, 0)]
}

# Opprett spillvinduet
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HØYDE])

class TetrisBrikke:
    def __init__(self, form, x, y, farge):
        self.form = form
        self.x = x
        self.y = y
        self.farge = farge

    def tegn(self, overflate):
        for dx, dy in self.form:
            rektangel = (self.x + dx) * RUTESTØRRELSE, (self.y + dy) * RUTESTØRRELSE, RUTESTØRRELSE, RUTESTØRRELSE
            pg.draw.rect(overflate, self.farge, rektangel)

class Brett:
    def __init__(self):
        self.rutenett = [[0] * KOLONNER for _ in range(RADER)]
        self.rutenett.append([1] * KOLONNER)  # Bunn-grense

    def legg_til_brikke(self, brikke):
        for dx, dy in brikke.form:
            self.rutenett[brikke.y + dy][brikke.x + dx] = 1

    def er_godkjent_posisjon(self, brikke, dx, dy):
        for x, y in brikke.form:
            ny_x = brikke.x + dx + x
            ny_y = brikke.y + dy + y
            if ny_x < 0 or ny_x >= KOLONNER or ny_y < 0 or ny_y >= RADER or self.rutenett[ny_y][ny_x]:
                return False
        return True

    def fjern_linjer(self):
        nytt_rutenett = [rad for rad in self.rutenett if any(celle == 0 for celle in rad)]
        fjernede_linjer = RADER - len(nytt_rutenett)
        nytt_rutenett = [[0] * KOLONNER for _ in range(fjernede_linjer)] + nytt_rutenett
        self.rutenett = nytt_rutenett
        return fjernede_linjer

class Spiller:
    def __init__(self, brett):
        self.brett = brett
        self.nåværende_brikke = self.ny_brikke()
        self.neste_brikke = self.ny_brikke()
        self.poeng = 0

    def ny_brikke(self):
        form = random.choice(list(tetrominoer.keys()))
        return TetrisBrikke(tetrominoer[form], KOLONNER // 2, 0, BLÅ)

    def flytt_brikke(self, dx, dy):
        if self.brett.er_godkjent_posisjon(self.nåværende_brikke, dx, dy):
            self.nåværende_brikke.x += dx
            self.nåværende_brikke.y += dy
            return True
        return False

    def roter_brikke(self):
        rotert_form = [(-y, x) for x, y in self.nåværende_brikke.form]
        rotert_brikke = TetrisBrikke(rotert_form, self.nåværende_brikke.x, self.nåværende_brikke.y, self.nåværende_brikke.farge)
        if self.brett.er_godkjent_posisjon(rotert_brikke, 0, 0):
            self.nåværende_brikke.form = rotert_form

    def hard_drop(self):
        while self.flytt_brikke(0, 1):
            pass
        self.lås_brikke()

    def lås_brikke(self):
        self.brett.legg_til_brikke(self.nåværende_brikke)
        fjernede_linjer = self.brett.fjern_linjer()
        self.poeng += fjernede_linjer
        self.nåværende_brikke = self.neste_brikke
        self.neste_brikke = self.ny_brikke()

    def tegn(self, overflate):
        self.nåværende_brikke.tegn(overflate)
        for y in range(RADER):
            for x in range(KOLONNER):
                if self.brett.rutenett[y][x]:
                    rektangel = x * RUTESTØRRELSE, y * RUTESTØRRELSE, RUTESTØRRELSE, RUTESTØRRELSE
                    pg.draw.rect(overflate, HVIT, rektangel)

# Hovedspill-løkke
def hoved():
    brett = Brett()
    spiller = Spiller(brett)
    klokke = pg.time.Clock()
    fall_tid = 0
    fall_hastighet = 500  # Millisekunder

    kjører = True
    while kjører:
        fall_tid += klokke.get_rawtime()
        klokke.tick()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                kjører = False
            if event.type == pg.KEYDOWN:
                if event.key == K_a:
                    spiller.flytt_brikke(-1, 0)
                elif event.key == K_d:
                    spiller.flytt_brikke(1, 0)
                elif event.key == K_s:
                    spiller.flytt_brikke(0, 1)
                elif event.key == K_w:
                    spiller.roter_brikke()
                elif event.key == pg.K_SPACE:
                    spiller.hard_drop()

        if fall_tid > fall_hastighet:
            if not spiller.flytt_brikke(0, 1):
                spiller.lås_brikke()
            fall_tid = 0

        vindu.fill(SVART)
        spiller.tegn(vindu)
        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    hoved()
