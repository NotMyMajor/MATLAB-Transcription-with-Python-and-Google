
def install(package):
    import subprocess
    import sys
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])
    except:
        print("Installation failed. Manual installation required.")

def startup_check():

    import sys
    import pkg_resources
    import os

    dirname = os.path.dirname(os.path.abspath(__file__))

    required = ['google-cloud-speech', 'google-cloud-storage']
    installed = list({pkg.key for pkg in pkg_resources.working_set})
    missing = [ele for ele in range(len(required)) if ele not in installed]

    ready_to_go = True

    if missing:
        try:
            for i in range(len(missing)):
                install(required[missing[i]])
        except:
            print("Automatic installation failed. Switching to manual installation instructions.\n")

            print("\nMissing the following package(s): {}\n".format(missing))
            print("Please install the missing packages with pip.\n")
            print("Run the following command in another terminal:")
            packages_install = "python -m pip install "
            packages_install_alt = "py -m pip install "
            for entry in missing:
                packages_install += str(entry)
                packages_install += " "
                packages_install_alt += str(entry)
                packages_install_alt += " "
            print(packages_install, "\n")
            print("If that command does not work. Please try the following: ")
            print(packages_install_alt, "\n")
            #input("Press ENTER to continue.\n")
            ready_to_go = False
    else:
        print("\nAll necessary packages found.")

    if dirname not in sys.path:
        print("\nDirectory not found in PATH. Adding current directory to PATH.")
        sys.path.append(dirname)
        print("Added {} to system PATH. New sys.path: {}".format(dirname, sys.path))

    else:
        print("\nDirectory found in system PATH.")

    try:

        from google.cloud import speech_v1p1beta1 as speech
        from google.cloud import storage
        print("Looks like everything works as intended! You're ready to begin!")

    except:

        print("Oops something went wrong. You may have to manually install the required packages. Sorry!")
        ready_to_go = False
    
    return ready_to_go

startup_check()
