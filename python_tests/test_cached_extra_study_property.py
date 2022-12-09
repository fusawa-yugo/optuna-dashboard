from typing import Dict
from typing import List
from unittest import TestCase
import warnings

import optuna
from optuna import create_trial
from optuna.distributions import BaseDistribution
from optuna.distributions import FloatDistribution
from optuna.exceptions import ExperimentalWarning
from optuna.trial import TrialState
from optuna_dashboard._cached_extra_study_property import _CachedExtraStudyProperty


class _CachedExtraStudyPropertySearchSpaceTestCase(TestCase):
    def setUp(self) -> None:
        optuna.logging.set_verbosity(optuna.logging.ERROR)
        warnings.simplefilter("ignore", category=ExperimentalWarning)

    def test_same_distributions(self) -> None:
        distributions: List[Dict[str, BaseDistribution]] = [
            {
                "x0": FloatDistribution(low=0, high=10),
                "x1": FloatDistribution(low=0, high=10),
            },
            {
                "x0": FloatDistribution(low=0, high=10),
                "x1": FloatDistribution(low=0, high=10),
            },
        ]
        params = [
            {
                "x0": 0.5,
                "x1": 0.5,
            },
            {
                "x0": 0.5,
                "x1": 0.5,
            },
        ]
        trials = [
            create_trial(state=TrialState.COMPLETE, value=0, distributions=d, params=p)
            for d, p in zip(distributions, params)
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)

        self.assertEqual(len(cached_extra_study_property.intersection), 2)
        self.assertEqual(len(cached_extra_study_property.union), 2)

    def test_different_distributions(self) -> None:
        distributions: List[Dict[str, BaseDistribution]] = [
            {
                "x0": FloatDistribution(low=0, high=10),
                "x1": FloatDistribution(low=0, high=10),
            },
            {
                "x0": FloatDistribution(low=0, high=5),
                "x1": FloatDistribution(low=0, high=10),
            },
        ]
        params = [
            {
                "x0": 0.5,
                "x1": 0.5,
            },
            {
                "x0": 0.5,
                "x1": 0.5,
            },
        ]
        trials = [
            create_trial(state=TrialState.COMPLETE, value=0, distributions=d, params=p)
            for d, p in zip(distributions, params)
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)

        self.assertEqual(len(cached_extra_study_property.intersection), 1)
        self.assertEqual(len(cached_extra_study_property.union), 3)

    def test_dynamic_search_space(self) -> None:
        distributions: List[Dict[str, BaseDistribution]] = [
            {
                "x0": FloatDistribution(low=0, high=10),
                "x1": FloatDistribution(low=0, high=10),
            },
            {
                "x0": FloatDistribution(low=0, high=5),
            },
            {
                "x0": FloatDistribution(low=0, high=10),
                "x1": FloatDistribution(low=0, high=10),
            },
        ]
        params = [
            {
                "x0": 0.5,
                "x1": 0.5,
            },
            {
                "x0": 0.5,
            },
            {
                "x0": 0.5,
                "x1": 0.5,
            },
        ]
        trials = [
            create_trial(state=TrialState.COMPLETE, value=0, distributions=d, params=p)
            for d, p in zip(distributions, params)
        ]

        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)

        self.assertEqual(len(cached_extra_study_property.intersection), 0)
        self.assertEqual(len(cached_extra_study_property.union), 3)

    def test_contains_failed_trials(self) -> None:
        distributions = {
            "x0": FloatDistribution(low=0, high=10),
            "x1": FloatDistribution(low=0, high=10),
        }
        params = {
            "x0": 0.5,
            "x1": 0.5,
        }
        trials = [
            create_trial(
                state=TrialState.COMPLETE, value=0, distributions=distributions, params=params
            ),
            create_trial(state=TrialState.FAIL, value=0, distributions={}, params={}),
            create_trial(
                state=TrialState.COMPLETE, value=0, distributions=distributions, params=params
            ),
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)

        self.assertEqual(len(cached_extra_study_property.intersection), 2)
        self.assertEqual(len(cached_extra_study_property.union), 2)


class _CachedExtraStudyPropertyIntermediateTestCase(TestCase):
    def setUp(self) -> None:
        optuna.logging.set_verbosity(optuna.logging.ERROR)
        warnings.simplefilter("ignore", category=ExperimentalWarning)

    def test_no_intermediate_value(self) -> None:
        intermediate_values: List[Dict] = [
            {},
            {},
        ]
        trials = [
            create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions={"x0": FloatDistribution(low=0, high=10)},
                intermediate_values=iv,
                params={"x0": 0.5},
            )
            for iv in intermediate_values
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)
        self.assertFalse(cached_extra_study_property.has_intermediate_values)

    def test_some_trials_has_no_intermediate_value(self) -> None:
        intermediate_values: List[Dict] = [
            {0: 0.3, 1: 1.2},
            {},
            {0: 0.3, 1: 1.2},
        ]
        trials = [
            create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions={"x0": FloatDistribution(low=0, high=10)},
                intermediate_values=iv,
                params={"x0": 0.5},
            )
            for iv in intermediate_values
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)
        self.assertTrue(cached_extra_study_property.has_intermediate_values)

    def test_all_trials_has_intermediate_value(self) -> None:
        intermediate_values: List[Dict] = [{0: 0.3, 1: 1.2}, {0: 0.3, 1: 1.2}]
        trials = [
            create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions={"x0": FloatDistribution(low=0, high=10)},
                intermediate_values=iv,
                params={"x0": 0.5},
            )
            for iv in intermediate_values
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)
        self.assertTrue(cached_extra_study_property.has_intermediate_values)

    def test_no_trials(self) -> None:
        trials: list = []
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)
        self.assertFalse(cached_extra_study_property.has_intermediate_values)


class _CachedExtraStudyPropertyUserAttrs(TestCase):
    def setUp(self) -> None:
        optuna.logging.set_verbosity(optuna.logging.ERROR)
        warnings.simplefilter("ignore", category=ExperimentalWarning)

    def test_contains_failed_trials(self) -> None:
        distributions = {
            "x0": FloatDistribution(low=0, high=10),
            "x1": FloatDistribution(low=0, high=10),
        }
        params = {
            "x0": 0.5,
            "x1": 0.5,
        }
        trials = [
            create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions=distributions,
                params=params,
                user_attrs={"foo": "foo"},
            ),
            create_trial(
                state=TrialState.FAIL,
                value=0,
                distributions={},
                params={},
                user_attrs={"bar": "bar"},
            ),
            create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions=distributions,
                params=params,
                user_attrs={"baz": "baz"},
            ),
        ]
        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)

        self.assertEqual(len(cached_extra_study_property.union_user_attrs), 3)

    def test_infer_sortable(self) -> None:
        user_attrs_list = [
            {"a": 1, "b": 1, "c": 1, "d": "a"},
            {"a": 2, "b": "a", "c": "a", "d": "a"},
            {"a": 3, "b": None, "c": 3, "d": "a"},
        ]
        expected = {"a": True, "b": False, "c": False, "d": False}

        trials = []
        for user_attrs in user_attrs_list:
            trials.append(create_trial(
                state=TrialState.COMPLETE,
                value=0,
                distributions={"x0": FloatDistribution(low=0, high=10), "x1": FloatDistribution(low=0, high=10)},
                params={"x0": 0.5, "x1": 0.5},
                user_attrs=user_attrs,
            ))

        cached_extra_study_property = _CachedExtraStudyProperty()
        cached_extra_study_property.update(trials)
        actual = {k: v for k, v in cached_extra_study_property.union_user_attrs}
        assert actual == expected
