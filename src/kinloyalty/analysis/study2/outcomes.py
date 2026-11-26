"""Define Study 2 outcome eligibility and signed buyer-offer summaries."""

from collections.abc import Iterable

from kinloyalty.negotiation.transcript import TranscriptTurn


OUTCOME_NOTES = {
    'surplus_share': 'Deals: (b-p)/(b-s); impasses: zero; exclusions: unavailable. No clipping.',
    'within_deal_share': 'Defined only among deals. Conditions on agreement, which the card can affect.',
    'deal': 'One for a deal, zero for either impasse; exclusions unavailable.',
    'messages_to_agreement': 'Valid messages used, among deals only. Conditions on agreement, which the card can affect.',
    'buyer_first_offer_position': 'First own buyer offer x: (b-x)/(b-s). Undefined without a buyer offer; no clipping.',
    'buyer_average_concession': 'Mean (later-earlier)/(b-s) over consecutive own buyer offers. Signed, unclipped; undefined below two offers.',
    'buyer_mandate_violation': 'Deal above b, including an accepted own offer. Zero for impasses; exclusions unavailable.',
    'seller_mandate_violation': 'Deal below s. Zero for impasses; exclusions unavailable.',
}


def buyer_offer_outcomes(turns: Iterable[TranscriptTurn], *, buyer_max: int, seller_min: int) -> dict:
    """Ignore acceptance prices; measure only consecutive offers made by the buyer."""
    zone = buyer_max - seller_min
    if zone <= 0:
        raise ValueError('Buyer-offer outcomes require a positive zone of agreement.')
    prices = [int(turn.price) for turn in turns if turn.role == 'buyer' and turn.action == 'offer']
    return {'buyer_offer_count': len(prices),
            'buyer_first_offer_position': (buyer_max - prices[0]) / zone if prices else None,
            'buyer_average_concession': sum((later - earlier) / zone for earlier, later in zip(prices, prices[1:])) / (len(prices) - 1)
            if len(prices) >= 2 else None}
