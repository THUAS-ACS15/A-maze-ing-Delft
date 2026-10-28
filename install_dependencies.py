from display import out


def check_dependencies():
    """
    Install missing or incompatible packages declared in requirements.txt.
    
    This function checks the installed packages against the requirements in the requirements.txt file.
    If any required packages are missing or have incompatible versions, it attempts to install them using pip.
    
    If running inside a pyinstaller exe, this function is skipped fully.
    
    Inputs: NONE
    
    Outputs: NONE
    """

    from pathlib import Path
    import sys
    import subprocess
    import platform
    from importlib.metadata import PackageNotFoundError, distribution
    from packaging.requirements import Requirement

    # if system packages are frozen, we're running inside a bundled exe and can skip dependency checks
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return

    requirements_path = Path(__file__).resolve() # get the full path to main
    requirements_path = requirements_path.with_name('requirements.txt') # add /requirements.txt
    requirements = []
    with requirements_path.open(encoding='utf-8') as req_file:
        for line in req_file:
            # strip extra whitespace
            requirement_text = line.strip()
            # check if comment
            if not requirement_text or requirement_text.startswith('#'):
                continue
            # add class form requirement and original text to list
            requirements.append((Requirement(requirement_text), requirement_text))

    missing = []

    for requirement, requirement_text in requirements:
        try:
            # get version specific to OS with distribution(), then get version of that
            installed_version = distribution(requirement.name).version
            if requirement.specifier and not requirement.specifier.contains(installed_version):
                missing.append(requirement_text)
        except PackageNotFoundError:
            missing.append(requirement_text)

    if missing:
        out(f'Found missing packages: {", ".join(missing)}')
        out('Installing them... Please wait.')
        python_path = sys.executable
        try:
            try:
                # shortcut to devnull (void all stdout/stderr)
                devnull = subprocess.DEVNULL
                subprocess.check_call([python_path, '-m', 'pip', '--version'], stdout = devnull, stderr = devnull)
            except (OSError, subprocess.CalledProcessError):
                try:
                    subprocess.check_call([python_path, '-m', 'ensurepip'])
                except Exception:
                    print('Pip is not installed and ensurepip is not available. Please install pip manually.')
                    return

            install_command = [python_path, '-m', 'pip', 'install', *missing]
            # this is needed for external package manages like apt or yum on Linux
            # that freeze system packages
            if platform.system() == 'Linux':
                install_command.append('--break-system-packages')
            subprocess.check_call(install_command, stdout=subprocess.DEVNULL)
        except Exception:
            print('Failed to install dependencies. Try running "pip install -r', end = '')
            print('requirements.txt" from your terminal while in the game\'s root folder.')