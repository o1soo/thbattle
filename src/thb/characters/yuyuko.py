# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# -- stdlib --
# -- third party --
# -- own --
from game.autoenv import EventHandler, Game, user_input
from thb.actions import DrawCards, DummyAction, FinalizeStage, GenericAction, LifeLost
from thb.actions import MaxLifeChange, Pindian, PlayerDeath, TryRevive, UserAction, ttags
from thb.cards import Heal, Skill, t_None, t_OtherOne
from thb.characters.baseclasses import Character, register_character_to
from thb.inputlets import ChooseOptionInputlet


# -- code --
class GuidedDeath(Skill):
    associated_action = None
    skill_category = ('character', 'passive')
    target = t_None


class GuidedDeathLifeLost(LifeLost):
    pass


class GuidedDeathEffect(GenericAction):
    def __init__(self, source, target_list):
        self.source = source
        self.target = source
        self.target_list = target_list

    def apply_action(self):
        g = Game.getgame()

        for p in self.target_list:
            g.process_action(GuidedDeathLifeLost(p, p))

        return True


class GuidedDeathHandler(EventHandler):
    interested = ('action_apply',)

    def handle(self, evt_type, act):
        if evt_type == 'action_apply' and isinstance(act, FinalizeStage):
            g = Game.getgame()

            src = act.target
            if not (src.has_skill(GuidedDeath) and not src.dead):
                return act

            tl = [p for p in g.players.rotate_to(src) if p.life == 1 and p is not src]
            if not tl:
                return act

            g.process_action(GuidedDeathEffect(src, tl))

        return act


class SoulDrain(Skill):
    associated_action = None
    skill_category = ('character', 'passive')
    target = t_None


class SoulDrainEffect(GenericAction):
    def apply_action(self):
        src, tgt = self.source, self.target
        g = Game.getgame()
        g.process_action(DrawCards(src, 1))

        assert tgt.life <= 0

        if not tgt.cards and not tgt.showncards:
            return True

        if src is tgt:
            return True

        if user_input([src], ChooseOptionInputlet(self, (False, True))):
            if g.process_action(Pindian(src, tgt)):
                g.process_action(MaxLifeChange(src, tgt, -tgt.maxlife + 1))
            else:
                g.process_action(Heal(src, tgt, -tgt.life + 1))

        return True


class SoulDrainHandler(EventHandler):
    interested = ('action_before',)

    def handle(self, evt_type, act):
        if evt_type == 'action_before' and isinstance(act, TryRevive):
            g = Game.getgame()
            tgt = act.target

            for p in g.players:
                if p.has_skill(SoulDrain) and not p.dead and p is not tgt:
                    break
            else:
                return act

            g.process_action(SoulDrainEffect(p, tgt))

            if tgt.life > 0:
                # Abort TryRevive process
                return DummyAction(p, act.target)
            else:
                return act

        return act


class PerfectCherryBlossomHandler(EventHandler):
    interested = ('action_apply',)

    def handle(self, evt_type, act):
        if evt_type == 'action_apply' and isinstance(act, PlayerDeath):
            g = Game.getgame()
            for pcb in reversed(g.action_stack):
                if isinstance(pcb, PerfectCherryBlossomAction):
                    break
            else:
                return act

            src, tgt = pcb.source, pcb.target

            if src.dead:
                return act

            g.process_action(PerfectCherryBlossomExtractAction(src, tgt))

        return act


class PerfectCherryBlossomExtractAction(UserAction):
    def apply_action(self):
        g = Game.getgame()
        src = self.source
        g.process_action(MaxLifeChange(src, src, 1))
        g.process_action(Heal(src, src, 1))

        try:
            src.skills.remove(PerfectCherryBlossom)
        except Exception:
            pass

        return True


class PerfectCherryBlossomAction(UserAction):
    def apply_action(self):
        src, tgt = self.source, self.target
        if tgt.dead: return True
        g = Game.getgame()
        ttags(src)['perfect_cherry_blossom'] = True
        g.process_action(LifeLost(src, tgt, 1))
        if not tgt.dead:
            g.process_action(Heal(tgt, tgt, 1))

        return True

    def is_valid(self):
        src, tgt = self.source, self.target
        if ttags(src)['perfect_cherry_blossom']:
            return False
        if not tgt.life < tgt.maxlife:
            return False
        return True


class PerfectCherryBlossom(Skill):
    associated_action = PerfectCherryBlossomAction
    skill_category = ('character', 'active')
    target = t_OtherOne
    usage = 'drop'

    def check(self):
        cl = self.associated_cards
        return len(cl) == 0


@register_character_to('common')
class Yuyuko(Character):
    skills = [GuidedDeath, SoulDrain, PerfectCherryBlossom]
    eventhandlers_required = [GuidedDeathHandler, SoulDrainHandler, PerfectCherryBlossomHandler]
    maxlife = 3
