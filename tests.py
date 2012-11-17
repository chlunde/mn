#!/usr/bin/env python
import random
import unittest

from metan import d

class CommonMatcherTest(object):
    def test_matching(self):
	self.assertTrue(self.score('a', 'a') > 0)

    def test_matching_prefix(self):
	self.assertTrue(self.score('a', 'ab') > 0)

    def test_matching_suffix(self):
	self.assertTrue(self.score('a', 'ab') > 0)

    def test_matching_infix(self):
	self.assertTrue(self.score('a', 'bab') > 0)

    def test_matching_string(self):
	self.assertTrue(self.score('abc', 'babcx') > 0)

    def test_matching_string_many_skips(self):
	# Seed so we get the same results each run
	r = random.Random()
	r.seed(0)

	s = 'abcabcabc'
	for a in range(1000):
	    # Insert a random character at a random offset
	    offset = r.randint(0, len(s))
	    char = chr(r.randint(32, 126))
	    if char in 'abc':
		continue

	    l = list(s) # split to list ['a','b','c']
	    l.insert(offset, char)
	    s = "".join(l) # convert back to string

	    # Check that we still match it
	    self.assertTrue(self.score('abcabcabc', s) > 0)

    def test_matching_case(self):
	self.assertTrue(self.score('A', 'a') > 0)
	self.assertTrue(self.score('a', 'A') > 0)

    def test_nonmatching(self):
	self.assertTrue(self.score('b', 'a') in (0.0, None))

    def test_nonmatching_leftovercharacters(self):
	self.assertTrue(self.score('ba', 'ab') in (0.0, None))

    def test_scoring_skips(self):
	self.assertTrue(self.score('ab', 'axb') < self.score('ab', 'ab'))

    def test_scoring_skips_distance(self):
	self.assertTrue(self.score('ab', 'axxb') < self.score('ab', 'axb'))

    def test_scoring_leading(self):
	self.assertTrue(self.score('ab', 'xab') < self.score('ab', 'ab'))

    def test_scoring_trailing(self):
	self.assertTrue(self.score('ab', 'abx') < self.score('ab', 'ab'))

    def test_scoring_skips_natural_break_slash(self):
	self.assertTrue(self.score('pathfile', 'pathFOOfile') < self.score('pathfile', 'path/x/file'))

    def test_scoring_skips_natural_break_dot(self):
	self.assertTrue(self.score('projectnamefpy', 'projectnamexfxpyfoo') < self.score('projectnamefpy', 'projectnamexxxfx.py'))

def score_or_none(matcher):
    """Helper wrapper for tests; returns the score - if any, or noen if no score"""
    def f(a, b):
	result = matcher(a, b)
	if result:
	    return result['score']
	return None
    return f

class MatcherDTest(CommonMatcherTest, unittest.TestCase):
    def setUp(self):
	self.match = d
	self.score = score_or_none(d)

if __name__ == '__main__':
    unittest.main()
