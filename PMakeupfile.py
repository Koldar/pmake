import os

import semantic_version
from semantic_version import Version

import pmakeup as pm

core: pm.CorePMakeupPlugin = pmakeup_info.pmakeup_plugins["CorePMakeupPlugin"]
files: pm.FilesPMakeupPlugin = pmakeup_info.pmakeup_plugins["FilesPMakeupPlugin"]
log: pm.LoggingPMakeupPlugin = pmakeup_info.pmakeup_plugins["LoggingPMakeupPlugin"]
operating_system: pm.OperatingSystemPMakeupPlugin = pmakeup_info.pmakeup_plugins["OperatingSystemPMakeupPlugin"]
paths: pm.PathsPMakeupPlugin = pmakeup_info.pmakeup_plugins["PathsPMakeupPlugin"]
targets: pm.TargetsPMakeupPlugin = pmakeup_info.pmakeup_plugins["TargetsPMakeupPlugin"]

core.require_pmakeup_version("2.3.4")

global TWINE_TEST_PYPI_USER
global TWINE_TEST_PYPI_PASSWORD
global ADMIN_PASSWORD

TWINE_TEST_PYPI_USER = "Koldar"
TWINE_PYPI_USER = "Koldar"
ADMIN_PASSWORD = files.read_file_content("PASSWORD")


def clean():
    log.echo("Cleaning...", foreground="blue")
    files.remove_tree("dist")
    files.remove_tree("build")
    files.remove_tree("pmake.egg-info")


def _read_version() -> Version:
    version_filepath = os.path.join("pmakeup", "version.py")
    with open(version_filepath, "r") as f:
        version = f.read().split("=")[1].strip("\" \t\n")
    return Version(version)


def update_version_major():
    version = _read_version()
    new_version = version.next_major()
    version_filepath = os.path.join("pmakeup", "version.py")

    log.echo(f"Updating version from {version} to {new_version} in {paths.cwd()}...", foreground="blue")
    files.write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def update_version_minor():
    version = _read_version()
    new_version = version.next_minor()
    version_filepath = os.path.join("pmakeup", "version.py")

    log.echo(f"Updating version from {version} to {new_version} in {paths.cwd()}...", foreground="blue")
    files.write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def update_version_patch():
    version = _read_version()
    new_version = version.next_patch()
    version_filepath = os.path.join("pmakeup", "version.py")

    log.echo(f"Updating version from {version} to {new_version} in {paths.cwd()}...", foreground="blue")
    files.write_file(version_filepath, f"VERSION = \"{new_version}\"", overwrite=True)


def uninstall():
    log.echo("Uninstall...", foreground="blue")
    operating_system.execute_admin_with_password_stdout_on_screen(
        password=ADMIN_PASSWORD,
        commands="pip3 uninstall --yes pmake",
    )


def build():
    log.echo("Building...", foreground="blue")
    if core.on_linux():
        log.echo("building for linux", foreground="blue")
        operating_system.execute_stdout_on_screen([
            f"source {paths.path('venv', 'bin', 'activate')}",
            f"python setup.py bdist_wheel",
            f"deactivate"
        ])
    elif core.on_windows():
        log.echo(f"building for windows in {paths.cwd()}", foreground="blue")
        operating_system.execute_stdout_on_screen([
            f"python setup.py bdist_wheel",
        ])
    else:
        raise pm.PMakeupException()


def generate_documentation():
    log.echo("Building documentation...", foreground="blue")
    oldcwd = paths.cd("docs")
    if core.on_linux():
        operating_system.execute_stdout_on_screen([
                "make html latexpdf"
            ],
        )
    elif core.on_windows():
        operating_system.execute_stdout_on_screen([
            "make.bat html latexpdf"
        ],
        )
    paths.cd(oldcwd)


