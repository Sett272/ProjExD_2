import os
import random
import sys
import pygame as pg

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -10), #上矢印キー
    pg.K_DOWN: (0, 10), #下矢印キー
    pg.K_LEFT: (-10, 0), #左矢印キー
    pg.K_RIGHT: (10, 0), #右矢印キー
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（左方向判定結果、縦方向判定結果）
    Trueなら画面内、Falseなら画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: #横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向判定
        tate = False
    return yoko, tate

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0)) # 背景が黒くならないように透過処理を維持
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def gameover(screen:pg.Surface) -> None:
    #黒画面
    go_img = pg.Surface((WIDTH, HEIGHT))
    go_img.fill((0, 0, 0))
    go_img.set_alpha(150)
    screen.blit(go_img, [0, 0])
    
    #Game Over
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255)) # 白文字で描画したSurfaceを作成
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(txt, txt_rect)

    kkgo_img = pg.transform.rotozoom(pg.image.load("fig/4.png"), 0, 0.9)
    
    # 左側のこうかとん (中心からX座標を-200ずらす)
    kkgo_rect_left = kkgo_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))
    screen.blit(kkgo_img, kkgo_rect_left)
    
    # 右側のこうかとん (中心からX座標を+200ずらす)
    kkgo_rect_right = kkgo_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))
    screen.blit(kkgo_img, kkgo_rect_right)

    # 4. 画面を更新して5秒待つ
    pg.display.update()
    pg.time.wait(5000)

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9) 
    img1 = pg.transform.flip(img0, True, False) 

    return {
        (0, 0): img1, # キー押下がない場合は右向き
        (10, 0): img1, # 右
        (10, -10): pg.transform.rotozoom(img1, -45, 1.0), # 右上
        (0, -10): pg.transform.rotozoom(img1, -90, 1.0), # 上
        (-10, -10): pg.transform.rotozoom(img0, 45, 1.0), # 左上
        (-10, 0): img0, # 左
        (-10, 10): pg.transform.rotozoom(img0, -45, 1.0), # 左下
        (0, 10): pg.transform.rotozoom(img1, 90, 1.0), # 下
        (10, 10): pg.transform.rotozoom(img1, 45, 1.0), # 右下
}
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    
    # while文の前で呼び出して2つのリストを得る
    bb_imgs, bb_accs = init_bb_imgs()

    # 爆弾の初期化
    bb_img = bb_imgs[0]
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
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向に移動量
                sum_mv[1] += mv[1] #縦方向の移動量
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            #動きをキャンセルします
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) 
        kk_img = get_kk_imgs().get(tuple(sum_mv), get_kk_imgs()[(0, 0)])
        screen.blit(kk_img, kk_rct)

        # while文の中でtmrの値に応じて、リストから適切な要素を選択する
        avx = vx * bb_accs[min(tmr//500, 9)]
        avy = vy * bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]

        # Surfaceの大きさが変わった場合は、Rectのwidth属性とheight属性を更新する
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        #爆弾の移動と境界判定 (avx, avy を使う)
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1 # カウントアップ
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()