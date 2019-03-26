import glob
import logging
import os
import os.path
import subprocess

from functools import partial
from multiprocessing.pool import Pool
from subprocess import Popen, PIPE

REPO_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKERFILES_DIR = f'{REPO_DIR}/dockerfiles'

logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def all_dockerfiles():
    return normalize_paths([
        filename for filename in glob.iglob(f'{DOCKERFILES_DIR}/**', recursive=True)
        if "Dockerfile" in filename
    ])


def dockerfiles(differ=None):
    logging.info('Fetching list of changed Dockerfiles')
    try:
        return normalize_paths(
            subprocess.check_output(
                differ, stderr=subprocess.DEVNULL,  shell=True
            ).decode('utf8').strip().split('\n')
        )
    except:
        logging.warn('Unable to find changed dockerfiles. Returning all.')
        return all_dockerfiles()


def normalize_paths(dockerfiles):
    dockerfile_list = [file.split(f'dockerfiles/')[-1] for file in dockerfiles]
    return [file.split('/Dockerfile')[0] for file in dockerfile_list]


def get_tag(dockerfile):
    return f'gcr.io/cloud-devrel-kokoro-resources/{dockerfile}'


def run(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, encoding="utf-8", stderr=PIPE)
    return p.communicate()


def build(dockerfile, logs=[], errs=[]):
    logs.append(f'Building {dockerfile}')
    tag = get_tag(dockerfile)
    output, err = run(
        f'docker build --tag {tag} {DOCKERFILES_DIR}/{dockerfile}')
    logs.append(output)
    errs.append(err)
    if not err:
        logs.append(f'Successfully built {dockerfile}')
    else:
        errs.append(err)
        logs.append(f'Unable to build {dockerfile}')
    return logs, errs


def push(dockerfile, logs=[], errs=[]):
    logs.append(f'Pushing {dockerfile}')
    output, err = run(f'docker push {get_tag(dockerfile)}')
    logs.append(output)
    if not err:
        logs.append(f'Successfully pushed {dockerfile}')
    else:
        errs.append(err)
        logs.append(f'Unable to push {dockerfile}')
    return logs, errs


def update(should_push, dockerfile):
    logs, errs = build(dockerfile)
    if should_push and not ''.join(errs):
        output, errs_b = push(dockerfile)
        logs.extend(output)
        if errs_b:
            errs.extend(errs_b)
    logging.info('\n'.join(logs))
    logging.info('\n'.join(errs))


def main():
    differ = None
    should_push = True
    # if os.environ['JOB_TYPE'] == 'presubmit':
    #     differ = 'git --no-pager diff --name-only HEAD $(git merge-base HEAD master) | grep "Dockerfile"'
    #     should_push = False
    # elif os.environ['JOB_TYPE'] == 'continuous':
    #     differ = 'git --no-pager diff --name-only HEAD^ HEAD | grep "Dockerfile"'
    dockerfile_list = dockerfiles(differ)

    if should_push:
        logging.info('Updating docker images:')
    else:
        logging.info('Building docker images:')
    logging.info(
        '\n'.join([f'   - {dockerfile}' for dockerfile in dockerfile_list]) + '\n')

    updater = partial(update, should_push)
    with Pool(len(dockerfile_list)) as p:
        p.map(updater, dockerfile_list)


if __name__ == '__main__':
    main()
