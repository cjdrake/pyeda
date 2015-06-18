/*
** Filename: test_basic.cpp
**
** Test basic Boolean expression creation and deletion
*/


#include "boolexprtest.hpp"


TEST_F(BoolExpr_Test, CreateOperators)
{
    BoolExpr *ys[4] = {xns[0], xs[1], xns[2], xs[3]};

    ops[0] = BX_Or(4, ys);
    ops[1] = BX_Nor(4, ys);
    ops[2] = BX_And(4, ys);
    ops[3] = BX_Nand(4, ys);
    ops[4] = BX_Xor(4, ys);
    ops[5] = BX_Xnor(4, ys);
    ops[6] = BX_Equal(4, ys);
    ops[7] = BX_Unequal(4, ys);

    ops[8] = BX_OrN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[9] = BX_NorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[10] = BX_AndN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[11] = BX_NandN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[12] = BX_XorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[13] = BX_XnorN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[14] = BX_EqualN(4, xns[0], xs[1], xns[2], xs[3]);
    ops[15] = BX_UnequalN(4, xns[0], xs[1], xns[2], xs[3]);

    ops[16] = BX_Not(ops[0]);
    ops[17] = BX_Implies(xns[0], xs[1]);
    ops[18] = BX_ITE(xns[0], xs[1], xns[2]);
}


TEST_F(BoolExpr_Test, DegenerateForms)
{
    ops[0] = BX_OrN(0);
    EXPECT_EQ(ops[0], &BX_Zero);

    ops[1] = BX_OrN(1, xs[0]);
    EXPECT_EQ(ops[1], xs[0]);

    ops[2] = BX_NorN(0);
    EXPECT_EQ(ops[2], &BX_One);

    ops[3] = BX_NorN(1, xs[0]);
    EXPECT_EQ(ops[3], xns[0]);

    ops[4] = BX_AndN(0);
    EXPECT_EQ(ops[4], &BX_One);

    ops[5] = BX_AndN(1, xs[0]);
    EXPECT_EQ(ops[5], xs[0]);

    ops[6] = BX_NandN(0);
    EXPECT_EQ(ops[6], &BX_Zero);

    ops[7] = BX_NandN(1, xs[0]);
    EXPECT_EQ(ops[7], xns[0]);

    ops[8] = BX_XorN(0);
    EXPECT_EQ(ops[8], &BX_Zero);

    ops[9] = BX_XorN(1, xs[0]);
    EXPECT_EQ(ops[9], xs[0]);

    ops[10] = BX_XnorN(0);
    EXPECT_EQ(ops[10], &BX_One);

    ops[11] = BX_XnorN(1, xs[0]);
    EXPECT_EQ(ops[11], xns[0]);

    ops[12] = BX_EqualN(0);
    EXPECT_EQ(ops[12], &BX_One);

    ops[13] = BX_EqualN(1, xs[0]);
    EXPECT_EQ(ops[13], &BX_One);

    ops[14] = BX_UnequalN(0);
    EXPECT_EQ(ops[14], &BX_Zero);

    ops[15] = BX_UnequalN(1, xs[0]);
    EXPECT_EQ(ops[15], &BX_Zero);

    ops[16] = BX_Not(&BX_Zero);
    EXPECT_EQ(ops[16], &BX_One);

    ops[17] = BX_Not(&BX_One);
    EXPECT_EQ(ops[17], &BX_Zero);

    ops[18] = BX_Not(&BX_Logical);
    EXPECT_EQ(ops[18], &BX_Logical);

    ops[19] = BX_Not(&BX_Illogical);
    EXPECT_EQ(ops[19], &BX_Illogical);

    ops[20] = BX_Not(xs[0]);
    EXPECT_EQ(ops[20], xns[0]);

    ops[21] = BX_Not(xns[0]);
    EXPECT_EQ(ops[21], xs[0]);

    ops[22] = BX_NorN(2, xs[0], xs[1]);
    ops[23] = BX_Not(ops[22]);
    EXPECT_EQ(ops[23], ops[22]->data.xs->items[0]);
}


