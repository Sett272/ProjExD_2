import os
import random
import sys
import pygame as pg



WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), #上矢印キー
    pg.K_DOWN: (0, 5), #下矢印キー
    pg.K_LEFT: (-5, 0), #左矢印キー
    pg.K_RIGHT: (5, 0), #右矢印キー
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（左方向判定結果、縦方向判定結果
    Trueなら画面内、Falseなら画面外"""
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: #横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向判定
        tate = False
    return yoko, tate

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    

    #爆弾の初期化

    bb_radius = 10
    bb_img = pg.Surface((bb_radius * 2, bb_radius * 2)) #爆弾用の空のsurface
    pg.draw.circle(bb_img, (255, 0, 0), (bb_radius, bb_radius), bb_radius)
    bb_img.set_colorkey((0, 0, 0)) 
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH) #横
    bb_rct.centery = random.randint(0, HEIGHT) #縦
    vx = random.choice([-5, 5])
    vy = random.choice([-5, 5])
    tmr = 0     

    clock = pg.time.Clock()
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            print("Game Over")
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向に移動量
                sum_mv[1] += mv[1] #縦方向の移動量
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            #動きをキャンセルします
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) #動きをなかったことにする
        screen.blit(kk_img, kk_rct)

        #爆弾の移動と境界判定
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 2
        if tmr % 300 == 0:
            bb_radius += 2
            vx += 1 if vx > 0 else -1
            vy += 1 if vy > 0 else -1
            center = bb_rct.center
            bb_img = pg.Surface((bb_radius * 2, bb_radius * 2))
            pg.draw.circle(bb_img, (255, 0, 0), (bb_radius, bb_radius), bb_radius)
            bb_img.set_colorkey((0, 0, 0))
            bb_rct = bb_img.get_rect()
            bb_rct.center = center
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
