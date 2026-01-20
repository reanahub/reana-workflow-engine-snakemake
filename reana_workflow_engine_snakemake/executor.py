# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Snakemake executor."""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Generator, Optional

from bravado.exception import HTTPNotFound
from reana_commons.config import REANA_DEFAULT_SNAKEMAKE_ENV_IMAGE
from reana_commons.utils import build_progress_message

from reana_commons.api_client import JobControllerAPIClient
from reana_commons.publisher import WorkflowStatusPublisher

from snakemake_interface_executor_plugins.executors.base import SubmittedJobInfo
from snakemake_interface_executor_plugins.executors.remote import RemoteExecutor
from snakemake_interface_executor_plugins.settings import (
    CommonSettings,
)
from snakemake_interface_executor_plugins.jobs import (
    JobExecutorInterface,
)
from snakemake_interface_common.exceptions import WorkflowError

from reana_workflow_engine_snakemake.config import (
    LOGGING_MODULE,
    MOUNT_CVMFS,
    WORKFLOW_KERBEROS,
    POLL_JOBS_STATUS_SLEEP_IN_SECONDS,
    JobStatus,
    RunStatus,
)
from reana_workflow_engine_snakemake.utils import (
    publish_job_submission,
    publish_workflow_start,
)

log = logging.getLogger(LOGGING_MODULE)


# Required:
# Specify common settings shared by various executors.

common_settings = CommonSettings(
    # define whether your executor plugin executes locally
    # or remotely. In virtually all cases, it will be remote execution
    # (cluster, cloud, etc.). Only Snakemake's standard execution
    # plugins (snakemake-executor-plugin-dryrun, snakemake-executor-plugin-local)
    # are expected to specify False here.
    non_local_exec=True,
    # Whether the executor implies to not have a shared file system
    implies_no_shared_fs=False,
    # whether to deploy workflow sources to default storage provider before execution
    job_deploy_sources=True,
    # whether arguments for setting the storage provider shall be passed to jobs
    pass_default_storage_provider_args=True,
    # whether arguments for setting default resources shall be passed to jobs
    pass_default_resources_args=True,
    # whether environment variables shall be passed to jobs (if False, use
    # self.envvars() to obtain a dict of environment variables and their values
    # and pass them e.g. as secrets to the execution backend)
    pass_envvar_declarations_to_cmd=True,
    # whether the default storage provider shall be deployed before the job is run on
    # the remote node. Usually set to True if the executor does not assume a shared fs
    auto_deploy_default_storage_provider=False,
    # specify initial amount of seconds to sleep before checking for job status
    init_seconds_before_status_checks=0,
)


