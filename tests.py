#!/usr/bin/env python
import random
import unittest

from metan import MatcherA, MatcherB

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
	self.assertEquals(self.score('b', 'a'), 0)

    # def test_nonmatching_leftovercharacters(self):
	# self.assertEquals(self.score('ba', 'ab'), 0)

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

class MatcherATest(CommonMatcherTest, unittest.TestCase):
    def setUp(self):
	self.score = lambda a, b: MatcherA([b]).d(a, b)[1]

class MatcherBTest(CommonMatcherTest, unittest.TestCase):
    def setUp(self):
	def score(pattern, choice):
	    m = MatcherB([choice]).match(pattern)
	    if len(m):
		return m[0][0]
	    else:
		return 0
	self.score = score

if __name__ == '__main__':
    unittest.main()
