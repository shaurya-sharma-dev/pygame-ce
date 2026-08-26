# This file uses vendored-in code from pygame-ce, licensed under LGPL 2.1.

import pygame as pg
import time
import statistics
import gc

pg.print_debug_info()

def gen_ag():
    ag = pg.sprite.AbstractGroup()

    for _ in range(100):
        s = pg.sprite.Sprite()
        s.image = pg.Surface((10, 10))
        s.rect = s.image.get_rect(center=(0, 0))
        ag.add(s)

    return ag

def spritecollide_dokill_lambda(sprite, group, dokill, collided=None, exclude=None):
    exclude = exclude if exclude is not None else set()

    collided = (
        collided
        if collided is not None
        else lambda sprite, group_sprite: sprite.rect.colliderect(group_sprite.rect)
    )

    kill_if_do_kill = (
        (lambda group_sprite: (group_sprite.kill(), group_sprite)[1])
        if dokill
        else (lambda group_sprite: group_sprite)
    )

    collided_sprites = [
        kill_if_do_kill(group_sprite)
        for group_sprite in group
        if group_sprite not in exclude and collided(sprite, group_sprite)
    ]
    return collided_sprites

def spritecollide_dokill_subsequent_iter(sprite, group, dokill, collided=None, exclude=None):
    exclude = exclude if exclude is not None else set()

    collided = (
        collided
        if collided is not None
        else lambda sprite, group_sprite: sprite.rect.colliderect(group_sprite.rect)
    )

    collided_sprites = [
        group_sprite
        for group_sprite in group
        if group_sprite not in exclude and collided(sprite, group_sprite)
    ]

    if dokill:
        for sprite in collided_sprites:
            sprite.kill()

    return collided_sprites

sprite = pg.sprite.Sprite()
sprite.image = pg.Surface((10, 10))
sprite.rect = sprite.image.get_rect(center=(0, 0))

perc_changes = []

for _ in range(250):
    ag = gen_ag()
    before_lambda_run = time.perf_counter()
    spritecollide_dokill_lambda(sprite, ag, True)
    lambda_time = time.perf_counter() - before_lambda_run

    time.sleep(.2)
    gc.collect()

    ag = gen_ag()
    before_subsequent_iter_run = time.perf_counter()
    spritecollide_dokill_subsequent_iter(sprite, ag, True)
    sub_iter_time = time.perf_counter() - before_subsequent_iter_run

    perc_change = ((lambda_time - sub_iter_time) / abs(sub_iter_time)) * 100
    perc_changes.append(perc_change)
    print(f"Percentage change:\t{perc_change:.2f}%")
    time.sleep(.2)
    gc.collect()

print(f"Average percentage change:\t{statistics.mean(perc_changes):.2f}%")