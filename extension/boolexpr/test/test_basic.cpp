/*
** Filename: test_basic.cpp
**
** Test basic Boolean expression creation and deletion
*/


#include "boolexprtest.hpp"


TEST_F(BoolExprTest, CreateOperators)
{
    BoolExpr *ys[4] = {xns[0], xs[1], xns[2], xs[3]};

    ops[0] = Or(4, ys);
    ops[1] = Nor(4, ys);
    ops[2] = And(4, ys);
    ops[3] = Nand(4, ys);
    ops[4] = Xor(4, ys);
    ops[5] = Xnor(4, ys);
    ops[6] = Equal(4, ys);
    ops[7] = Unequal(4, ys);

    ops[8] = OrN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[9] = NorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[10] = AndN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[11] = NandN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[12] = XorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[13] = XnorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[14] = EqualN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[15] = UnequalN(4, xns[0], xs[1], xns[2], xs[3]);

    ops[16] = Not(ops[0]);
    ops[17] = Implies(xns[0], xs[1]);
    ops[18] = ITE(xns[0], xs[1], xns[2]);
}


TEST_F(BoolExprTest, DegenerateForms)
{
    ops[0] = OrN(0);
    EXPECT_EQ(ops[0], &Zero);

    ops[1] = OrN(1, xs[0]);
    EXPECT_EQ(ops[1], xs[0]);

    ops[2] = NorN(0);
    EXPECT_EQ(ops[2], &One);

    ops[3] = NorN(1, xs[0]);
    EXPECT_EQ(ops[3], xns[0]);

    ops[4] = AndN(0);
    EXPECT_EQ(ops[4], &One);

    ops[5] = AndN(1, xs[0]);
    EXPECT_EQ(ops[5], xs[0]);

    ops[6] = NandN(0);
    EXPECT_EQ(ops[6], &Zero);

    ops[7] = NandN(1, xs[0]);
    EXPECT_EQ(ops[7], xns[0]);

    ops[8] = XorN(0);
    EXPECT_EQ(ops[8], &Zero);

    ops[9] = XorN(1, xs[0]);
    EXPECT_EQ(ops[9], xs[0]);

    ops[10] = XnorN(0);
    EXPECT_EQ(ops[10], &One);

    ops[11] = XnorN(1, xs[0]);
    EXPECT_EQ(ops[11], xns[0]);

    ops[12] = EqualN(0);
    EXPECT_EQ(ops[12], &One);

    ops[13] = EqualN(1, xs[0]);
    EXPECT_EQ(ops[13], &One);

    ops[14] = UnequalN(0);
    EXPECT_EQ(ops[14], &Zero);

    ops[15] = UnequalN(1, xs[0]);
    EXPECT_EQ(ops[15], &Zero);

    ops[16] = Not(&Zero);
    EXPECT_EQ(ops[16], &One);

    ops[17] = Not(&One);
    EXPECT_EQ(ops[17], &Zero);

    ops[18] = Not(&Logical);
    EXPECT_EQ(ops[18], &Logical);

    ops[19] = Not(&Illogical);
    EXPECT_EQ(ops[19], &Illogical);

    ops[20] = Not(xs[0]);
    EXPECT_EQ(ops[20], xns[0]);

    ops[21] = Not(xns[0]);
    EXPECT_EQ(ops[21], xs[0]);

    ops[22] = NorN(2, xs[0], xs[1]);
    ops[23] = Not(ops[22]);
    EXPECT_EQ(ops[23], ops[22]->data.xs->items[0]);
}


TEST_F(BoolExprTest, Iterate)
{
    int i;
    BoolExprIter *it;
    BoolExpr *ex;

    ops[0] = AndN(2, xs[0], xs[1]);
    ops[1] = XorN(2, xs[2], xs[3]);
    ops[2] = EqualN(2, xs[4], xs[5]);
    ops[3] = Implies(xs[6], xs[7]);
    ops[4] = ITE(xs[8], xs[9], xs[10]);
    ops[5] = NorN(5, ops[0], ops[1], ops[2], ops[3], ops[4]);

    BoolExpr *expected[] = {
        xs[0], xs[1], ops[0],
        xs[2], xs[3], ops[1],
        xs[4], xs[5], ops[2],
        xs[6], xs[7], ops[3],
        xs[8], xs[9], xs[10], ops[4],
        ops[5]->data.xs->items[0],
        ops[5],
    };

    it = BoolExprIter_New(ops[5]);
    for (i = 0; !it->done; ++i) {
        ex = BoolExprIter_Next(it);
        EXPECT_EQ(ex, expected[i]);
    }
    BoolExprIter_Del(it);

    EXPECT_EQ(i, 18);
}


