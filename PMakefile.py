
global TWINE_USER
global TWINE_PASSWORD
global ADMIN_PASSWORD

TWINE_USER = "Koldar"
TWINE_PASSWORD = read_file_content("TWINE_PASSWORD")
ADMIN_PASSWORD = read_file_content("PASSWORD")


def clean():
    remove_tree("dist")
    remove_tree("build")
    remove_tree("pmake.egg-info")


def update_version():
    ensure_has_variable("VERSION_IDENTIFIER")
    ensure_has_variable("NEW_VERSION")

    version_filepath = os.path.join("pmake", "version.py")
    remove_last_n_line_from_file(version_filepath, n=1)
    append_strings_at_end_of_file(version_filepath, content=[
        f"{variables.VERSION_IDENTIFIER} = \"{variables.NEW_VERSION}\"",
        f"",
        f"VERSION = {variables.VERSION_IDENTIFIER}"
    ])


def uninstall():
    execute_admin_with_password_stdout_on_screen(
        password=ADMIN_PASSWORD,
        commands="pip3 uninstall --yes pmake",
    )


def build():
    if on_linux():
        echo("building for linux", foreground="blue")
        execute_and_forget([
            f"source venv/bin/activate",
            f"python setup.py bdist_wheel",
            f"deactivate"
        ])
    elif on_windows():
        echo("building for windows", foreground="blue")
        execute_and_forget([
            f"python setup.py bdist_wheel",
        ])
    else:
        raise PMakeException()


def generate_documentation():
    oldcwd = cd("docs")
    if on_linux():
        execute_stdout_on_screen([
                "make html latexpdf"
            ],
        )
    elif on_windows():
        execute_stdout_on_screen([
            "make.bat html latexpdf"
        ],
        )
    cd(oldcwd)


def install():
    ADMIN_PASSWORD = read_file_content("PASSWORD")
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    echo(f"file list = {' '.join(file_list)}")
    wheel_file = list(filter(lambda x: '.whl' in x, file_list))[0]
    execute_admin_with_password_stdout_on_screen(
        password=ADMIN_PASSWORD,
        commands=f"pip3 install {wheel_file}",
    )


def upload_to_test_pypi():
    latest_version, file_list = get_latest_version_in_folder("dist", version_fetcher=semantic_version_2_only_core)
    upload_files = ' '.join(map(lambda x: f"\"{x}\"", file_list))

    if on_linux():
        echo("Uploading for linux", foreground="blue")
        execute_stdout_on_screen([
            #"source venv/bin/activate",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_USER}\" --password \"{TWINE_PASSWORD}\" {upload_files}",
            #"deactivate"
        ])
    elif on_windows():
        echo("Uploading for windows", foreground="blue")
        execute_stdout_on_screen([
            #"venv/Scripts/activate.bat",
            f"twine upload --verbose --repository testpypi --username \"{TWINE_USER}\" --password \"{TWINE_PASSWORD}\" {upload_files}",
            #"venv/Scripts/deactivate.bat"
        ])
    else:
        raise PMakeException()


if "clean" in targets:
    echo("Cleaning...", foreground="blue")
    clean()

if "uninstall" in targets:
    echo("Uninstall...", foreground="blue")
    uninstall()

if "update-version" in targets:
    echo("Updating version...", foreground="blue")
    update_version()

if "build" in targets:
    echo("Building...", foreground="blue")
    build()

if "generate-documentation" in targets:
    echo("Building documentation...", foreground="blue")
    generate_documentation()

if "install" in targets:
    echo("Installing...", foreground="blue")
    install()

if "upload-to-test-pypi" in targets:
    echo("Uploading to test pypi...", foreground="blue")
    upload_to_test_pypi()

if "upload-to-pypi" in targets:
    echo("Uploading to pypi...", foreground="blue")
    upload_to_pypi()

echo("DONE!", foreground="green")