TEST_F(BoolExpr_Test, Iterate)
{

    ops[0] = BX_AndN(2, xs[0], xs[1]);
    ops[1] = BX_XorN(2, xs[2], xs[3]);
    ops[2] = BX_EqualN(2, xs[4], xs[5]);
    ops[3] = BX_Implies(xs[6], xs[7]);
    ops[4] = BX_ITE(xs[8], xs[9], xs[10]);
    ops[5] = BX_NorN(5, ops[0], ops[1], ops[2], ops[3], ops[4]);

    size_t count = 0;
    struct BX_Iter *it;

    struct BoolExpr *exp0[] = {xs[0]};

    it = BX_Iter_New(xs[0]);
    for (count = 0; !it->done; ++count) {
        EXPECT_EQ(it->item, exp0[0]);
        BX_Iter_Next(it);
    }
    BX_Iter_Del(it);
    EXPECT_EQ(count, 1);

    struct BoolExpr *exp1[] = {xs[0], xs[1], ops[0]};

    it = BX_Iter_New(ops[0]);
    for (count = 0; !it->done; ++count) {
        EXPECT_EQ(it->item, exp1[count]);
        BX_Iter_Next(it);
    }
    BX_Iter_Del(it);
    EXPECT_EQ(count, 3);

    struct BoolExpr *exp2[] = {
        xs[0], xs[1], ops[0],
        xs[2], xs[3], ops[1],
        xs[4], xs[5], ops[2],
        xs[6], xs[7], ops[3],
        xs[8], xs[9], xs[10], ops[4],
        ops[5]->data.xs->items[0],
        ops[5],
    };

    it = BX_Iter_New(ops[5]);
    for (count = 0; !it->done; ++count) {
        EXPECT_EQ(it->item, exp2[count]);
        BX_Iter_Next(it);
    }

    EXPECT_EQ(it->item, (struct BoolExpr *) NULL);

    /* Should have no effect */
    BX_Iter_Next(it);
    BX_Iter_Next(it);
    BX_Iter_Next(it);
    BX_Iter_Next(it);

    EXPECT_EQ(it->item, (struct BoolExpr *) NULL);

    BX_Iter_Del(it);

    EXPECT_EQ(count, 18);
}


TEST_F(BoolExpr_Test, Properties)
{
    ops[0] = BX_AndN(2, xs[0], xns[1]);
    ops[1] = BX_XorN(2, xs[2], xns[3]);
    ops[2] = BX_EqualN(2, xs[4], xns[5]);
    ops[3] = BX_Implies(xs[6], xns[7]);
    ops[4] = BX_ITE(xs[8], xns[9], xs[10]);
    ops[5] = BX_NorN(5, ops[0], ops[1], ops[2], ops[3], ops[4]);

    EXPECT_EQ(BX_Depth(xs[0]), 0);
    EXPECT_EQ(BX_Depth(ops[0]), 1);
    EXPECT_EQ(BX_Depth(ops[1]), 1);
    EXPECT_EQ(BX_Depth(ops[2]), 1);
    EXPECT_EQ(BX_Depth(ops[3]), 1);
    EXPECT_EQ(BX_Depth(ops[4]), 1);
    EXPECT_EQ(BX_Depth(ops[5]), 3);

    EXPECT_EQ(BX_Size(xs[0]), 1);
    EXPECT_EQ(BX_Size(ops[0]), 3);
    EXPECT_EQ(BX_Size(ops[1]), 3);
    EXPECT_EQ(BX_Size(ops[2]), 3);
    EXPECT_EQ(BX_Size(ops[3]), 3);
    EXPECT_EQ(BX_Size(ops[4]), 4);
    EXPECT_EQ(BX_Size(ops[5]), 18);

    EXPECT_EQ(BX_AtomCount(xs[0]), 1);
    EXPECT_EQ(BX_AtomCount(ops[0]), 2);
    EXPECT_EQ(BX_AtomCount(ops[1]), 2);
    EXPECT_EQ(BX_AtomCount(ops[2]), 2);
    EXPECT_EQ(BX_AtomCount(ops[3]), 2);
    EXPECT_EQ(BX_AtomCount(ops[4]), 3);
    EXPECT_EQ(BX_AtomCount(ops[5]), 11);

    EXPECT_EQ(BX_OpCount(xs[0]), 0);
    EXPECT_EQ(BX_OpCount(ops[0]), 1);
    EXPECT_EQ(BX_OpCount(ops[1]), 1);
    EXPECT_EQ(BX_OpCount(ops[2]), 1);
    EXPECT_EQ(BX_OpCount(ops[3]), 1);
    EXPECT_EQ(BX_OpCount(ops[4]), 1);
    EXPECT_EQ(BX_OpCount(ops[5]), 7);

    struct BX_Set *s = BX_Set_New();
    for (int i = 0; i <= 10; ++i)
        BX_Set_Insert(s, xs[i]);
    struct BX_Set *t = BX_Support(ops[5]);

    struct BX_Set *u = BX_Support(&BX_Zero);
    EXPECT_EQ(u->length, 0);

    struct BX_Set *v = BX_Support(&BX_One);
    EXPECT_EQ(v->length, 0);

    EXPECT_TRUE(BX_Set_EQ(s, t));

    BX_Set_Del(s);
    BX_Set_Del(t);
    BX_Set_Del(u);
    BX_Set_Del(v);
}


