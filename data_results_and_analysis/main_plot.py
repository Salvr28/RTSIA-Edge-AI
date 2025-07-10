from box_plotter import BoxPlotter
import os
import matplotlib.pyplot as plt

def main():

    # --- Boxplot Configuration for experiment: "Impact of stressor on AI workload" ---
    configs1 ={
        'models':{
            'mobilnetV1':{
                'model_name': 'mobilnetV1',
                'data_path': os.path.join('stress_on_ai_data', 'mobilnetV1'),
                'color': 'lightcoral'
            },
            'mobilnetV2':{
                'model_name': 'mobilnetV2',
                'data_path': os.path.join('stress_on_ai_data', 'mobilnetV2'),
                'color': 'lightblue'
            }

        },
        'stressors':[
            'no_stress',
            'cpu',
            'vm',
            'memcpy',
            'open',
            'irq',
            'fork',
            'udp'
        ]
    }

    configs2 ={
        'models':{
            'ssd_mobilnetV1':{
                'model_name': 'ssd_mobilnetV1',
                'data_path': os.path.join('stress_on_ai_data', 'ssd_mobilnetV1'),
                'color': 'mediumorchid'
            },
            'ssd_mobilnetV2':{
                'model_name': 'ssd_mobilnetV2',
                'data_path': os.path.join('stress_on_ai_data', 'ssd_mobilnetV2'),
                'color': 'sienna'
            }

        },
        'stressors':[
            'no_stress',
            'cpu',
            'vm',
            'memcpy',
            'open',
            'irq',
            'fork',
            'udp'
        ]
    }

    # --- Boxplot Configuration for experiment: "Impact of AI workload on Real-Time Task" ---
    configs_isolation_comparison = {
        'models': {
            'BASELINE': {
                'not_isolated_path': os.path.join('cyclic_test_not_isolated_data', 'baseline_not_isolated.txt'),
                'isolated_path': os.path.join('cyclic_test_isolated_data', 'baseline_isolated.txt')
            },
            'mobilenetV1': {
                'not_isolated_path': os.path.join('cyclic_test_not_isolated_data', 'mobilnetV1_not_isolated.txt'),
                'isolated_path': os.path.join('cyclic_test_isolated_data', 'mobilnetV1_isolated.txt')
            },
            'mobilenetV2': {
                'not_isolated_path': os.path.join('cyclic_test_not_isolated_data', 'mobilnetV2_not_isolated.txt'),
                'isolated_path': os.path.join('cyclic_test_isolated_data', 'mobilnetV2_isolated.txt')
            },
            'ssd_mobilenetV1': {
                'not_isolated_path': os.path.join('cyclic_test_not_isolated_data', 'ssd_mobilnetV1_not_isolated.txt'),
                'isolated_path': os.path.join('cyclic_test_isolated_data', 'ssd_mobilnetV1_isolated.txt')
            },
            'ssd_mobilenetV2': {
                'not_isolated_path': os.path.join('cyclic_test_not_isolated_data', 'ssd_mobilnetV2_not_isolated.txt'),
                'isolated_path': os.path.join('cyclic_test_isolated_data', 'ssd_mobilnetV2_isolated.txt')
            }
        },
        'colors': {
            'NOT ISOLATED': 'indianred',
            'ISOLATED': 'springgreen'
        }
    }

    box_plotter1 = BoxPlotter(configs1)
    fig1, ax1 = box_plotter1.plots_data()
    box_plotter2 = BoxPlotter(configs2)
    fig2, ax2 = box_plotter2.plots_data()
    box_plotter_comparison = BoxPlotter(configs_isolation_comparison)
    fig_comp, ax_comp = box_plotter_comparison.plot_isolation_comparison()


    plt.show()

if __name__=="__main__":
    main()
