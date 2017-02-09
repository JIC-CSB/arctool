"""Module for generating slurm scripts."""

import os

from arctool import JINJA2_ENV


def generate_slurm_script(command_string, job_parameters):
    """Return slurm script.

    :param command_string: command to run in slurm script
    :param job_parameters: dictionary of job parameters
    :returns: slurm sbatch script
    """
    template = JINJA2_ENV.get_template('submit_command.slurm.j2')
    return template.render(job=job_parameters, command_string=command_string)