TEST_F(BoolExpr_Test, IsCnfDnf)
{
    // Constants
    EXPECT_TRUE(BX_IsDNF(&BX_Zero));
    EXPECT_FALSE(BX_IsDNF(&BX_One));
    EXPECT_FALSE(BX_IsCNF(&BX_Zero));
    EXPECT_TRUE(BX_IsCNF(&BX_One));

    // Literals
    EXPECT_TRUE(BX_IsDNF(xns[0]));
    EXPECT_TRUE(BX_IsDNF(xs[0]));
    EXPECT_TRUE(BX_IsCNF(xns[0]));
    EXPECT_TRUE(BX_IsCNF(xs[0]));

    // OR clause
    ops[0] = BX_OrN(4, xns[0], xs[1], xns[2], xs[3]);
    EXPECT_TRUE(BX_IsDNF(ops[0]));
    EXPECT_TRUE(BX_IsCNF(ops[0]));
    ops[1] = BX_Simplify(ops[0]);
    EXPECT_TRUE(BX_IsDNF(ops[1]));
    EXPECT_TRUE(BX_IsCNF(ops[1]));

    // AND clause
    ops[2] = BX_AndN(4, xns[0], xs[1], xns[2], xs[3]);
    EXPECT_TRUE(BX_IsDNF(ops[2]));
    EXPECT_TRUE(BX_IsCNF(ops[2]));
    ops[3] = BX_Simplify(ops[2]);
    EXPECT_TRUE(BX_IsDNF(ops[3]));
    EXPECT_TRUE(BX_IsCNF(ops[3]));

    // a | b | (w & x) | (y & z)
    ops[4] = BX_AndN(2, xs[2], xs[3]);
    ops[5] = BX_AndN(2, xs[4], xs[5]);
    ops[6] = BX_OrN(4, xs[0], xs[1], ops[4], ops[5]);
    ops[7] = BX_Simplify(ops[6]);
    EXPECT_TRUE(BX_IsDNF(ops[7]));
    EXPECT_FALSE(BX_IsCNF(ops[7]));

    // a & b & (w | x) & (y | z)
    ops[8] = BX_OrN(2, xs[2], xs[3]);
    ops[9] = BX_OrN(2, xs[4], xs[5]);
    ops[10] = BX_AndN(4, xs[0], xs[1], ops[8], ops[9]);
    ops[11] = BX_Simplify(ops[10]);
    EXPECT_FALSE(BX_IsDNF(ops[11]));
    EXPECT_TRUE(BX_IsCNF(ops[11]));

    // a | (b & c) | ((w | x) & (y | z))
    ops[12] = BX_AndN(2, xs[1], xs[2]);
    ops[13] = BX_OrN(2, xs[3], xs[4]);
    ops[14] = BX_OrN(2, xs[5], xs[6]);
    ops[15] = BX_AndN(2, ops[13], ops[14]);
    ops[16] = BX_OrN(3, xs[0], ops[12], ops[15]);
    ops[17] = BX_Simplify(ops[16]);
    EXPECT_FALSE(BX_IsDNF(ops[17]));

    // a & (b | c) & ((w & x) | (y & z))
    ops[18] = BX_OrN(2, xs[1], xs[2]);
    ops[19] = BX_AndN(2, xs[3], xs[4]);
    ops[20] = BX_AndN(2, xs[5], xs[6]);
    ops[21] = BX_OrN(2, ops[19], ops[20]);
    ops[22] = BX_AndN(3, xs[0], ops[18], ops[21]);
    ops[23] = BX_Simplify(ops[22]);
    EXPECT_FALSE(BX_IsCNF(ops[23]));

    // XOR is neither CNF or DNF
    ops[24] = BX_XorN(4, xs[0], xs[1], xs[2], xs[3]);
    EXPECT_FALSE(BX_IsCNF(ops[24]));
    EXPECT_FALSE(BX_IsDNF(ops[24]));
}

