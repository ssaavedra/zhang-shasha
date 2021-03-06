#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import unittest, os, sys, base64, itertools, random, time, copy
import copy, collections
from random import randint, seed, shuffle

from zss import compare, Node

seed(os.urandom(15))

N = 3

def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
if not hasattr(itertools, 'product'):
    setattr(itertools, 'product', product)

tree1_nodes = ['a','b','c','d','e','f']
def tree1():
    return (
        Node("f")
            .addkid(Node("d")
                .addkid(Node("a"))
                .addkid(Node("c")
                    .addkid(Node("b"))))
            .addkid(Node("e"))
        )

tree2_nodes = ['a','b','c','d','e','f']
def tree2():
    return (
        Node("a")
            .addkid(Node("c")
                .addkid(Node("d")
                    .addkid(Node("b"))
                    .addkid(Node("e"))))
            .addkid(Node("f"))
        )

tree3_nodes = ['a','b','c','d','e','f']
def tree3():
    return (
        Node("a")
            .addkid(Node("d")
                .addkid(Node("f"))
                .addkid(Node("c")
                    .addkid(Node("b"))))
            .addkid(Node("e"))
        )

tree4_nodes = ['q','b','c','d','e','f']
def tree4():
    return (
        Node("f")
            .addkid(Node("d")
                .addkid(Node("q"))
                .addkid(Node("c")
                    .addkid(Node("b"))))
            .addkid(Node("e"))
        )

def randtree(depth=2, alpha='abcdefghijklmnopqrstuvwxyz', repeat=2, width=2):
    labels = [''.join(x) for x in itertools.product(alpha, repeat=repeat)]
    shuffle(labels)
    labels = (x for x in labels)
    root = Node("root")
    p = [root]
    c = list()
    for x in xrange(depth-1):
        for y in p:
            for z in xrange(randint(1,1+width)):
                n = Node(labels.next())
                y.addkid(n)
                c.append(n)
        p = c
        c = list()
    return root

class TestTestNode(unittest.TestCase):

    def test_contains(self):
        root = tree1()
        self.assertTrue("a" in root)
        self.assertTrue("b" in root)
        self.assertTrue("c" in root)
        self.assertTrue("d" in root)
        self.assertTrue("e" in root)
        self.assertTrue("f" in root)
        self.assertFalse("q" in root)

    def test_get(self):
        root = tree1()
        self.assertEquals(root.get("a").label, "a")
        self.assertEquals(root.get("b").label, "b")
        self.assertEquals(root.get("c").label, "c")
        self.assertEquals(root.get("d").label, "d")
        self.assertEquals(root.get("e").label, "e")
        self.assertEquals(root.get("f").label, "f")

        self.assertNotEquals(root.get("a").label, "x")
        self.assertNotEquals(root.get("b").label, "x")
        self.assertNotEquals(root.get("c").label, "x")
        self.assertNotEquals(root.get("d").label, "x")
        self.assertNotEquals(root.get("e").label, "x")
        self.assertNotEquals(root.get("f").label, "x")

        self.assertEquals(root.get("x"), None)

    def test_iter(self):
        root = tree1()
        self.assertEqual(list(x.label for x in root.iter()), ['f','d','e','a','c','b'])

class TestCompare(unittest.TestCase):
    def test_distance(self):
        trees = itertools.product([tree1(), tree2(), tree3(), tree4()], repeat=2)
        for a,b in trees:
            ab = compare.distance(a,b)
            ba = compare.distance(b,a)
            #print '-----------------------------'
            #print a
            #print '------'
            #print b
            #print '------'
            #print ab, ba
            self.assertEquals(ab,ba)
            self.assertTrue((ab == 0 and a is b) or a is not b)
            #break
        trees = itertools.product([tree1(), tree2(), tree3(), tree4()], repeat=3)
        for a,b,c in trees:
            ab = compare.distance(a,b)
            bc = compare.distance(b,c)
            ac = compare.distance(a,c)
            self.assertTrue(ac <= ab + bc)
            #break

    #def test_randtree(self):
        #print randtree(5, repeat=3, width=2)

    def test_symmetry(self):
        trees = itertools.product((randtree(5, repeat=3, width=2) for x in xrange(N)), repeat=2)
        for a,b in trees:
            ab = compare.distance(a,b)
            ba = compare.distance(b,a)
            #print '-----------------------------'
            #print ab, ba
            self.assertEquals(ab, ba)

    def test_nondegenercy(self):
        trees = itertools.product((randtree(5, repeat=3, width=2) for x in xrange(N)), repeat=2)
        for a,b in trees:
            d = compare.distance(a,b)
            #print '-----------------------------'
            #print d, a is b
            self.assertTrue((d == 0 and a is b) or a is not b)

    def test_triangle_inequality(self):
        trees = itertools.product((randtree(5, repeat=3, width=2) for x in xrange(N)), (randtree(5, repeat=3, width=2) for x in xrange(N)), (randtree(5, repeat=3, width=2) for x in xrange(N)))
        for a,b,c in trees:
            #print '--------------------------------'
            ab = compare.distance(a,b)
            bc = compare.distance(b,c)
            ac = compare.distance(a,c)
            #print ab, bc, ac
            self.assertTrue(ac <= ab + bc)


    def test_labelchange(self):

        for A in (randtree(5, repeat=3, width=2) for x in xrange(N*4)):
            B = copy.deepcopy(A)
            node = random.choice([n for n in B.iter()])
            old_label = str(node.label)
            node.label = 'xty'
            assert compare.distance(A, B) == compare.strdist(old_label, node.label)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        import cProfile
        cProfile.run('unittest.main()', 'profile')
    else:
        unittest.main()

