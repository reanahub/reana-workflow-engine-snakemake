# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2021, 2022, 2023, 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Snakemake runner."""

import os
import logging
from pathlib import Path

from snakemake.api import SnakemakeApi
from snakemake.settings.types import (
    ConfigSettings,
    DAGSettings,
    DeploymentSettings,
    OutputSettings,
    ResourceSettings,
    StorageSettings,
    WorkflowSettings,
)

from snakemake_interface_executor_plugins.registry import ExecutorPluginRegistry
from snakemake_interface_report_plugins.registry import ReportPluginRegistry
from snakemake_interface_report_plugins.settings import (
    ReportSettingsBase,
)
from snakemake_interface_common.exceptions import WorkflowError

from reana_workflow_engine_snakemake.config import (
    LOGGING_MODULE,
    SNAKEMAKE_MAX_PARALLEL_JOBS,
    DEFAULT_SNAKEMAKE_REPORT_FILENAME,
)

from reana_workflow_engine_snakemake import executor as reana_executor

log = logging.getLogger(LOGGING_MODULE)


my_registry = ExecutorPluginRegistry()
my_registry.register_plugin("reana", reana_executor)


def _generate_report(dag_api, workflow_workspace, report_file_name):
    """Generate HTML report."""
    from snakemake.report import html_reporter

    registry = ReportPluginRegistry()
    registry.register_plugin("html", html_reporter)
    report_plugin = registry.get_plugin("html")

    report_args = ReportSettingsBase()
    report_args.report_html_path = Path(workflow_workspace) / report_file_name
    report_args.report_html_stylesheet_path = None

    report_settings = report_plugin.get_settings(args=report_args)
    dag_api.create_report(reporter="html", report_settings=report_settings)


def run_jobs(
    workflow_workspace,
    workflow_file,
    workflow_parameters,
    operational_options={},
):
    """Run Snakemake jobs using custom REANA executor."""
    workflow_file_path = os.path.join(workflow_workspace, workflow_file)
    with SnakemakeApi(
        OutputSettings(
            printshellcmds=True,
        )
    ) as snakemake_api:
        try:
            workflow_api = snakemake_api.workflow(
                resource_settings=ResourceSettings(nodes=SNAKEMAKE_MAX_PARALLEL_JOBS),
                config_settings=ConfigSettings(config=workflow_parameters),
                storage_settings=StorageSettings(),
                storage_provider_settings=dict(),
                workflow_settings=WorkflowSettings(),
                deployment_settings=DeploymentSettings(),
                snakefile=Path(workflow_file_path),
                workdir=Path(workflow_workspace),
            )
            dag_api = workflow_api.dag(
                dag_settings=DAGSettings(),
            )

            dag_api.execute_workflow(
                executor="reana",
            )

            report_file_name = operational_options.get(
                "report", DEFAULT_SNAKEMAKE_REPORT_FILENAME
            )
            _generate_report(dag_api, workflow_workspace, report_file_name)
            return True

        except WorkflowError as e:
            snakemake_api.print_exception(e)
            return False
