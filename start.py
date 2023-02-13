import os
import pkg_resources

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
__requirements_path = ROOT_DIR + 'requirements.txt'


def create_venv(python_exe_path_, proj_path):
    command = ' -m venv '
    os.system(python_exe_path_ + command + proj_path + '.venv')


def import_requirements(proj_path):
    python_interpreter = proj_path + '.venv/bin/python'
    os.system(python_interpreter + ' -m pip install -r ' + __requirements_path)


if __name__ == '__main__':
    project_path = ROOT_DIR

    if not os.path.exists(project_path + '.venv'):
        print(f'Creating [venv] to {project_path}...', end=' ')
        create_venv('py', project_path)
        print(f'done')

        print('Importing requirements...', end=' ')
        import_requirements(project_path)
        print('done')

    else:
        print('Checking packages...', end=' ')
        pkg_resources.require(open(__requirements_path, mode='r', encoding='utf-8').readlines())
        print('done')

    print(f'Starting main file at {project_path + r"app.py"}')

    try:
        os.system(project_path + '.venv/bin/python ' + project_path + r'app.py')

    except KeyboardInterrupt:
        pass