def install():
    log.echo("Installing...", foreground="blue")
    ADMIN_PASSWORD = files.read_file_content("PASSWORD")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    log.echo(f"file list = {' '.join(file_list)}")
    wheel_file = list(filter(lambda x: '.whl' in x, file_list))[0]
    if core.on_linux():
        operating_system.execute_admin_with_password_stdout_on_screen(
            password=ADMIN_PASSWORD,
            commands=f"pip3 install {wheel_file}",
        )
    elif core.on_windows():
        operating_system.execute_admin_with_password_stdout_on_screen(
            password=ADMIN_PASSWORD,
            commands=f"pip install {wheel_file}",
        )


def upload_to_test_pypi():
    TWINE_TEST_PYPI_PASSWORD = files.read_file_content("TWINE_TEST_PYPI_PASSWORD")
    log.echo("Uploading to test pypi...", foreground="blue")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))

    if core.on_linux():
        log.echo("Uploading for linux", foreground="blue")
        operating_system.execute_stdout_on_screen([
            #"source venv/bin/activate",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_TEST_PYPI_USER}\" --password \"{TWINE_TEST_PYPI_PASSWORD}\" {upload_files}",
            #"deactivate"
        ])
    elif core.on_windows():
        log.echo("Uploading for windows", foreground="blue")
        operating_system.execute_stdout_on_screen([
            #"venv/Scripts/activate.bat",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_TEST_PYPI_USER}\" --password \"{TWINE_TEST_PYPI_PASSWORD}\" {upload_files}",
            #"venv/Scripts/deactivate.bat"
        ])
    else:
        raise pm.PMakeupException()


def upload_to_pypi():
    TWINE_PYPI_PASSWORD = files.read_file_content("TWINE_PYPI_PASSWORD")
    log.echo("Uploading to pypi ...", foreground="blue")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))
    log.echo(f"File to upload is {upload_files}...", foreground="blue")

    if core.on_linux():
        log.echo("Uploading for linux", foreground="blue")
        operating_system.execute_stdout_on_screen([
            f"twine upload --verbose --non-interactive --username \"{TWINE_PYPI_USER}\" --password \"{TWINE_PYPI_PASSWORD}\" {upload_files}",
        ])
    elif core.on_windows():
        log.echo("Uploading for windows", foreground="blue")
        operating_system.execute_stdout_on_screen([
            f"twine upload --verbose --non-interactive --username \"{TWINE_PYPI_USER}\" --password \"{TWINE_PYPI_PASSWORD}\" {upload_files}",
        ])
    else:
        raise pm.PMakeupException()


targets.declare_file_descriptor(f"""
    This file allows to build, locally install and potentially upload a new version of pmake.
""")
targets.declare_target(
    target_name="clean",
    description="Clean all folders that are automatically generated",
    f=clean,
    requires=[],
)
targets.declare_target(
    target_name="uninstall",
    description="Uninstall local version of pmake in the global pip sites",
    f=uninstall,
    requires=[],
)
targets.declare_target(
    target_name="update-version-patch",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_patch,
    requires=[],
)
targets.declare_target(
    target_name="update-version-minor",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_minor,
    requires=[],
)
targets.declare_target(
    target_name="update-version-major",
    description="Uninstall local version of pmake in the global pip sites",
    f=update_version_major,
    requires=[],
)
targets.declare_target(
    target_name="build",
    description="Build the application",
    f=build,
    requires=[],
)
targets.declare_target(
    target_name="generate-documentation",
    description="Generate documentation of the application",
    f=generate_documentation,
    requires=["build"],
)
targets.declare_target(
    target_name="install",
    description="Install the application on your system. Uses elevated privileges",
    f=install,
    requires=["build"],
)
targets.declare_target(
    target_name="upload-to-test-pypi",
    description="Upload the latest version of pmake to pypi test",
    f=upload_to_test_pypi,
    requires=["build"],
)
targets.declare_target(
    target_name="upload-to-pypi",
    description="Upload the latest version of pmake to pypi",
    f=upload_to_pypi,
    requires=["build"],
)

targets.process_targets()
