# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2021, 2022, 2023, 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-Workflow-Engine-Snakemake executor."""

import os
import logging
import asyncio
from collections import namedtuple
from typing import Callable

from bravado.exception import HTTPNotFound
from reana_commons.config import REANA_DEFAULT_SNAKEMAKE_ENV_IMAGE
from reana_commons.utils import build_progress_message
from snakemake import snakemake
from snakemake.common import async_lock
from snakemake.executors import ClusterExecutor, GenericClusterExecutor
from snakemake.jobs import Job
from snakemake.resources import DefaultResources
from snakemake import scheduler  # for monkeypatch

from reana_workflow_engine_snakemake.config import (
    DEFAULT_SNAKEMAKE_REPORT_FILENAME,
    LOGGING_MODULE,
    MOUNT_CVMFS,
    SNAKEMAKE_MAX_PARALLEL_JOBS,
    POLL_JOBS_STATUS_SLEEP_IN_SECONDS,
    WORKFLOW_KERBEROS,
    JobStatus,
    RunStatus,
)
from reana_workflow_engine_snakemake.utils import (
    publish_job_submission,
    publish_workflow_start,
)

log = logging.getLogger(LOGGING_MODULE)


REANAClusterJob = namedtuple("REANAClusterJob", "job callback error_callback")


class REANAClusterExecutor(GenericClusterExecutor):
    """REANA Cluster Snakemake executor implementation."""

    def run(
        self,
        job: Job,
        callback: Callable = None,
        submit_callback: Callable = None,
        error_callback: Callable = None,
    ):
        """Override GenericClusterExecutor run method."""
        super()._run(job)

        workflow_workspace = os.getenv("workflow_workspace", "default")
        workflow_uuid = os.getenv("workflow_uuid", "default")
        publish_workflow_start(
            workflow_uuid=workflow_uuid, publisher=self.publisher, job=job
        )
        try:
            job.reana_job_id = None
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
                    "job_name": job.name,
                    "cvmfs_mounts": MOUNT_CVMFS,
                    "compute_backend": job.resources.get("compute_backend", ""),
                    "kerberos": job.resources.get("kerberos", WORKFLOW_KERBEROS),
                    "unpacked_img": job.resources.get("unpacked_img", False),
                    "kubernetes_uid": job.resources.get("kubernetes_uid"),
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
                }
                job_id = submit_job(
                    self.rjc_api_client, self.publisher, job_request_body
                )
                job.reana_job_id = job_id
                self.workflow.persistence.started(job, external_jobid=job.reana_job_id)
            elif job.is_run:
                # Python code
                log.error("Python code execution is not supported yet.")

        except Exception as excep:
            log.error(f"Error submitting job {job.name}: {excep}")
            error_callback(job)
            return

        with self.lock:
            self.active_jobs.append(REANAClusterJob(job, callback, error_callback))

    @staticmethod
    def _get_container_image(job: Job) -> str:
        if job.container_img_url:
            container_image = job.container_img_url.replace("docker://", "")
            log.info(f"Environment: {container_image}")
        else:
            container_image = REANA_DEFAULT_SNAKEMAKE_ENV_IMAGE
            log.info(f"No environment specified, falling back to: {container_image}")
        return container_image

    def _handle_job_status(
        self, job: Job, job_status: JobStatus, workflow_status: RunStatus
    ) -> None:
        workflow_uuid = os.getenv("workflow_uuid", "default")
        job_id = job.reana_job_id
        log.info(f"{job.name} job is {job_status.name}. job_id: {job_id}")
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

    def handle_job_success(self, job: Job) -> None:
        """Override job success method to publish job status."""
        # override handle_touch = True, to enable `touch()` in Snakefiles
        # `touch()` is responsible for checking output files existence
        super(ClusterExecutor, self).handle_job_success(
            job, upload_remote=False, handle_log=False, handle_touch=True
        )

        self._handle_job_status(
            job, job_status=JobStatus.finished, workflow_status=RunStatus.running
        )

    def handle_job_error(self, job: Job) -> None:
        """Override job error method to publish job status."""
        super().handle_job_error(job)

        self._handle_job_status(
            job, job_status=JobStatus.failed, workflow_status=RunStatus.failed
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

    async def _wait_for_jobs(self):
        """Override _wait_for_jobs method to poll job-controller for job statuses.

        Original GenericClusterExecutor._wait_for_jobs method checks success/failure via .jobfinished or .jobfailed files.
        """
        while True:
            async with async_lock(self.lock):
                if not self.wait:
                    return
                active_jobs = self.active_jobs
                self.active_jobs = []
                still_running = []

            for active_job in active_jobs:
                job_id = active_job.job.reana_job_id

                status = self._get_job_status_from_controller(job_id)

                if status == JobStatus.finished.name or active_job.job.is_norun:
                    active_job.callback(active_job.job)
                elif status in (
                    JobStatus.failed.name,
                    JobStatus.stopped.name,
                ):
                    active_job.error_callback(active_job.job)
                else:
                    still_running.append(active_job)

            async with async_lock(self.lock):
                # Even though we have set active_jobs to a new empty list at the
                # beginning of _wait_for_jobs, here that list might not be empty anymore
                # as more jobs might have been added while we were fetching the job
                # statuses from r-j-controller. For this reason we have to extend the
                # list, instead of simply setting active_jobs to still_running.
                self.active_jobs.extend(still_running)

            await asyncio.sleep(POLL_JOBS_STATUS_SLEEP_IN_SECONDS)


def submit_job(rjc_api_client, publisher, job_request_body):
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


def run_jobs(
    rjc_api_client,
    publisher,
    workflow_workspace,
    workflow_file,
    workflow_parameters,
    operational_options={},
):
    """Run Snakemake jobs using custom REANA executor."""
    workflow_file_path = os.path.join(workflow_workspace, workflow_file)
    common_snakemake_args = dict(
        snakefile=workflow_file_path,
        config=workflow_parameters,
        workdir=workflow_workspace,
        keep_logger=True,
        # Since Snakemake v7.3.0, the workflow logs include Snakemake-percieved native
        # resource information on memory and storage (`mem_mb`, `disk_mb`) for each
        # Snakemake rule run on cloud. However, REANA overrides these when running
        # user jobs, so we should hide these in order not to present any misleading
        # information to users. For this reason, the default resources are overridden
        # here with the only the "bare" ones (`tmpdir`).
        default_resources=DefaultResources(mode="bare"),
    )

    def _generate_report():
        """Generate HTML report."""
        success = snakemake(
            **common_snakemake_args,
            report=operational_options.get("report", DEFAULT_SNAKEMAKE_REPORT_FILENAME),
        )
        if not success:
            log.error("Error generating workflow HTML report.")

    # Inject RJC API client and workflow status publisher in the REANA executor
    REANAClusterExecutor.rjc_api_client = rjc_api_client
    REANAClusterExecutor.publisher = publisher
    # Monkeypatch GenericClusterExecutor class in `scheduler` module
    scheduler.GenericClusterExecutor = REANAClusterExecutor

    success = snakemake(
        **common_snakemake_args,
        printshellcmds=True,
        # FIXME: Can be anything as it's not directly used. It's supposed
        # to be the shell command to submit to job e.g. `condor_q`,
        # but we call RJC API client instead.
        cluster="reana",
        notemp=True,
        nodes=SNAKEMAKE_MAX_PARALLEL_JOBS,  # enables DAG parallelization
    )
    # Once the workflow is finished, generate the report,
    # taking into account the metadata generated.
    _generate_report()
    return success
