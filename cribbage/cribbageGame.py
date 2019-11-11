from cribbage.deck import Deck, card_to_string, peg_val
from copy import deepcopy

PAIR_SCORES={2:("Pair",2),3:("3 of a kind",6),4:("Four of a kind",12)}


def min_card(hand):
    """
    Returns a card with the minimum pegging value
    """
    c = hand[0]
    for i in range(1,len(hand)):
        if peg_val(hand[i]) < peg_val(c):
            c = hand[i]
    return c


def min_card_val(hand):
    """
    returns the pegging value of the minimum card
    """
    return min([peg_val(c) for c in hand])


def can_peg(hand, total):
    if len(hand) == 0:
        return False
    return min_card_val(hand) + total <= 31


class CribbageGame:
    def __init__(self, agent_a, agent_b):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.a_score = 0
        self.b_score = 0
        self.verbose=True

    def run_round(self, a_is_dealer):
        """
        Runs a round of cribbage between agent_a and agent_b
        :param a_is_dealer: if a is the dealer and gets the crib
        :return:
        """

        # setup
        deck = Deck()
        deck.shuffle()
        hand_a = deck.drawCards(6)
        hand_b = deck.drawCards(6)
        crib = []

        # discards
        discard_a = self.agent_a.discard_crib(deepcopy(hand_a), a_is_dealer)
        if len(discard_a) != 2:
            raise IllegalMoveException("Agent discarded more or less than 2 cards.")
        if discard_a[0] not in hand_a or discard_a[1] not in hand_a:
            raise IllegalMoveException("Agent discarded a card it did not own.")
        if discard_a[0] == discard_a[1]:
            raise IllegalMoveException("Agent discarded the same card twice.")

        discard_b = self.agent_b.discard_crib(deepcopy(hand_b), not a_is_dealer)
        if len(discard_b) != 2:
            raise IllegalMoveException("Agent discarded more or less than 2 cards.")
        if discard_b[0] not in hand_b or discard_b[1] not in hand_b:
            raise IllegalMoveException("Agent discarded a card it did not own.")
        if discard_b[0] == discard_b[1]:
            raise IllegalMoveException("Agent discarded the same card twice.")
        crib = [discard_a[0],discard_a[1],discard_b[0],discard_b[1]]

        # cut card
        cut_card = deck.drawCard()
        if self.verbose:
            print("The cut card is the",card_to_string(cut_card))
        if cut_card[0] is 11: # if the a jack is turned
            self.score_points(2, "His heels", a_is_dealer)

        self.pegging(hand_a,hand_b,a_is_dealer)

    def score_points(self,amount, reason, is_a):
        if is_a:
            self.a_score += amount
        else:
            self.b_score += amount
        if self.verbose:
            print("%s for %d (%s)"%(reason, amount, "A" if is_a else "B"))

    def pegging(self, hand_a, hand_b, is_a):
        """
        :param hand_a: the hand of player a. Must be a copy/mutable
        :param hand_b: the hand of player b. Must be a copy/mutable
        :param is_a: a starts the pegging
        """
        #
        # next_player = hand_b if a_goes_first else hand_a
        total = 0
        seq = []

        while True:
            player = self.agent_a if is_a else self.agent_b
            hand = hand_a if is_a else hand_b
            # the current player can play
            if can_peg(hand, total):
                pick = player.pegging_move(deepcopy(hand), deepcopy(seq), total)
                # a card should be played
                if pick is None:
                    raise IllegalMoveException("Must play a card if able to")
                if pick not in hand:
                    raise IllegalMoveException("Must play a card from your hand")
                if peg_val(pick) + total > 31:
                    raise IllegalMoveException("Cannot play a card resulting in a sum over 31")
                seq.append(pick)
                hand.remove(pick)
                total += peg_val(pick)
                if self.verbose:
                    print("%s played the %s for %d" % ("A" if is_a else "B",card_to_string(pick),total))
                    # print("total:", total)
                    # print("sequence:", ", ".join([card_to_string(c) for c in seq]))
                self.score_pegging(seq, total, is_a)
            if not can_peg(hand_a,total) and not can_peg(hand_b,total):
                # neither person can go
                self.score_points(1,"Last card", is_a)
                total=0
                seq=[]

            is_a = not is_a

            if len(hand_a) == 0 and len(hand_b) == 0:
                # pegging is finished
                return

    def score_pegging(self, seq, total, is_a):
        """
        Scores a single play in pegging
        :param seq:
        :param total:
        :param is_a:
        :return:
        """
        if len(seq)<2:
            return
        if total == 15:
            self.score_points(2,"Fifteen", is_a)
        if total == 21:
            self.score_points(1,"Thirty one",is_a)
        run_up=0
        run_down=0
        continue_run=True
        pair=1
        continue_pair = True
        top_card=seq[-1]
        for i in range(len(seq)-2,-1,-1):
            if continue_pair:
                if seq[i] == top_card:
                    pair += 1
                else:
                    continue_pair = False

            if continue_run:
                if seq[i][0]==top_card[0]-1-run_down:
                    # card we're looking at is part of a sequence down
                    run_down += 1
                elif seq[i][0]==top_card[0]+1+run_up:
                    run_up += 1
                else:
                    continue_run = False
        if pair in PAIR_SCORES:
            self.score_points(PAIR_SCORES[pair][1],PAIR_SCORES[pair][0],is_a)
        run_total = run_up+run_down+1
        if run_total>2:
            self.score_points(run_total,"A run of %d"%run_total,is_a)

        return 0

    def pegging_round(self,hand_a,hand_b,a_goes_first):
        pass


class IllegalMoveException(Exception):
    pass

