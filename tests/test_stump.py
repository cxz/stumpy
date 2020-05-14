import numpy as np
import numpy.testing as npt
import pandas as pd
from stumpy import stump, core
import pytest
import utils


test_data = [
    (
        np.array([9, 8100, -60, 7], dtype=np.float64),
        np.array([584, -11, 23, 79, 1001, 0, -19], dtype=np.float64),
    ),
    (
        np.random.uniform(-1000, 1000, [8]).astype(np.float64),
        np.random.uniform(-1000, 1000, [64]).astype(np.float64),
    ),
]

substitution_locations = [(slice(0, 0), 0, -1, slice(1, 3), [0, 3])]
substitution_values = [np.nan, np.inf]


@pytest.mark.parametrize("T_A, T_B", test_data)
def test_stump_self_join(T_A, T_B):
    m = 3
    zone = int(np.ceil(m / 4))
    left = utils.naive_stamp(T_B, m, exclusion_zone=zone)
    right = stump(T_B, m, ignore_trivial=True)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left, right)

    right = stump(pd.Series(T_B), m, ignore_trivial=True)
    utils.replace_inf(right)
    npt.assert_almost_equal(left, right)


@pytest.mark.parametrize("T_A, T_B", test_data)
def test_stump_A_B_join(T_A, T_B):
    m = 3
    left = utils.naive_stamp(T_A, m, T_B=T_B)
    right = stump(T_A, m, T_B, ignore_trivial=False)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left, right)

    right = stump(pd.Series(T_A), m, pd.Series(T_B), ignore_trivial=False)
    utils.replace_inf(right)
    npt.assert_almost_equal(left, right)


def test_stump_constant_subsequence_self_join():
    T_A = np.concatenate((np.zeros(20, dtype=np.float64), np.ones(5, dtype=np.float64)))
    m = 3
    zone = int(np.ceil(m / 4))
    left = utils.naive_stamp(T_A, m, exclusion_zone=zone)
    right = stump(T_A, m, ignore_trivial=True)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    right = stump(pd.Series(T_A), m, ignore_trivial=True)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices


def test_stump_one_constant_subsequence_A_B_join():
    T_A = np.random.rand(20)
    T_B = np.concatenate((np.zeros(20, dtype=np.float64), np.ones(5, dtype=np.float64)))
    m = 3
    left = utils.naive_stamp(T_A, m, T_B=T_B)
    right = stump(T_A, m, T_B, ignore_trivial=False)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    right = stump(pd.Series(T_A), m, pd.Series(T_B), ignore_trivial=False)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    # Swap inputs
    left = utils.naive_stamp(T_B, m, T_B=T_A)
    right = stump(T_B, m, T_A, ignore_trivial=False)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices


def test_stump_two_constant_subsequences_A_B_join():
    T_A = np.concatenate(
        (np.zeros(10, dtype=np.float64), np.ones(10, dtype=np.float64))
    )
    T_B = np.concatenate((np.zeros(20, dtype=np.float64), np.ones(5, dtype=np.float64)))
    m = 3
    left = utils.naive_stamp(T_A, m, T_B=T_B)
    right = stump(T_A, m, T_B, ignore_trivial=False)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    right = stump(pd.Series(T_A), m, pd.Series(T_B), ignore_trivial=False)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    # Swap inputs
    left = utils.naive_stamp(T_B, m, T_B=T_A)
    right = stump(T_B, m, T_A, ignore_trivial=False)
    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices

    right = stump(pd.Series(T_B), m, pd.Series(T_A), ignore_trivial=False)
    utils.replace_inf(right)
    npt.assert_almost_equal(left[:, 0], right[:, 0])  # ignore indices


@pytest.mark.parametrize("T_A, T_B", test_data)
@pytest.mark.parametrize("substitute_B", substitution_values)
@pytest.mark.parametrize("substitution_locations", substitution_locations)
def test_stump_nan_inf_self_join(T_A, T_B, substitute_B, substitution_locations):
    m = 3

    T_B_sub = T_B.copy()

    for substitution_location_B in substitution_locations:
        T_B_sub[:] = T_B[:]
        T_B_sub[substitution_location_B] = substitute_B

        zone = int(np.ceil(m / 4))
        left = utils.naive_stamp(T_B_sub, m, exclusion_zone=zone)
        right = stump(T_B_sub, m, ignore_trivial=True)
        utils.replace_inf(left)
        utils.replace_inf(right)
        npt.assert_almost_equal(left, right)

        right = stump(pd.Series(T_B_sub), m, ignore_trivial=True)
        utils.replace_inf(right)
        npt.assert_almost_equal(left, right)


@pytest.mark.parametrize("T_A, T_B", test_data)
@pytest.mark.parametrize("substitute_A", substitution_values)
@pytest.mark.parametrize("substitute_B", substitution_values)
@pytest.mark.parametrize("substitution_locations", substitution_locations)
def test_stump_nan_inf_A_B_join(
    T_A, T_B, substitute_A, substitute_B, substitution_locations
):
    m = 3

    T_A_sub = T_A.copy()
    T_B_sub = T_B.copy()

    for substitution_location_B in substitution_locations:
        for substitution_location_A in substitution_locations:
            T_A_sub[:] = T_A[:]
            T_B_sub[:] = T_B[:]
            T_A_sub[substitution_location_A] = substitute_A
            T_B_sub[substitution_location_B] = substitute_B

            left = utils.naive_stamp(T_A_sub, m, T_B=T_B_sub)
            right = stump(T_A_sub, m, T_B_sub, ignore_trivial=False)
            utils.replace_inf(left)
            utils.replace_inf(right)
            npt.assert_almost_equal(left, right)

            right = stump(
                pd.Series(T_A_sub), m, pd.Series(T_B_sub), ignore_trivial=False
            )
            utils.replace_inf(right)
            npt.assert_almost_equal(left, right)


def test_stump_nan_zero_mean_self_join():
    T = np.array([-1, 0, 1, np.inf, 1, 0, -1])
    m = 3

    zone = int(np.ceil(m / 4))
    left = utils.naive_stamp(T, m, exclusion_zone=zone)
    right = stump(T, m, ignore_trivial=True)

    utils.replace_inf(left)
    utils.replace_inf(right)
    npt.assert_almost_equal(left, right)