# Required:
# Implementation of your executor
class Executor(RemoteExecutor):
    """REANA Snakemake executor implementation."""

    def __post_init__(self):
        """Override generic executor __post__init method."""
        # IMPORTANT: in your plugin, only access methods and properties of
        # Snakemake objects (like Workflow, Persistence, etc.) that are
        # defined in the interfaces found in the
        # snakemake-interface-executor-plugins and the
        # snakemake-interface-common package.
        # Other parts of those objects are NOT guaranteed to remain
        # stable across new releases.

        # To ensure that the used interfaces are not changing, you should
        # depend on these packages as >=a.b.c,<d with d=a+1 (i.e. pin the
        # dependency on this package to be at least the version at time
        # of development and less than the next major version which would
        # introduce breaking changes).

        # In case of errors outside of jobs, please raise a WorkflowError

        self.publisher = WorkflowStatusPublisher()
        self.rjc_api_client = JobControllerAPIClient("reana-job-controller")

    def run_job(self, job: JobExecutorInterface):
        """Override generic executor run_job method."""
        # Implement here how to run a job.
        # You can access the job's resources, etc.
        # via the job object.
        # After submitting the job, you have to call
        # self.report_job_submission(job_info).
        # with job_info being of type
        # snakemake_interface_executor_plugins.executors.base.SubmittedJobInfo.
        # If required, make sure to pass the job's id to the job_info object, as keyword
        # argument 'external_job_id'.

        workflow_workspace = os.getenv("workflow_workspace", "default")
        workflow_uuid = os.getenv("workflow_uuid", "default")
        publish_workflow_start(
            workflow_uuid=workflow_uuid, publisher=self.publisher, job=job
        )
        try:
            log.info(f"Job '{job.name}' received, command: {job.shellcmd}")
            container_image = self._get_container_image(job)
            if job.is_shell:
                # Shell command
                job_request_body = {
                    "workflow_uuid": workflow_uuid,
                    "image": container_image,
                    "cmd": f"cd {workflow_workspace} && {job.shellcmd}",
                    "prettified_cmd": job.shellcmd,
                    "workflow_workspace": workflow_workspace,
                    "job_name": self._build_job_name(job),
                    "cvmfs_mounts": MOUNT_CVMFS,
                    "compute_backend": job.resources.get("compute_backend", ""),
                    "kerberos": job.resources.get("kerberos", WORKFLOW_KERBEROS),
                    "unpacked_img": job.resources.get("unpacked_img", False),
                    "kubernetes_uid": job.resources.get("kubernetes_uid"),
                    "kubernetes_cpu_request": job.resources.get(
                        "kubernetes_cpu_request"
                    ),
                    "kubernetes_cpu_limit": job.resources.get("kubernetes_cpu_limit"),
                    "kubernetes_memory_request": job.resources.get(
                        "kubernetes_memory_request"
                    ),
                    "kubernetes_memory_limit": job.resources.get(
                        "kubernetes_memory_limit"
                    ),
                    "kubernetes_job_timeout": job.resources.get(
                        "kubernetes_job_timeout"
                    ),
                    "voms_proxy": job.resources.get("voms_proxy", False),
                    "rucio": job.resources.get("rucio", False),
                    "htcondor_max_runtime": job.resources.get(
                        "htcondor_max_runtime", ""
                    ),
                    "htcondor_accounting_group": job.resources.get(
                        "htcondor_accounting_group", ""
                    ),
                    "slurm_partition": job.resources.get("slurm_partition"),
                    "slurm_time": job.resources.get("slurm_time"),
                    "c4p_cpu_cores": job.resources.get("c4p_cpu_cores"),
                    "c4p_memory_limit": job.resources.get("c4p_memory_limit"),
                    "c4p_additional_requirements": job.resources.get(
                        "c4p_additional_requirements"
                    ),
                }
                job_id = self._submit_job(
                    self.rjc_api_client, self.publisher, job_request_body
                )
                self.report_job_submission(
                    SubmittedJobInfo(job=job, external_jobid=job_id)
                )
            elif job.is_run:
                # Python code
                log.error("Python code execution is not supported yet.")
        except Exception as e:
            log.error(f"Error submitting job {job.name}: {e}")
            return

    async def check_active_jobs(
        self, active_jobs: List[SubmittedJobInfo]
    ) -> Generator[SubmittedJobInfo, None, None]:
        """Override generic executor check_active_jobs method."""
        # Check the status of active jobs.

        # You have to iterate over the given list active_jobs.
        # If you provided it above, each will have its external_jobid set according
        # to the information you provided at submission time.
        # For jobs that have finished successfully, you have to call
        # self.report_job_success(active_job).
        # For jobs that have errored, you have to call
        # self.report_job_error(active_job).
        # This will also take care of providing a proper error message.
        # Usually there is no need to perform additional logging here.
        # Jobs that are still running have to be yielded.
        #
        # For queries to the remote middleware, please use
        # self.status_rate_limiter like this:
        #
        # async with self.status_rate_limiter:
        #    # query remote middleware here
        #
        # To modify the time until the next call of this method,
        # you can set self.next_sleep_seconds here.

        self.next_sleep_seconds = POLL_JOBS_STATUS_SLEEP_IN_SECONDS

        log.debug(f"Checking status of {len(active_jobs)} jobs")

        for active_job in active_jobs:
            async with self.status_rate_limiter:
                try:
                    job_id = active_job.external_jobid

                    status = self._get_job_status_from_controller(job_id)

                    if status == JobStatus.finished.name or active_job.job.is_norun:
                        self.report_job_success(active_job)
                        self._handle_job_status(
                            active_job.external_jobid,
                            active_job.job.name,
                            job_status=JobStatus.finished,
                            workflow_status=RunStatus.running,
                        )

                    elif status in (
                        JobStatus.failed.name,
                        JobStatus.stopped.name,
                    ):
                        self.report_job_error(active_job)
                        self._handle_job_status(
                            active_job.external_jobid,
                            active_job.job.name,
                            job_status=JobStatus.failed,
                            workflow_status=RunStatus.failed,
                        )

                    else:
                        yield active_job

                except WorkflowError as e:
                    log.error(
                        f"Something went wrong while checking the status of the active jobs.\nError message{str(e)}"
                    )
                    self.report_job_error(active_job)

    def cancel_jobs(self, active_jobs: List[SubmittedJobInfo]):
        """Override generic executor cancel_jobs method."""
        # Cancel all active jobs.
        # This method is called when Snakemake is interrupted.

        for active_job in active_jobs:
            job_id = active_job.external_jobid

            self.rjc_api_client.delete_job(job_id)

        workflow_uuid = os.getenv("workflow_uuid", "default")
        self.publisher.publish_workflow_status(
            workflow_uuid,
            RunStatus.failed,
            message="Snakemake is interrupted and all jobs are cancelled",
        )

    @staticmethod
    def _build_job_name(job: JobExecutorInterface) -> str:
        """Build a descriptive job name including wildcards.

        This creates more informative job names by appending wildcard key-value
        pairs to the rule name. For example, a rule "process" with wildcards
        sample=A and fileno=22 becomes "process (sample=A, fileno=22)".
        """
        try:
            if job.wildcards:
                wildcards = ", ".join(f"{k}={v}" for k, v in job.wildcards.items())
                return f"{job.name} ({wildcards})"
        except AttributeError:
            pass
        return job.name

    @staticmethod
    def _get_container_image(job: JobExecutorInterface) -> str:
        if job.container_img_url:
            container_image = job.container_img_url.replace("docker://", "")
            log.info(f"Environment: {container_image}")
        else:
            container_image = REANA_DEFAULT_SNAKEMAKE_ENV_IMAGE
            log.info(f"No environment specified, falling back to: {container_image}")
        return container_image

    def _handle_job_status(
        self,
        job_id: str,
        job_name: str,
        job_status: JobStatus,
        workflow_status: RunStatus,
    ) -> None:
        workflow_uuid = os.getenv("workflow_uuid", "default")
        log.info(f"{job_name} job is {job_status.name}. job_id: {job_id}")
        message = None
        if job_id:
            message = {
                "progress": build_progress_message(
                    **{job_status.name: {"total": 1, "job_ids": [job_id]}}
                )
            }
        self.publisher.publish_workflow_status(
            workflow_uuid, workflow_status.value, message=message
        )

    def _get_job_status_from_controller(self, job_id: str) -> str:
        """Get job status from controller.

        If error occurs, return `failed` status.
        """
        try:
            response = self.rjc_api_client.check_status(job_id)
        except HTTPNotFound:
            log.error(
                f"Job {job_id} was not found in job-controller. Return job failed status."
            )
            return JobStatus.failed.name
        except Exception as exception:
            log.error(
                f"Error getting status of job with id {job_id}. Return job failed status. Details: {exception}"
            )
            return JobStatus.failed.name

        try:
            return response.status
        except AttributeError:
            log.error(
                f"job-controller response for job {job_id} does not contain 'status' field. Return job failed status."
                f"Response: {response}"
            )
            return JobStatus.failed.name

    def _submit_job(self, rjc_api_client, publisher, job_request_body):
        """Submit job to REANA Job Controller."""
        response = rjc_api_client.submit(**job_request_body)
        job_id = str(response["job_id"])

        log.info(f"submitted job: {job_id}")
        publish_job_submission(
            workflow_uuid=job_request_body["workflow_uuid"],
            publisher=publisher,
            reana_job_id=job_id,
        )
        return job_id
