import os, sys, argparse, shutil
from datetime import date
from distutils.dir_util import copy_tree

if __name__ == "__main__":
    copyrightMessage = (
        "Contact: patis@iu.edu\n\n"
        + "This program is NOT FDA/CE approved and NOT intended for clinical use.\nCopyright (c) "
        + str(date.today().year)
        + " Indiana University. All rights reserved."
    )
    parser = argparse.ArgumentParser(
        prog="GANDLF_Experiment_Submitter_Scratch_Space_Handler",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Submit GaNDLF experiments on IU Cluster (Big Red, Quartz).\n\n"
        + copyrightMessage,
    )

    parser.add_argument(
        "-g",
        "--gandlfrun",
        metavar="",
        default="/cbica/home/patis/comp_space/testing/gandlf_mine/gandlf_run",
        type=str,
        help="Full path of 'gandlf_run' script to be called.",
    )
    parser.add_argument(
        "-d",
        "--datafile",
        metavar="",
        default=None,
        type=str,
        help="Full path to 'data.csv'.",
    )
    parser.add_argument(
        "-o",
        "--outputdir",
        metavar="",
        default=None,
        type=str,
        help="Full path to 'data.csv'.",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="",
        default=None,
        type=str,
        help="Full path to 'data.csv'.",
    )
    parser.add_argument(
        "-f",
        "--foldertocopy",
        metavar="",
        default=None,
        type=str,
        help="Full path to the data folder to copy into the location in '$CBICA_TMP'.",
    )

    args = parser.parse_args()

    ## special check for $CBICA_TMPDIR
    tempdir = None
    if "CBICA_TMPDIR" in os.environ:
        if args.foldertocopy is not None:
            if args.foldertocopy != "None":
                tempdir = os.environ["CBICA_TMPDIR"]
                print("Copying data folder to $CBICA_TMPDIR.")
                new_data_dir = os.path.join(tempdir, "data")
                copy_tree(args.foldertocopy, new_data_dir)

                print("Updating paths in csv files.")
                data_files_to_replace_path = args.datafile.split(",")
                new_data_files = ""
                new_data_files_to_delete = []
                for data_file in data_files_to_replace_path:
                    new_data_filename = os.path.join(
                        tempdir, os.path.basename(data_file)
                    )
                    new_data_files = new_data_filename + ","
                    new_data_files_to_delete.append(new_data_filename)
                    with open(data_file, "r") as f:
                        lines = f.readlines()
                    with open(new_data_filename, "w") as f:
                        for line in lines:
                            line = line.replace(args.foldertocopy, new_data_dir)
                            f.write(line)

                args.datafile = new_data_files[:-1]

    command_to_run = (
        sys.executable
        + " "
        + args.gandlfrun
        + " --inputdata "
        + args.datafile
        + " --modeldir "
        + args.outputdir
        + " --config "
        + args.config
        + " --train True --reset True --device cuda"
    )
    print("Running command: " + command_to_run)
    os.system(command_to_run)

    if tempdir is not None:
        shutil.rmtree(new_data_dir)
        for data_file in new_data_files_to_delete:
            os.remove(data_file)
