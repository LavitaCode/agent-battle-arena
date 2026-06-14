"""Unit tests for ELO rating service."""
import unittest

from backend.app.services.elo_service import DEFAULT_RATING, expected, update


class EloServiceTest(unittest.TestCase):
    def test_equal_ratings_expected_score_is_half(self):
        self.assertAlmostEqual(expected(1200, 1200), 0.5)

    def test_higher_rated_player_has_higher_expectation(self):
        self.assertGreater(expected(1400, 1200), 0.5)
        self.assertLess(expected(1200, 1400), 0.5)

    def test_win_increases_winner_rating(self):
        ra, rb = update(1200.0, 1200.0, 1.0)
        self.assertGreater(ra, 1200.0)
        self.assertLess(rb, 1200.0)

    def test_loss_decreases_loser_rating(self):
        ra, rb = update(1200.0, 1200.0, 0.0)
        self.assertLess(ra, 1200.0)
        self.assertGreater(rb, 1200.0)

    def test_draw_keeps_equal_ratings_unchanged(self):
        ra, rb = update(1200.0, 1200.0, 0.5)
        self.assertAlmostEqual(ra, 1200.0, places=6)
        self.assertAlmostEqual(rb, 1200.0, places=6)

    def test_zero_sum_property(self):
        ra0, rb0 = 1300.0, 1100.0
        ra1, rb1 = update(ra0, rb0, 1.0)
        self.assertAlmostEqual(ra1 + rb1, ra0 + rb0, places=6)

    def test_draw_between_unequal_players_transfers_points(self):
        # underdog draws — should gain points; favourite should lose
        ra, rb = update(1200.0, 1400.0, 0.5)
        self.assertGreater(ra, 1200.0)
        self.assertLess(rb, 1400.0)

    def test_default_rating_constant(self):
        self.assertEqual(DEFAULT_RATING, 1200.0)
