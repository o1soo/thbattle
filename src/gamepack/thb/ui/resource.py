import pyglet
import os

from client.ui.resource import ResLoader

with ResLoader(__file__) as args:
    locals().update(args)

    bgm_game = lambda: ldr.media('bgm_game.ogg')

    thblogo_3v3 = tx('thblogo_3v3.png')

    card_attack = tx('card_attack.png')
    tag_attacked = anim('tag_attacked.png', [10000], True)
    card_graze = tx('card_graze.png')
    card_heal = tx('card_heal.png')
    card_demolition = tx('card_demolition.png')
    card_reject = tx('card_reject.png')
    card_sealarray = tx('card_sealarray.png')
    tag_sealarray = anim('tag_sealarray.png', [83]*36, True)

    card_nazrinrod= tx('card_nazrinrod.png')
    card_opticalcloak = tx('card_opticalcloak.png')
    card_opticalcloak_small = tx('card_opticalcloak_small.png')
    card_greenufo = tx('card_greenufo.png')
    card_greenufo_small = tx('card_greenufo_small.png')
    card_redufo = tx('card_redufo.png')
    card_redufo_small = tx('card_redufo_small.png')
    card_sinsack = tx('card_sinsack.png')
    tag_sinsack = anim('tag_sinsack.png', [10000], True)
    card_yukaridimension = tx('card_yukaridimension.png')
    card_duel = tx('card_duel.png')
    card_sinsackcarnival = tx('card_sinsackcarnival.png')
    card_mapcannon = tx('card_mapcannon.png')
    card_hakurouken = tx('card_hakurouken.png')
    card_hakurouken_small = tx('card_hakurouken_small.png')
    card_reactor = tx('card_reactor.png')
    card_reactor_small = tx('card_reactor_small.png')
    card_umbrella = tx('card_umbrella.png')
    card_umbrella_small = tx('card_umbrella_small.png')
    card_roukanken = tx('card_roukanken.png')
    card_roukanken_small = tx('card_roukanken_small.png')
    card_gungnir = tx('card_gungnir.png')
    card_gungnir_small = tx('card_gungnir_small.png')
    card_laevatein = tx('card_laevatein.png')
    card_laevatein_small = tx('card_laevatein_small.png')
    card_trident = tx('card_trident.png')
    card_trident_small = tx('card_trident_small.png')
    card_repentancestick = tx('card_repentancestick.png')
    card_repentancestick_small = tx('card_repentancestick_small.png')
    card_wine = tx('card_wine.png')
    tag_wine = anim('tag_wine.png', [150]*3, True)
    card_feast = tx('card_feast.png')
    card_harvest = tx('card_harvest.png')
    card_maidencostume = tx('card_maidencostume.png')
    card_maidencostume_small = tx('card_maidencostume_small.png')
    card_exinwan = tx('card_exinwan.png')
    card_ibukigourd = tx('card_ibukigourd.png')
    card_ibukigourd_small = tx('card_ibukigourd_small.png')
    card_houraijewel = tx('card_houraijewel.png')
    card_houraijewel_small = tx('card_houraijewel_small.png')
    card_saigyoubranch = tx('card_saigyoubranch.png')
    card_saigyoubranch_small = tx('card_saigyoubranch_small.png')
    card_flirtingsword = tx('card_flirtingsword.png')
    card_flirtingsword_small = tx('card_flirtingsword_small.png')
    card_camera = tx('card_camera.png')
    card_ayaroundfan = tx('card_ayaroundfan.png')
    card_ayaroundfan_small = tx('card_ayaroundfan_small.png')
    card_scarletrhapsodysword = tx('card_scarletrhapsodysword.png')
    card_scarletrhapsodysword_small = tx('card_scarletrhapsodysword_small.png')
    card_deathsickle = tx('card_deathsickle.png')
    card_deathsickle_small = tx('card_deathsickle_small.png')
    card_keystone = tx('card_keystone.png')
    card_keystone_small = tx('card_keystone_small.png')
    card_witchbroom = tx('card_witchbroom.png')
    card_witchbroom_small = tx('card_witchbroom_small.png')
    card_yinyangorb = tx('card_yinyangorb.png')
    card_yinyangorb_small = tx('card_yinyangorb_small.png')
    card_suwakohat = tx('card_suwakohat.png')
    card_suwakohat_small = tx('card_suwakohat_small.png')
    card_phantom = tx('card_phantom.png')
    card_phantom_small = tx('card_phantom_small.png')
    card_icewing = tx('card_icewing.png')
    card_icewing_small = tx('card_icewing_small.png')
    card_grimoire = tx('card_grimoire.png')
    card_grimoire_small = tx('card_grimoire_small.png')
    card_dollcontrol = tx('card_dollcontrol.png')
    card_donationbox = tx('card_donationbox.png')

    parsee_port = tx('parsee_port.png')
    youmu_port = tx('youmu_port.png')
    koakuma_port = tx('koakuma_port.png')
    marisa_port = tx('marisa_port.png')
    daiyousei_port = tx('daiyousei_port.png')
    flandre_port = tx('flandre_port.png')
    tag_flandrecs = anim('tag_flandrecs.png', [10000], True)
    nazrin_port = tx('nazrin_port.png')
    alice_port = tx('alice_port.png')
    yugi_port = tx('yugi_port.png')
    tewi_port = tx('tewi_port.png')
    patchouli_port = tx('patchouli_port.png')
    reimu_port = tx('reimu_port.png')
    eirin_port = tx('eirin_port.png')
    kogasa_port = tx('kogasa_port.png')
    shikieiki_port = tx('shikieiki_port.png')
    tenshi_port = tx('tenshi_port.png')
    rumia_port = tx('rumia_port.png')
    yuuka_port = tx('yuuka_port.png')
    rinnosuke_port = tx('rinnosuke_port.png')
    ran_port = tx('ran_port.png')
    remilia_port = tx('remilia_port.png')
    minoriko_port = tx('minoriko_port.png')
    meirin_port = tx('meirin_port.png')
    suika_port = tx('suika_port.png')

    for k in args.keys(): del k
    del args
