import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1100, 650

DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（左方向判定結果、縦方向判定結果）
    Trueなら画面内、Falseなら画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img1 = pg.transform.flip(img0, True, False)

    return {
        (0, 0): img1,
        (5, 0): img1,
        (5, -5): pg.transform.rotozoom(img1, 45, 1.0),
        (0, -5): pg.transform.rotozoom(img1, 90, 1.0),
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),
        (-5, 0): img0,
        (-5, 5): pg.transform.rotozoom(img0, 45, 1.0),
        (0, 5): pg.transform.rotozoom(img1, -90, 1.0),
        (5, 5): pg.transform.rotozoom(img1, -45, 1.0),
    }

def gameover(screen: pg.Surface) -> None:
    # 1. 黒い矩形を描画するための空のSurfaceを作り，黒い矩形を描画する
    go_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(go_img, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT)) 

    # 2. 1のSurfaceの透明度を設定する
    go_img.set_alpha(150)

    # 3. 白文字でGame Overと書かれたフォントSurfaceを作り，1のSurfaceにblitする
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect()
    txt_rect.center = (WIDTH // 2, HEIGHT // 2)
    go_img.blit(txt, txt_rect)

    # 4. こうかとん画像をロードし，こうかとんSurfaceを作り，1のSurfaceにblitする
    kkgo_img = pg.transform.rotozoom(pg.image.load("fig/4.png"), 0, 0.9)
    
    kkgo_rect_left = kkgo_img.get_rect()
    kkgo_rect_left.center = (WIDTH // 2 - 200, HEIGHT // 2)
    
    kkgo_rect_right = kkgo_img.get_rect()
    kkgo_rect_right.center = (WIDTH // 2 + 200, HEIGHT // 2)
    
    go_img.blit(kkgo_img, kkgo_rect_left)
    go_img.blit(kkgo_img, kkgo_rect_right)

    # 5. 1のSurfaceをscreen Surfaceにblitする
    screen.blit(go_img, [0, 0])

    # 6. pg.display.update()したら，time.sleep(5)する
    pg.display.update()
    time.sleep(5)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx = random.choice([-5, 5])
    vy = random.choice([-5, 5])
    tmr = 0     

    clock = pg.time.Clock()
    
    # フォントの準備
    font = pg.font.Font(None, 50)
    score = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
                
        idx = min(tmr // 500, 9)
        level = idx + 1
        score += 2
                
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
            
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) 
            
        kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]

        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        screen.blit(bb_img, bb_rct)
        
        # スコア、レベルのテキストを描画する
        score_txt = font.render(f"Score: {score}", True, (0, 0, 0))
        level_txt = font.render(f"Level: {level}", True, (0, 0, 0))

        screen.blit(score_txt, [20, 20])
        screen.blit(level_txt, [20, 70])
        
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()