# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2026 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Snakemake executor tests."""

import json
from unittest.mock import Mock, patch

import pytest
from reana_workflow_engine_snakemake.config import RunStatus
from reana_workflow_engine_snakemake.executor import Executor


class MockJob:
    """Mock job object for testing."""

    def __init__(self, name, wildcards=None):
        self.name = name
        self.wildcards = wildcards if wildcards is not None else {}


def make_shell_job():
    """Build a minimal shell job accepted by Executor.run_job."""
    job = Mock()
    job.name = "calculate"
    job.shellcmd = "echo hello"
    job.is_shell = True
    job.is_run = False
    job.container_img_url = "docker://docker.io/library/ubuntu:24.04"
    job.resources = {}
    job.wildcards = {}
    return job


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


@patch("reana_workflow_engine_snakemake.executor.publish_workflow_start")
def test_run_job_reports_submission_failure(publish_workflow_start):
    """Test that an RJC submission failure marks the job and workflow failed."""
    executor = Executor.__new__(Executor)
    executor.publisher = Mock()
    executor.rjc_api_client = Mock()
    executor.rjc_api_client.submit.side_effect = RuntimeError("image rejected")
    executor.report_job_error = Mock()
    executor.report_job_submission = Mock()
    job = make_shell_job()

    with patch(
        "reana_workflow_engine_snakemake.executor.publish_job_submission"
    ) as publish_job_submission:
        executor.run_job(job)

    executor.report_job_error.assert_called_once()
    executor.report_job_submission.assert_not_called()
    publish_job_submission.assert_not_called()
    executor.publisher.publish_workflow_status.assert_called_once_with(
        "default",
        RunStatus.failed.value,
        message="Job submission failed for calculate: image rejected",
    )


@patch("reana_workflow_engine_snakemake.executor.publish_workflow_start")
def test_run_job_does_not_report_publish_failure_as_submission_failure(
    publish_workflow_start,
):
    """Test that post-submit publication failures remain visible."""
    executor = Executor.__new__(Executor)
    executor.publisher = Mock()
    executor.rjc_api_client = Mock()
    executor.rjc_api_client.submit.return_value = {"job_id": "job-id"}
    executor.report_job_error = Mock()
    executor.report_job_submission = Mock()
    job = make_shell_job()

    with (
        patch(
            "reana_workflow_engine_snakemake.executor.publish_job_submission",
            side_effect=RuntimeError("publisher failed"),
        ),
        pytest.raises(RuntimeError, match="publisher failed"),
    ):
        executor.run_job(job)

    executor.report_job_error.assert_not_called()
    executor.report_job_submission.assert_not_called()


@patch("reana_workflow_engine_snakemake.executor.publish_workflow_start")
def test_run_job_does_not_report_submission_callback_failure(
    publish_workflow_start,
):
    """Test that Snakemake callback failures are not treated as RJC failures."""
    executor = Executor.__new__(Executor)
    executor.publisher = Mock()
    executor.rjc_api_client = Mock()
    executor.rjc_api_client.submit.return_value = {"job_id": "job-id"}
    executor.report_job_error = Mock()
    executor.report_job_submission = Mock(side_effect=RuntimeError("callback failed"))
    job = make_shell_job()

    with pytest.raises(RuntimeError, match="callback failed"):
        executor.run_job(job)

    executor.report_job_error.assert_not_called()


@pytest.mark.parametrize(
    "rule_secret_names,workflow_resources,expected_secret_names",
    [
        (None, {}, None),
        (None, {"secret_names": ["global"]}, ["global"]),
        ("", {"secret_names": ["global"]}, []),
        ("local", {"secret_names": ["global"]}, ["local"]),
    ],
)
@patch("reana_workflow_engine_snakemake.executor.publish_workflow_start")
def test_run_job_secret_names_resolution(
    publish_workflow_start,
    monkeypatch,
    rule_secret_names,
    workflow_resources,
    expected_secret_names,
):
    """Rule-local secret_names should override or inherit workflow defaults."""
    monkeypatch.setenv("workflow_uuid", "test-uuid")
    monkeypatch.setenv("workflow_workspace", "/workspace")
    monkeypatch.setenv("REANA_WORKFLOW_RESOURCES", json.dumps(workflow_resources))

    executor = Executor.__new__(Executor)
    executor.publisher = Mock()
    executor.rjc_api_client = Mock()
    executor.rjc_api_client.submit.return_value = {"job_id": "job-id"}
    executor.report_job_error = Mock()
    executor.report_job_submission = Mock()

    job = make_shell_job()
    if rule_secret_names is not None:
        job.resources = {"secret_names": rule_secret_names}

    with patch("reana_workflow_engine_snakemake.executor.publish_job_submission"):
        executor.run_job(job)

    assert (
        executor.rjc_api_client.submit.call_args.kwargs.get("secret_names")
        == expected_secret_names
    )
