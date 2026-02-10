<!-- markdownlint-disable MD013 -->

# Changelog

## [0.9.5](https://github.com/reanahub/reana-workflow-engine-snakemake/compare/0.9.4...0.9.5) (2026-02-10)


### Build

* **python:** pin setuptools below 81 ([#120](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/120)) ([9544928](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/9544928cb043c55900146837038267e8004d2c7b))


### Features

* **executor:** include wildcards in job names ([#119](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/119)) ([3c63cdd](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/3c63cdd2c36db2eabd33be5df98f93ea07c6d500)), closes [#118](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/118)
* **executor:** pass K8S requests/limits to job controller ([#108](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/108)) ([a63d589](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/a63d58971ef0a72c073d14f7aac817ff1e2c1330))
* **executor:** pass K8S requests/limits to job controller ([#108](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/108)) ([c851e91](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/c851e916ce6a6e2cbf2c74fb49987e345e8b4cb7))


### Bug fixes

* **runner:** use Path object for report path ([#116](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/116)) ([eaf8dd3](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/eaf8dd3d1b29f2c1ed3dda304f5307186bf2e9de))


### Code style

* **python:** adapt code base to the new black version ([#119](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/119)) ([c533f74](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/c533f743a4d5787076c027c5777ac81a7c80ece8))


### Continuous integration

* **commitlint:** fix local running of commit linter on macOS ([#111](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/111)) ([87de837](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/87de837f53b1626b0333ac9939edb083cb909943))
* **jsonlint:** add JSON linting ([#113](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/113)) ([7bf64ad](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/7bf64ad0ec6b58e97502217805c5e3d72f16ada9))
* **markdownlint:** add Markdown linting ([#113](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/113)) ([0caa994](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/0caa994d41fcc67451676fe78e223f9f31259a42))
* **prettier:** add Prettier code formatting checks ([#113](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/113)) ([c281daf](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/c281daf1be8bb1baa95b55cc3557622afe87eba9))
* **runners:** upgrade CI runners to Ubuntu 22.04 ([#110](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/110)) ([a63d589](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/a63d58971ef0a72c073d14f7aac817ff1e2c1330))
* **runners:** upgrade CI runners to Ubuntu 22.04 ([#110](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/110)) ([1f71907](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/1f71907cfa20dd67fec6c5c094e58727bea6806e))
* **shfmt:** add shell script formatting checks ([#113](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/113)) ([365c940](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/365c940ce6cf0471f06181499f7d3ae82b1f02f8))
* **yamllint:** add YAML linting ([#113](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/113)) ([396408d](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/396408df6879590e1802b9e6a2c950794268905f))

## [0.9.4](https://github.com/reanahub/reana-workflow-engine-snakemake/compare/0.9.3...0.9.4) (2024-11-29)

### Build

* **docker:** fix XRootD repository location ([#95](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/95)) ([69fea32](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/69fea329dd9bf91ff9eb1de9ac741262512a872a))
* **docker:** pin setuptools 70 ([#102](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/102)) ([b27c9cf](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/b27c9cfa21603ecc1554931f23c945d3f9e256d6))
* **python:** bump shared REANA packages as of 2024-11-28 ([#104](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/104)) ([fb9efc8](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/fb9efc8267c24ce65e8d188a5171d8abd5531cd7))

### Features

* **executor:** allow Compute4PUNCH backend options ([#97](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/97)) ([4b00c52](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/4b00c523eb8750f49262471a43c9deefad1021d3))

### Bug fixes

* **executor:** override default resources to remove mem/disk ([#91](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/91)) ([572a83f](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/572a83f5190c7cae95a4607b792f4b6e0c39262c)), closes [#90](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/90)

## [0.9.3](https://github.com/reanahub/reana-workflow-engine-snakemake/compare/0.9.2...0.9.3) (2024-03-04)

### Build

* **docker:** install correct extras of reana-commons submodule ([#79](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/79)) ([fd9b88a](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/fd9b88a857ba016343d956e42a49b6fbc906f068))
* **docker:** non-editable submodules in "latest" mode ([#73](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/73)) ([c3595c2](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/c3595c297e90f74a9215fd76c6d6b5f69d640440))
* **python:** bump all required packages as of 2024-03-04 ([#85](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/85)) ([66e81e2](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/66e81e2148ad4ba72099a90dbb556454df3cfc99))
* **python:** bump shared REANA packages as of 2024-03-04 ([#85](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/85)) ([d07f91f](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/d07f91f6f725050c681c66ec920727f26db3fdbf))

### Features

* **config:** get max number of parallel jobs from env vars ([#84](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/84)) ([69cfad4](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/69cfad460b240e5dbafea42137d891d6fea607a5))
* **executor:** upgrade to Snakemake v7.32.4 ([#81](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/81)) ([4a3f359](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/4a3f3592c8dd3f323e81850f5bdfae45ea893825))

### Bug fixes

* **progress:** handle stopped jobs ([#78](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/78)) ([4829d80](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/4829d80a5e03ab5788fb6646bd792a7345abe14a))

### Code refactoring

* **docs:** move from reST to Markdown ([#82](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/82)) ([31de94f](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/31de94f79b1955328961d506ce9d8d4efbe7227f))

### Continuous integration

* **commitlint:** addition of commit message linter ([#74](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/74)) ([145b7e7](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/145b7e716a784c340e2ecdca5619b3ed97325b1b))
* **commitlint:** allow release commit style ([#86](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/86)) ([fd032db](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/fd032db1605ac1a295a0eac5c32799707d78cd6b))
* **commitlint:** check for the presence of concrete PR number ([#80](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/80)) ([b677913](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/b677913aef2df090103d461bc71dc2cde42b4212))
* **release-please:** initial configuration ([#74](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/74)) ([9b16bd0](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/9b16bd052903be4a8c567b2e71f7b56a601982b4))
* **release-please:** update version in Dockerfile ([#77](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/77)) ([3c35a67](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/3c35a67db7c181e23f28fda6152f40c8251f9b74))
* **shellcheck:** fix exit code propagation ([#80](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/80)) ([ad15c0d](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/ad15c0d0e2020fd874a9eed5c4b36e320129b9eb))

### Documentation

* **authors:** complete list of contributors ([#83](https://github.com/reanahub/reana-workflow-engine-snakemake/issues/83)) ([4782678](https://github.com/reanahub/reana-workflow-engine-snakemake/commit/478267864a20da6ab4d7f99be5592fcf19a20ca1))

## 0.9.2 (2023-12-12)

* Adds automated container image building for amd64 architecture.
* Adds metadata labels to Dockerfile.
* Fixes creation of image thumbnails for output files in Snakemake HTML execution reports.
* Fixes container image building on the arm64 architecture.

## 0.9.1 (2023-09-27)

* Changes remote storage file support to use XRootD 5.6.0.
* Fixes the reported total number of jobs for restarted workflows by excluding cached jobs that were simply reused from previous runs in the workspace and not really executed by Snakemake.
* Fixes an issue where workflows could get stuck waiting for already-finished jobs.
* Fixes container image names to be Podman-compatible.

## 0.9.0 (2023-01-19)

* Adds support for specifying `slurm_partition` and `slurm_time` for Slurm compute backend jobs.
* Adds support for XRootD remote file locations in workflow specification definitions.
* Adds support for Kerberos authentication for workflow orchestration.
* Adds support for Rucio authentication for workflow jobs.
* Changes global setting of maximum number of parallel jobs to 300.
* Changes the base image of the component to Ubuntu 20.04 LTS and reduces final Docker image size by removing build-time dependencies.
* Fixes progress reporting for failed workflow jobs.

## 0.8.1 (2022-02-07)

* Adds support for specifying `kubernetes_job_timeout` for Kubernetes compute backend jobs.
* Adds polling job-controller to determine job statuses instead of checking files.

## 0.8.0 (2021-11-22)

* Adds initial REANA Snakemake executor implementation.
* Adds support for snakemake reports generation.
* Adds support for REANA custom resources.
* Adds support for parallel job execution.
