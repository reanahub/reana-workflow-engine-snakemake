# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Snakemake executor tests."""

from reana_workflow_engine_snakemake.executor import Executor


class MockJob:
    """Mock job object for testing."""

    def __init__(self, name, wildcards=None):
        self.name = name
        self.wildcards = wildcards if wildcards is not None else {}


class TestBuildJobName:
    """Tests for Executor._build_job_name method."""

    def test_job_without_wildcards(self):
        """Test job name when no wildcards are present."""
        job = MockJob(name="calculate")
        assert Executor._build_job_name(job) == "calculate"

    def test_job_with_single_wildcard(self):
        """Test job name with a single wildcard."""
        job = MockJob(name="calculate", wildcards={"mass": "100"})
        assert Executor._build_job_name(job) == "calculate (mass=100)"

    def test_job_with_multiple_wildcards(self):
        """Test job name with multiple wildcards."""
        job = MockJob(name="process", wildcards={"sample": "A", "fileno": "22"})
        result = Executor._build_job_name(job)
        assert "process" in result
        assert "sample=A" in result
        assert "fileno=22" in result