TEST_F(BoolExprTest, Properties)
{
    ops[0] = AndN(2, xs[0], xs[1]);
    ops[1] = XorN(2, xs[2], xs[3]);
    ops[2] = EqualN(2, xs[4], xs[5]);
    ops[3] = Implies(xs[6], xs[7]);
    ops[4] = ITE(xs[8], xs[9], xs[10]);
    ops[5] = NorN(5, ops[0], ops[1], ops[2], ops[3], ops[4]);

    EXPECT_EQ(BoolExpr_Depth(xs[0]), 0);
    EXPECT_EQ(BoolExpr_Depth(ops[0]), 1);
    EXPECT_EQ(BoolExpr_Depth(ops[1]), 1);
    EXPECT_EQ(BoolExpr_Depth(ops[2]), 1);
    EXPECT_EQ(BoolExpr_Depth(ops[3]), 1);
    EXPECT_EQ(BoolExpr_Depth(ops[4]), 1);
    EXPECT_EQ(BoolExpr_Depth(ops[5]), 3);

    EXPECT_EQ(BoolExpr_Size(xs[0]), 1);
    EXPECT_EQ(BoolExpr_Size(ops[0]), 3);
    EXPECT_EQ(BoolExpr_Size(ops[1]), 3);
    EXPECT_EQ(BoolExpr_Size(ops[2]), 3);
    EXPECT_EQ(BoolExpr_Size(ops[3]), 3);
    EXPECT_EQ(BoolExpr_Size(ops[4]), 4);
    EXPECT_EQ(BoolExpr_Size(ops[5]), 18);

    EXPECT_EQ(BoolExpr_AtomCount(xs[0]), 1);
    EXPECT_EQ(BoolExpr_AtomCount(ops[0]), 2);
    EXPECT_EQ(BoolExpr_AtomCount(ops[1]), 2);
    EXPECT_EQ(BoolExpr_AtomCount(ops[2]), 2);
    EXPECT_EQ(BoolExpr_AtomCount(ops[3]), 2);
    EXPECT_EQ(BoolExpr_AtomCount(ops[4]), 3);
    EXPECT_EQ(BoolExpr_AtomCount(ops[5]), 11);

    EXPECT_EQ(BoolExpr_OpCount(xs[0]), 0);
    EXPECT_EQ(BoolExpr_OpCount(ops[0]), 1);
    EXPECT_EQ(BoolExpr_OpCount(ops[1]), 1);
    EXPECT_EQ(BoolExpr_OpCount(ops[2]), 1);
    EXPECT_EQ(BoolExpr_OpCount(ops[3]), 1);
    EXPECT_EQ(BoolExpr_OpCount(ops[4]), 1);
    EXPECT_EQ(BoolExpr_OpCount(ops[5]), 7);
}


TEST_F(BoolExprTest, IsCnfDnf)
{
    // Constants
    EXPECT_TRUE(BoolExpr_IsDNF(&Zero));
    EXPECT_FALSE(BoolExpr_IsDNF(&One));
    EXPECT_FALSE(BoolExpr_IsCNF(&Zero));
    EXPECT_TRUE(BoolExpr_IsCNF(&One));

    // Literals
    EXPECT_TRUE(BoolExpr_IsDNF(xns[0]));
    EXPECT_TRUE(BoolExpr_IsDNF(xs[0]));
    EXPECT_TRUE(BoolExpr_IsCNF(xns[0]));
    EXPECT_TRUE(BoolExpr_IsCNF(xs[0]));

    // OR clause
    ops[0] = OrN(2, xns[0], xs[1], xns[2], xs[3]);
    EXPECT_FALSE(BoolExpr_IsDNF(ops[0])); // not simple
    EXPECT_FALSE(BoolExpr_IsCNF(ops[0])); // not simple
    ops[1] = BoolExpr_Simplify(ops[0]);
    EXPECT_TRUE(BoolExpr_IsDNF(ops[1]));
    EXPECT_TRUE(BoolExpr_IsCNF(ops[1]));

    // AND clause
    ops[2] = AndN(2, xns[0], xs[1], xns[2], xs[3]);
    EXPECT_FALSE(BoolExpr_IsDNF(ops[2])); // not simple
    EXPECT_FALSE(BoolExpr_IsCNF(ops[2])); // not simple
    ops[3] = BoolExpr_Simplify(ops[2]);
    EXPECT_TRUE(BoolExpr_IsDNF(ops[3]));
    EXPECT_TRUE(BoolExpr_IsCNF(ops[3]));

    // a | b | (w & x) | (y & z)
    ops[4] = AndN(2, xs[2], xs[3]);
    ops[5] = AndN(2, xs[4], xs[5]);
    ops[6] = OrN(4, xs[0], xs[1], ops[4], ops[5]);
    ops[7] = BoolExpr_Simplify(ops[6]);
    EXPECT_TRUE(BoolExpr_IsDNF(ops[7]));
    EXPECT_FALSE(BoolExpr_IsCNF(ops[7]));

    // a & b & (w | x) & (y | z)
    ops[8] = OrN(2, xs[2], xs[3]);
    ops[9] = OrN(2, xs[4], xs[5]);
    ops[10] = AndN(4, xs[0], xs[1], ops[8], ops[9]);
    ops[11] = BoolExpr_Simplify(ops[10]);
    EXPECT_FALSE(BoolExpr_IsDNF(ops[11]));
    EXPECT_TRUE(BoolExpr_IsCNF(ops[11]));

    // a | (b & c) | ((w | x) & (y | z))
    ops[12] = AndN(2, xs[1], xs[2]);
    ops[13] = OrN(2, xs[3], xs[4]);
    ops[14] = OrN(2, xs[5], xs[6]);
    ops[15] = AndN(2, ops[13], ops[14]);
    ops[16] = OrN(3, xs[0], ops[12], ops[15]);
    ops[17] = BoolExpr_Simplify(ops[16]);
    EXPECT_FALSE(BoolExpr_IsDNF(ops[17]));

    // a & (b | c) & ((w & x) | (y & z))
    ops[18] = OrN(2, xs[1], xs[2]);
    ops[19] = AndN(2, xs[3], xs[4]);
    ops[20] = AndN(2, xs[5], xs[6]);
    ops[21] = OrN(2, ops[19], ops[20]);
    ops[22] = AndN(3, xs[0], ops[18], ops[21]);
    ops[23] = BoolExpr_Simplify(ops[22]);
    EXPECT_FALSE(BoolExpr_IsCNF(ops[23]));

    // XOR is neither CNF or DNF
    ops[24] = XorN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_FALSE(BoolExpr_IsCNF(ops[24]));
    EXPECT_FALSE(BoolExpr_IsDNF(ops[24]));
}

