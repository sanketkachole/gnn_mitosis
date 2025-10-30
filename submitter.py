#!usr/bin/env python
# -*- coding: utf-8 -*-

import os, shutil, argparse, yaml
from datetime import date
from pathlib import Path


# main function
if __name__ == "__main__":
    copyrightMessage = (
        "Contact: patis@iu.edu\n\n"
        + "This program is NOT FDA/CE approved and NOT intended for clinical use.\nCopyright (c) "
        + str(date.today().year)
        + " Indiana University. All rights reserved."
    )

    cwd = Path(__file__).resolve().parent
    all_files_and_folders = os.listdir(cwd)

    parser = argparse.ArgumentParser(
        prog="GANDLF_Experiment_Submitter",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Submit GaNDLF experiments on IU Cluster (Big Red, Quartz).\n\n"
        + copyrightMessage,
    )

    parser.add_argument(
        "-i",
        "--interpreter",
        metavar="",
        default="/N/u/patis/Quartz/projects/gandlf_mine_dp/venv/bin/gandlf_run",
        type=str,
        help="Full path of python interpreter to be called.",
    )
    parser.add_argument(
        "-g",
        "--gandlfrun",
        metavar="",
        # default="/N/u/patis/BigRed200/projects/gandlf_mine/gandlf_run", ## old way: https://github.com/mlcommons/GaNDLF/pull/845
        default=" ",
        type=str,
        help="Full path of 'gandlf_run' script to be called.",
    )
    parser.add_argument(
        "-d",
        "--datafile",
        metavar="",
        default=os.path.join(cwd, "data.csv"),
        type=str,
        help="Full path to 'data.csv'. This can be comma-separated for specific train/val/test files.",
    )
    parser.add_argument(
        "-f",
        "--foldertocopy",
        metavar="",
        default=None,
        type=str,
        help="Full path to the data folder to copy into the location in '/N/scratch/$username'.",
    )
    parser.add_argument(
        "-r",
        "--runnerscript",
        metavar="",
        default=os.path.join(cwd, "runner.sh"),
        type=str,
        help="'runner.sh' script to be called.",
    )
    parser.add_argument(
        "-a",
        "--account",
        metavar="",
        default="a00123",  ## IU-SPECIFIC: you can this information using "sacctmgr show assoc | grep `whoami`" or from the specific projects on https://projects.rt.iu.edu/project
        type=str,
        help="IU account name.",
    )
    parser.add_argument(
        "-e",
        "--email",
        metavar="",
        default="user -at- site.domain",
        type=str,
        help="Email address to be used for notifications.",
    )

    args = parser.parse_args()

    # checks for the arguments
    assert args.account != None, "Please provide an account name."
    assert args.account != "a00123", "Please provide a valid account name."
    assert args.email != None, "Please provide an email address."
    assert (
        args.email != "user -at- site.domain"
    ), "Please provide a valid email address."
    assert args.datafile != None, "Please provide a data file."
    assert args.runnerscript != None, "Please provide a runner script."

    def _number_of_rows_in_csv(filename: str) -> int:
        """
        This is a helper function to count the number of lines in a file

        Args:
            filename (str): Path to the file

        Returns:
            int: Number of lines in the file
        """
        if os.path.isfile(filename):
            with open(filename) as f:
                return sum(1 for line in f)
        else:
            return 0

    all_files_and_folders.sort()
    jobs_that_have_run, jobs_that_have_not_run = 0, 0
    # iterate over all the folders
    for base_experiment_folder in all_files_and_folders:
        current_file_or_folder = os.path.join(cwd, base_experiment_folder)
        if os.path.isdir(current_file_or_folder):
            if base_experiment_folder != ".git":
                print("*****Folder:", base_experiment_folder)
                # change cwd so that logs are generated in single place
                os.chdir(current_file_or_folder)
                files_and_folders_inside = os.listdir(current_file_or_folder)
                files_and_folders_inside.sort()

                for internal_file_or_folder in files_and_folders_inside:
                    # only loop over configs
                    if internal_file_or_folder.endswith(
                        ".yaml"
                    ) or internal_file_or_folder.endswith(".yml"):
                        current_config = os.path.join(
                            current_file_or_folder, internal_file_or_folder
                        )
                        # get the config name
                        config, _ = os.path.splitext(internal_file_or_folder)
                        # automatically set the output directory
                        output_dir = os.path.join(current_file_or_folder, config)
                        Path(output_dir).mkdir(parents=True, exist_ok=True)

                        parameters = yaml.safe_load(open(current_config, "r"))

                        # check if the experiment has already run by checking if at least the number of epochs have been run is greater than the patience set in the config
                        # there are other ways to structure this, but this is the simplest
                        need_to_run = True
                        if os.path.isdir(output_dir):
                            # this is the expected validation logs
                            validation_logs_file = os.path.join(
                                output_dir, "logs_validation.csv"
                            )
                            if (
                                _number_of_rows_in_csv(validation_logs_file)
                                >= parameters["patience"]
                            ):
                                need_to_run = False

                        # if previous results are absent, delete and re-launch
                        if need_to_run:
                            shutil.rmtree(output_dir)
                            Path(output_dir).mkdir(parents=True, exist_ok=True)

                            experiment_name = base_experiment_folder + "_" + config

                            command = (
                                "sbatch -J "
                                + experiment_name
                                + " -A "
                                + args.account
                                + " --mail-user="
                                + args.email
                                + " -e "
                                + output_dir
                                + "/%j.err -o "
                                + output_dir
                                + "/%j.out "
                                + args.runnerscript
                                + " "
                                + args.interpreter
                                + " "
                                + args.gandlfrun  ## old way: this is no longer needed and will be removed in the future
                                + " "
                                + args.datafile
                                + " "
                                + current_config
                                + " "
                                + output_dir
                                + " "
                                + str(args.foldertocopy)
                            )
                            print(command)
                            os.system(command)
                            ## todo: some improvements for experiment tracking
                            # might be a good idea to check the return of the os.system call (which should be the job ID)
                            # put that in a variable
                            # to enable better tracking, construct a csv using experiment_name,job_id,command
                            jobs_that_have_run += 1
                        else:
                            jobs_that_have_not_run += 1

    print(
        f"Submitted jobs:{jobs_that_have_run}; not submitted jobs:{jobs_that_have_not_run}"
    )
