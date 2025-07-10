import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

class BoxPlotter():

    def __init__(self, configs):
        self.configs = configs
        self.models = self.configs['models']

    def plots_data(self):
        """
        Plots AI Inference times comparing different AI models in different stress conditions
        """
        
        stress_labels = self.configs['stressors']
        model_names = list(self.models.keys())
        num_models_per_group = len(model_names) # A boxplot for each stressor

        fig, ax = plt.subplots(1, 1, figsize=(1.2 * len(stress_labels) * num_models_per_group, 7))

        ax.set_ylabel('Inference time (ms)', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.tick_params(axis='y', which='both', left=True, right=True, labelleft=True)

        legend_patches = []
        for model_name in model_names:
            color = self.models[model_name]['color']
            legend_patches.append(mpatches.Patch(color=color, label=model_name))

        # Global counter for boxplot position, on x ax
        global_boxplot_position_counter = 0

        # tick and label lists, to ensure final position
        overall_stress_tick_positions = []
        overall_stress_tick_labels = []

        # Iterating through each stressor (a stressor is a square)
        for i, stress_type in enumerate(stress_labels):

            # BoxPlot initial position for this group
            current_group_start_position = global_boxplot_position_counter + 1

            inference_data_for_current_group = []
            boxplot_positions_for_current_group = []

            # Internal cicle: one iteration for each model in the stressor box
            for j, (model_name, model_dict) in enumerate(self.models.items()):
                file_path = os.path.join(model_dict['data_path'], f"{stress_type}.txt")

                try:
                    inference_times = np.loadtxt(file_path, dtype=float)
                    inference_data_for_current_group.append(inference_times)

                    # The boxplot position in the global ax X context
                    position_for_this_boxplot = current_group_start_position + j
                    boxplot_positions_for_current_group.append(position_for_this_boxplot)

                    # Update global counter
                    global_boxplot_position_counter = position_for_this_boxplot
                except FileNotFoundError:
                    print(f"Warning: Data file not found for model '{model_name}' under stress '{stress_type}': {file_path}")
                    continue
                except Exception as e:
                    print(f"Error loading data for model '{model_name}' under stress '{stress_type}': {e}")
                    continue

            # --- Drawing all boxplot for the current stress group ---
            if inference_data_for_current_group:
                bplot = ax.boxplot(inference_data_for_current_group,
                                   positions=boxplot_positions_for_current_group,
                                   widths=0.6,
                                   patch_artist=True,
                                   medianprops=dict(color='orange', linewidth=1.5),
                                   showfliers=True)

                # Painting boxplot
                for k, patch in enumerate(bplot['boxes']):
                    patch.set_facecolor(self.models[model_names[k]]['color'])
            else:
                # Placeholder if there aren't data
                placeholder_x = current_group_start_position + (num_models_per_group - 1) / 2
                ax.text(placeholder_x, ax.get_ylim()[0] * 1.5, 'No Data',
                        horizontalalignment='center', verticalalignment='bottom',
                        color='gray', fontsize=10)


            if boxplot_positions_for_current_group:
                center_of_current_group = (min(boxplot_positions_for_current_group) + max(boxplot_positions_for_current_group)) / 2
            else:
                 center_of_current_group = current_group_start_position + (num_models_per_group - 1) / 2

            overall_stress_tick_positions.append(center_of_current_group)
            overall_stress_tick_labels.append(stress_type)

            if i < len(stress_labels) - 1:
                line_x_position = global_boxplot_position_counter + 0.5
                ax.axvline(x=line_x_position, color='gray', linestyle='--', linewidth=1, clip_on=False)

        ax.set_xticks(overall_stress_tick_positions)
        ax.set_xticklabels(overall_stress_tick_labels, rotation=45, ha='center')

        ax.set_xlim(0.5, global_boxplot_position_counter + 0.5)

        ax.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(0.98, 0.98), frameon=True)


        plt.tight_layout(rect=[0, 0, 0.88, 1])

        return fig, ax

    def plot_isolation_comparison(self):
        """
        Plots cyclictest max latency values during AI inference. It compares different types
        of AI inference disturbs (different models).
        """

        # A boxplot for each model
        model_names = list(self.models.keys())
        num_isolation_types = 2

        boxplot_width = 0.6
        gap_within_group = 0.2
        gap_between_groups = 0.8

        fig_width = len(model_names) * (2.5 * boxplot_width + gap_within_group + gap_between_groups)
        fig, ax = plt.subplots(1, 1, figsize=(fig_width, 7))

        ax.set_ylabel('Max Latency (us)', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.tick_params(axis='y', which='both', left=True, right=True, labelleft=True)

        legend_patches = [
            mpatches.Patch(color=self.configs['colors']['NOT ISOLATED'], label='NOT ISOLATED'),
            mpatches.Patch(color=self.configs['colors']['ISOLATED'], label='ISOLATED')
        ]

        # Counter to set model's boxplot in the fig
        global_boxplot_position_counter = 0

        overall_x_tick_positions = []
        overall_x_tick_labels = []

        # Iterating through models
        for i, model_name in enumerate(model_names):

            # Comparing two enviroment, isolated and not isolated cpu
            # Each area will have two boxplot for one model, one for each configuration
            not_isolated_file_path = self.models[model_name]['not_isolated_path']
            isolated_file_path = self.models[model_name]['isolated_path']

            data_for_current_model_group = []
            boxplot_positions_for_current_model_group = []

            try:
                # Loading not isolated data from files
                not_isolated_data = np.loadtxt(not_isolated_file_path, dtype=float)
                data_for_current_model_group.append(not_isolated_data)
                position_not_isolated = global_boxplot_position_counter + 1
                boxplot_positions_for_current_model_group.append(position_not_isolated)
            except FileNotFoundError:
                print(f"Warning: File non isolato non trovato per '{model_name}': {not_isolated_file_path}")
                data_for_current_model_group.append([])
                position_not_isolated = global_boxplot_position_counter + 1
                boxplot_positions_for_current_model_group.append(position_not_isolated)
            except Exception as e:
                print(f"Errore caricamento dati non isolati per '{model_name}': {e}")
                data_for_current_model_group.append([])
                position_not_isolated = global_boxplot_position_counter + 1
                boxplot_positions_for_current_model_group.append(position_not_isolated)

            try:
                # Loading isolated data from files
                isolated_data = np.loadtxt(isolated_file_path, dtype=float)
                data_for_current_model_group.append(isolated_data)
                position_isolated = position_not_isolated + boxplot_width + gap_within_group
                boxplot_positions_for_current_model_group.append(position_isolated)
            except FileNotFoundError:
                print(f"Warning: File isolato non trovato per '{model_name}': {isolated_file_path}")
                data_for_current_model_group.append([])
                position_isolated = position_not_isolated + boxplot_width + gap_within_group
                boxplot_positions_for_current_model_group.append(position_isolated)
            except Exception as e:
                print(f"Errore caricamento dati isolati per '{model_name}': {e}")
                data_for_current_model_group.append([])
                position_isolated = position_not_isolated + boxplot_width + gap_within_group
                boxplot_positions_for_current_model_group.append(position_isolated)

            # Check data 
            valid_data_for_boxplot = [d for d in data_for_current_model_group if len(d) > 0]
            valid_positions_for_boxplot = [p for p, d in zip(boxplot_positions_for_current_model_group, data_for_current_model_group) if len(d) > 0]

            # Building the boxplot
            if valid_data_for_boxplot:
                bplot = ax.boxplot(valid_data_for_boxplot,
                                   positions=valid_positions_for_boxplot,
                                   widths=boxplot_width,
                                   patch_artist=True,
                                   medianprops=dict(color='orange', linewidth=1.5),
                                   showfliers=True)

                color_index = 0
                if len(data_for_current_model_group[0]) > 0:
                    bplot['boxes'][color_index].set_facecolor(self.configs['colors']['NOT ISOLATED'])
                    color_index += 1
                if len(data_for_current_model_group[1]) > 0:
                    bplot['boxes'][color_index].set_facecolor(self.configs['colors']['ISOLATED'])

            else:
                placeholder_x = (boxplot_positions_for_current_model_group[0] + boxplot_positions_for_current_model_group[1]) / 2
                ax.text(placeholder_x, ax.get_ylim()[0] * 1.5, 'No Data',
                                 horizontalalignment='center', verticalalignment='bottom',
                                 color='gray', fontsize=10)


            # Update global counter 
            global_boxplot_position_counter = max(boxplot_positions_for_current_model_group)

            # Calculating position for model label, centering it
            center_of_current_model_group = (boxplot_positions_for_current_model_group[0] + boxplot_positions_for_current_model_group[1]) / 2
            overall_x_tick_positions.append(center_of_current_model_group)
            overall_x_tick_labels.append(model_name)

            if i < len(model_names) - 1:
                line_x_position = global_boxplot_position_counter + (gap_between_groups / 2)
                ax.axvline(x=line_x_position, color='gray', linestyle='--', linewidth=1, clip_on=False)
                global_boxplot_position_counter += gap_between_groups

        # Setting all parameters to axis
        ax.set_xticks(overall_x_tick_positions)
        ax.set_xticklabels(overall_x_tick_labels, rotation=45, ha='center')

        ax.set_xlim(0.5, global_boxplot_position_counter + boxplot_width + 0.5)

        fig.legend(handles=legend_patches, loc='upper right', bbox_to_anchor=(0.98, 0.98), frameon=True)

        plt.tight_layout(rect=[0, 0, 0.88, 1])

        return fig, ax
