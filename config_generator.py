import os, yaml, pandas, argparse, ast, fileinput, tempfile, shutil
from datetime import date
from pathlib import Path


## detect "_per_label" metrics
def detect_per_label_metrics(filename):
    """
    This function detects if the file contains triaged (i.e., metrics split per label) per_label metrics or not

    Args:
        filename (str): The log file to check.

    Returns:
        bool: True if the file contains triaged per_label metrics or does not contain per_label stats, False otherwise.
    """
    with open(filename, "r") as fp:
        header = fp.readline()
    if "_per_label" in header:
        if "_per_label_" in header:
            # in this case, the per label triage has already happened
            return False
        else:
            return True
    else:
        return False


if __name__ == "__main__":
    copyrightMessage = (
        "Contact: patis@iu.edu\n\n"
        + "This program is NOT FDA/CE approved and NOT intended for clinical use.\nCopyright (c) "
        + str(date.today().year)
        + " Indiana University. All rights reserved."
    )

    cwd = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        prog="GANDLF_Experiment_Submitter_Config_Generator",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Submit GaNDLF experiments on IU Cluster (Big Red, Quartz).\n\n"
        + copyrightMessage,
    )

    parser.add_argument(
        "-c",
        "--config",
        metavar="",
        default=True,
        type=ast.literal_eval,
        help="Generate config or not. If false, tries to generate succinct information about training.",
    )
    args = parser.parse_args()

    if args.config:
        ## make sure you have a baseline configuration somewhere
        base_config = os.path.join(cwd, "config.yaml")

    #### update configurations to be trained
    ### this example is to generate multiple configs based on schedulers and learning rates
    # learning_rates = [0.1, 0.01, 0.001, 0.0001]
    # schedulers = ["exponential", "step", "reduce_on_plateau", "cosineannealing"]

    # for sched in schedulers:
    #     base_output_dir = os.path.join(cwd, sched)
    #     pathlib.Path(base_output_dir).mkdir(parents=True, exist_ok=True)

    #     for lr in learning_rates:
    #         with open(base_config, "r") as f:
    #             config = yaml.safe_load(f)
    #         config["learning_rate"] = lr
    #         config["scheduler"] = sched
    #         config["opt"] = "sgd"

    #         with open(os.path.join(base_output_dir, str(lr) + ".yaml"), "w") as f:
    #             yaml.dump(config, f)

    ### this example is to generate multiple configs based on a single scheduler (exponential), learning rate (0.01) and different gammas
    # gamma_vals = [1, 0.01, 0.001, 0.0001]

    # current_config_dir = os.path.join(cwd, "exponential")
    # pathlib.Path(current_config_dir).mkdir(parents=True, exist_ok=True)
    # for gamma in gamma_vals:
    #     config_to_write = os.path.join(current_config_dir, "gamma_" + str(gamma) + ".yaml")

    #     with open(base_config, "r") as f:
    #         config = yaml.safe_load(f)
    #     config["learning_rate"] = 0.01
    #     config["scheduler"] = {}
    #     config["scheduler"]["gamma"] = gamma
    #     config["scheduler"]["type"] = "exponential"

    #     with open(config_to_write, "w") as f:
    #         yaml.dump(config, f)

    ## this example is to generate multiple configs based on different batch sizes
    # batch_sizes = [48, 52, 58]

    # output_dir = os.path.join(cwd, "B")
    # os.makedirs(output_dir, exist_ok=True)

    # for batch in batch_sizes:
    #     config = os.path.join(output_dir, str(batch) + ".yaml")
    #     with open(base_config, "r") as f:
    #         config_dict = yaml.safe_load(f)
    #     config_dict["batch_size"] = batch
    #     with open(config, "w") as f:
    #         yaml.dump(config_dict, f)

    else:
        # get information about best config
        dirs_in_cwd = os.listdir(cwd)
        dirs_in_cwd.sort()
        best_info = {"config": [], "train_epoch": [], "valid_epoch": []}
        ## populate the metrics to be shown - example shown for classification
        metrics_to_populate = ["loss", "balanced_accuracy", "accuracy"]
        metrics_calculated_per_label = ["accuracy"]  # not always present
        for metric in metrics_to_populate:
            for type in ["train", "valid"]:
                best_info[type + "_" + metric] = []

        for dir in dirs_in_cwd:
            current_dir = os.path.join(cwd, dir)
            if os.path.isdir(current_dir):
                print("Current directory: ", current_dir)
                config_outputs_in_dir = os.listdir(current_dir)
                config_outputs_in_dir.sort()
                files_and_folders_inside = os.listdir(current_dir)
                files_and_folders_inside.sort()
                for internal_file_or_folder in files_and_folders_inside:
                    if internal_file_or_folder.endswith(
                        ".yaml"
                    ) or internal_file_or_folder.endswith(".yml"):
                        current_config = os.path.join(
                            current_dir, internal_file_or_folder
                        )
                        config = yaml.safe_load(open(current_config))
                        assert (
                            "model" in config
                        ), "The 'model' attribute was not found in config"
                        if "num_classes" in config["model"]:
                            number_of_classes = config["model"]["num_classes"]
                        elif "class_list" in config["model"]:
                            number_of_classes = len(config["model"]["class_list"])
                        else:
                            number_of_classes = 0
                            print(
                                "The number of classes could not be determined from the config file:",
                                current_config,
                            )

                        config_output_dir = os.path.join(
                            current_dir, internal_file_or_folder.split(".")[0]
                        )
                        if os.path.isdir(config_output_dir):
                            print("Current config output: ", config_output_dir)
                            file_logs_training = os.path.join(
                                config_output_dir, "logs_training.csv"
                            )
                            file_logs_validation = os.path.join(
                                config_output_dir, "logs_validation.csv"
                            )
                            if os.path.isfile(file_logs_training) and os.path.isfile(
                                file_logs_validation
                            ):
                                with open(file_logs_training, "r") as fp:
                                    len_logs_training = len(fp.readlines())
                                with open(file_logs_validation, "r") as fp:
                                    len_logs_validation = len(fp.readlines())
                                # ensure something other than the log headers have been written
                                if len_logs_training > 2 and len_logs_validation > 2:
                                    temp_dir = tempfile.gettempdir()
                                    Path(temp_dir).mkdir(parents=True, exist_ok=True)
                                    new_train_file = os.path.join(
                                        temp_dir, "logs_training.csv"
                                    )
                                    shutil.copyfile(file_logs_training, new_train_file)
                                    new_valid_file = os.path.join(
                                        temp_dir, "logs_validation.csv"
                                    )
                                    shutil.copyfile(
                                        file_logs_validation, new_valid_file
                                    )

                                    assert not detect_per_label_metrics(
                                        new_train_file
                                    ), "Per label metrics detected in training logs - update metrics_calculated_per_label with correct information, and comment these lines to ensure correct parsing"
                                    assert not detect_per_label_metrics(
                                        new_valid_file
                                    ), "Per label metrics detected in validation logs - update metrics_calculated_per_label with correct information, and comment these lines to ensure correct parsing"

                                    ### replace the per_label metric header information to ensure correct parsing - change as needed
                                    def get_new_header(cohort):
                                        return_string = "epoch_no," + cohort + "_loss,"
                                        for metric in metrics_calculated_per_label:
                                            if metric != "loss":
                                                return_string += (
                                                    cohort
                                                    + "_"
                                                    + metric
                                                    + ","
                                                    + ",".join(
                                                        [
                                                            cohort
                                                            + "_"
                                                            + metric
                                                            + "_per_label_"
                                                            + str(i)
                                                            for i in range(
                                                                number_of_classes
                                                            )
                                                        ]
                                                    )
                                                    + ","
                                                )
                                        return return_string

                                    def replace_per_label_metrics(filename, new_header):
                                        for line in fileinput.input(
                                            filename, inplace=True
                                        ):
                                            if fileinput.isfirstline():
                                                if "_dice_per_label" in line:
                                                    if "_dice_per_label_" in line:
                                                        # this means the per label metrics have already been replaced
                                                        print(line)
                                                    else:
                                                        print(new_header)
                                            else:
                                                print(line)

                                    replace_per_label_metrics(
                                        new_train_file, get_new_header("train")
                                    )
                                    replace_per_label_metrics(
                                        new_valid_file, get_new_header("valid")
                                    )
                                    ### replace the per_label metric header information to ensure correct parsing - change as needed
                                    ## sort by loss
                                    best_train_loss_row = (
                                        pandas.read_csv(new_train_file)
                                        .sort_values(by="train_loss", ascending=True)
                                        .iloc[0]
                                    )
                                    best_valid_loss_row = (
                                        pandas.read_csv(new_valid_file)
                                        .sort_values(by="valid_loss", ascending=True)
                                        .iloc[0]
                                    )
                                    best_info["config"].append(
                                        dir + "_" + internal_file_or_folder
                                    )
                                    best_info["train_epoch"].append(
                                        best_train_loss_row["epoch_no"]
                                    )
                                    best_info["valid_epoch"].append(
                                        best_valid_loss_row["epoch_no"]
                                    )
                                    shutil.rmtree(temp_dir)
                                    for type in ["train", "valid"]:
                                        for metric in metrics_to_populate:
                                            if type == "train":
                                                best_info[
                                                    "{}_{}".format(type, metric)
                                                ].append(
                                                    best_train_loss_row[
                                                        "{}_{}".format(type, metric)
                                                    ]
                                                )
                                            else:
                                                best_info[
                                                    "{}_{}".format(type, metric)
                                                ].append(
                                                    best_valid_loss_row[
                                                        "{}_{}".format(type, metric)
                                                    ]
                                                )

        pandas.DataFrame.from_dict(best_info).to_csv(
            os.path.join(cwd, "best_info.csv"), index=False
        )
