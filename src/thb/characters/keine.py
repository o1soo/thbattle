# -*- coding: utf-8 -*-
from __future__ import absolute_import

# -- stdlib --
# -- third party --
# -- own --
from game.autoenv import EventHandler, Game, GameException, user_input
from thb.actions import ActionStage, ActiveDropCards, BaseActionStage, DrawCards, DropCards
from thb.actions import GenericAction, LaunchCard, LifeLost, MaxLifeChange, PrepareStage, Reforge
from thb.actions import UserAction, migrate_cards, random_choose_card, ttags, user_choose_cards
from thb.cards import Card, Heal, PhysicalCard, Skill, VirtualCard, t_None, t_OtherOne
from thb.characters.baseclasses import Character, register_character_to
from thb.inputlets import ChooseOptionInputlet


# -- code --
class TeachTargetReforgeAction(UserAction):
    def apply_action(self):
        g = Game.getgame()
        tgt = self.target
        c = user_choose_cards(self, tgt, ('cards', 'showncards', 'equips'))
        c = c[0] if c else random_choose_card([tgt.cards, tgt.showncards, tgt.equips])
        if not c:
            return False

        g.process_action(Reforge(tgt, tgt, c))
        return True

    def cond(self, cards):
        return len(cards) == 1 and cards[0].is_card(PhysicalCard)


class TeachTargetActionStage(BaseActionStage):
    one_shot = True
    launch_card_cls = LaunchCard


class TeachTargetEffect(GenericAction):
    def __init__(self, source, target, card):
        self.source = source
        self.target = target
        self.card = card

    def apply_action(self):
        tgt = self.target
        c = self.card
        g = Game.getgame()
        tgt.reveal(c)
        migrate_cards([c], tgt.cards, unwrap=True)

        choice = user_input([tgt], ChooseOptionInputlet(self, ('reforge', 'action')))
        if choice == 'reforge':
            g.process_action(TeachTargetReforgeAction(tgt, tgt))
        else:
            act = TeachTargetActionStage(tgt)
            g.process_action(act)
            if act.action_count != 1:
                c = random_choose_card([tgt.cards, tgt.showncards, tgt.equips])
                if c:
                    g.players.reveal(c)
                    g.process_action(Reforge(tgt, tgt, c))

        return True


class TeachAction(UserAction):
    no_reveal = True

    def apply_action(self):
        src, tgt = self.source, self.target
        cl = VirtualCard.unwrap([self.associated_card])
        assert len(cl) == 1
        g = Game.getgame()
        ttags(src)['teach_used'] = True
        g.process_action(Reforge(src, src, cl[0]))
        cl = user_choose_cards(self, src, ('cards', 'showncards', 'equips'))
        c = cl[0] if cl else random_choose_card([src.cards, src.showncards, src.equips])
        g.process_action(TeachTargetEffect(src, tgt, c))
        return True

    def cond(self, cl):
        return len(cl) == 1 and not cl[0].is_card(VirtualCard)

    def is_valid(self):
        tgt = self.target
        return not ttags(tgt)['teach_used']


class Teach(Skill):
    associated_action = TeachAction
    skill_category = ('character', 'active')
    no_drop = True
    target = t_OtherOne
    usage = 'reforge'

    def check(self):
        if not self.associated_cards:
            return False

        c = self.associated_cards[0]
        return c.is_card(PhysicalCard)


class KeineGuard(Skill):
    associated_action = None
    skill_category = ('character', 'passive', 'awake')
    target = t_None


class KeineGuardAwake(UserAction):
    def apply_action(self):
        tgt = self.target
        g = Game.getgame()
        g.process_action(MaxLifeChange(tgt, tgt, -1))
        tgt.skills.remove(KeineGuard)
        tgt.skills.append(Devour)
        return True


class KeineGuardHandler(EventHandler):
    interested = ('action_before',)

    def handle(self, evt_type, act):
        if evt_type == 'action_before' and isinstance(act, PrepareStage):
            tgt = act.target
            g = Game.getgame()

            cond = True and tgt.has_skill(KeineGuard)
            cond = cond and (tgt.life <= min([p.life for p in g.players if not p.dead]))
            cond = cond and tgt.life < tgt.maxlife

            if cond:
                g.process_action(KeineGuardAwake(tgt, tgt))

        return act


class Devour(Skill):
    associated_action = None
    skill_category = ('character', 'passive')
    target = t_None


class DevourAction(UserAction):
    def __init__(self, source, target, card):
        self.source = source
        self.target = target
        self.card = card

    def apply_action(self):
        src, tgt = self.source, self.target
        c = self.card
        g = Game.getgame()
        ttags(tgt)['devour_effect'] = {
            'effect': 'life' if c.color == Card.RED else 'cards',
            'life': tgt.life,
            'cards': len(tgt.cards) + len(tgt.showncards),
            'source': src,
        }
        g.process_action(DropCards(src, src, [c]))
        return True


class DevourEffect(GenericAction):
    def __init__(self, source, target, params):
        self.source = source
        self.target = target
        self.params = params

    def apply_action(self):
        tgt = self.target
        params = self.params
        g = Game.getgame()
        if params['effect'] == 'life':
            to = params['life']
            if to > tgt.life:
                g.process_action(Heal(tgt, tgt, abs(to - tgt.life)))
            elif to < tgt.life:
                g.process_action(LifeLost(tgt, tgt, abs(to - tgt.life)))
        elif params['effect'] == 'cards':
            to = params['cards']
            cur = len(tgt.cards) + len(tgt.showncards)
            if to > cur:
                g.process_action(DrawCards(tgt, abs(to - cur)))
            elif to < cur:
                g.process_action(ActiveDropCards(tgt, tgt, abs(to - cur)))
        else:
            raise GameException('WTF?!')

        return True


class DevourHandler(EventHandler):
    interested = ('action_before', 'action_after')

    def handle(self, evt_type, act):
        if evt_type == 'action_before' and isinstance(act, ActionStage):
            g = Game.getgame()
            tgt = act.target
            for p in g.players:
                if p.dead or not p.has_skill(Devour):
                    continue

                if ttags(p)['devour_used']:
                    continue

                cl = user_choose_cards(self, p, ('cards', 'showncards', 'equips'))
                if not cl:
                    continue

                g.process_action(DevourAction(p, tgt, cl[0]))

        elif evt_type == 'action_after' and isinstance(act, ActionStage):
            tgt = act.target
            t = ttags(tgt)['devour_effect']
            if t:
                g = Game.getgame()
                g.process_action(DevourEffect(t['source'], tgt, t))

        return act

    def cond(self, cl):
        if len(cl) != 1:
            return False

        c = cl[0]
        return c.is_card(PhysicalCard) and 'basic' in c.category


@register_character_to('common')
class Keine(Character):
    skills = [Teach, KeineGuard]
    eventhandlers_required = [KeineGuardHandler, DevourHandler]
    maxlife = 4
