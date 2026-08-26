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

def spritecollide_old(sprite, group, dokill, collided=None):
    # Copied from main.
    if collided is not None:
        collided_sprites = [
            group_sprite for group_sprite in group if collided(sprite, group_sprite)
        ]
    else:
        sprite_rect_collide = sprite.rect.colliderect
        collided_sprites = [
            group_sprite
            for group_sprite in group
            if sprite_rect_collide(group_sprite.rect)
        ]
    if dokill:
        for group_sprite in collided_sprites:
            group_sprite.kill()
    return collided_sprites

def spritecollide_new(sprite, group, dokill, collided=None, exclude=None):
    # Copied from PR.
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
        for group_sprite in collided_sprites:
            group_sprite.kill()

    return collided_sprites

sprite = pg.sprite.Sprite()
sprite.image = pg.Surface((10, 10))
sprite.rect = sprite.image.get_rect(center=(0, 0))

perc_changes = []

for _ in range(250):
    ag = gen_ag()
    before_old_run = time.perf_counter()
    spritecollide_old(sprite, ag, True)
    old_time = time.perf_counter() - before_old_run

    time.sleep(.2)
    gc.collect()

    ag = gen_ag()
    before_new_run = time.perf_counter()
    spritecollide_new(sprite, ag, True)
    new_time = time.perf_counter() - before_new_run

    perc_change = ((new_time - old_time) / abs(old_time)) * 100
    perc_changes.append(perc_change)
    print(f"Percentage change:\t{perc_change:.2f}%")
    time.sleep(.2)
    gc.collect()

print(f"Average percentage change:\t{statistics.mean(perc_changes):.2f}%")