import gradio as gr

import pandas as pd

import birdnet_analyzer.config as cfg
import birdnet_analyzer.gui.localization as loc
import birdnet_analyzer.gui.utils as gu

TIMER_TICK_INTERVAL = 0.5

@gu.gui_runtime_error_handler
def run_real_time_analysis(
    input_path,
    use_top_n,
    top_n,
    confidence,
    sensitivity,
    overlap,
    merge_consecutive,
    audio_speed,
    fmin,
    fmax,
    species_list_choice,
    species_list_file,
    lat,
    lon,
    week,
    use_yearlong,
    sf_thresh,
    custom_classifier_file,
    locale,
    loopback
):

    from birdnet_analyzer.gui.analysis import run_analysis

    if species_list_choice == gu._CUSTOM_SPECIES:
        gu.validate(species_list_file, loc.localize("validation-no-species-list-selected"))

    if fmin is None or fmax is None or fmin < cfg.SIG_FMIN or fmax > cfg.SIG_FMAX or fmin > fmax:
        raise gr.Error(f"{loc.localize('validation-no-valid-frequency')} [{cfg.SIG_FMIN}, {cfg.SIG_FMAX}]")

    # call run_analysis in real-time mode
    run_analysis(
        input_path=input_path,
        output_path=None,
        use_top_n=use_top_n,
        top_n=top_n,
        confidence=confidence,
        sensitivity=sensitivity,
        overlap=overlap,
        merge_consecutive=merge_consecutive,
        audio_speed=audio_speed,
        fmin=fmin,
        fmax=fmax,
        species_list_choice=species_list_choice,
        species_list_file=species_list_file,
        lat=lat,
        lon=lon,
        week=week,
        use_yearlong=use_yearlong,
        sf_thresh=sf_thresh,
        custom_classifier_file=custom_classifier_file,
        output_types="csv",
        additional_columns=None,
        combine_tables=False,
        locale=locale if locale else "en",
        batch_size=1,
        threads=4,
        input_dir=None,
        skip_existing=False,
        save_params=False,
        progress=None,
        real_time=True,
        loopback=loopback,
        non_stop=True,
        input_device=None,
    )

def build_real_time_analysis_tab():
    with gr.Tab(loc.localize("real-time-tab-title")):

        # dummy audio file path object (not used in real-time mode but required arg for run_analysis)
        audio_path_state = gr.State(value="./")

        # same settings as in other tabs
        sample_settings, species_settings = gu.sample_and_species_settings(opened=False)

        with gr.Row():
            # checkbox for loopback mode selection
            loopback_cb = gr.Checkbox(
                value=False, 
                label=loc.localize("real-time-tab-loopback-checkbox-label"),
                info=loc.localize("real-time-tab-loopback-checkbox-info")
            )
            locale_radio = gu.locale()


        # buttons to start/stop real-time audio analysis
        with gr.Row():
            start_rt_button = gr.Button(loc.localize("real-time-tab-start-button-label"), variant="huggingface", interactive=True, elem_id='real-time-start')
            stop_rt_button = gr.Button(loc.localize("real-time-tab-stop-button-label"), variant="huggingface", interactive=False, elem_id='real-time-stop')        
        inputs = [
            audio_path_state,
            sample_settings["use_top_n_checkbox"],
            sample_settings["top_n_input"],
            sample_settings["confidence_slider"],
            sample_settings["sensitivity_slider"],
            sample_settings["overlap_slider"],
            sample_settings["merge_consecutive_slider"],
            sample_settings["audio_speed_slider"],
            sample_settings["fmin_number"],
            sample_settings["fmax_number"],
            species_settings["species_list_radio"],
            species_settings["species_file_input"],
            species_settings["lat_number"],
            species_settings["lon_number"],
            species_settings["week_number"],
            species_settings["yearlong_checkbox"],
            species_settings["sf_thresh_number"],
            species_settings["selected_classifier_state"],
            locale_radio,
            loopback_cb
        ]
        start_rt_button.click(run_real_time_analysis, inputs=inputs)
        def update_stop_flag():
            tmp_cfg = cfg.get_config()
            if not tmp_cfg['REAL_TIME_STOP_FLAG']:
                tmp_cfg['REAL_TIME_STOP_FLAG'] = True
                tmp_cfg['REAL_TIME_START_FLAG'] = False
                cfg.set_config(tmp_cfg)
            return gr.update(value=loc.localize("real-time-tab-start-button-label"), interactive=True), gr.update(value=loc.localize("real-time-tab-stop-button-label"), interactive=False)
        stop_rt_button.click(update_stop_flag, outputs=[start_rt_button, stop_rt_button])

        # buttons to save/clear output dataframe
        with gr.Row():
            save_rt_button = gr.Button(loc.localize("real-time-tab-save-button-label"), variant="huggingface", interactive=True)
            clear_rt_button = gr.Button(loc.localize("real-time-tab-clear-button-label"), variant="huggingface", interactive=True)

        # real-time analysis results dataframe
        REAL_TIME_OUTPUT_DATAframe = gr.Dataframe(
            type="pandas",
            headers=[
                loc.localize("single-tab-output-header-start"),
                loc.localize("single-tab-output-header-end"),
                loc.localize("single-tab-output-header-sci-name"),
                loc.localize("single-tab-output-header-common-name"),
                loc.localize("single-tab-output-header-confidence"),
            ],
            elem_id="single-file-output",
            interactive=False,
        )

        def save_dataframe_with_dialog(df: pd.DataFrame):
            file_path = gu.save_file_dialog(
                filetypes=("CSV Files (*.csv)",),
                state_key="last_save_dir",
                default_filename="BirdNET_real_time_analysis_results.csv"
            )
            if file_path:
                df.to_csv(file_path, index=False)
        save_rt_button.click(save_dataframe_with_dialog, inputs=REAL_TIME_OUTPUT_DATAframe)
        def clear_REAL_TIME_OUTPUT_DATAframe():
            tmp_cfg = cfg.get_config()
            tmp_cfg['REAL_TIME_OUTPUT_DATA'] = []
            cfg.set_config(tmp_cfg)
            return []
        clear_rt_button.click(clear_REAL_TIME_OUTPUT_DATAframe,outputs=REAL_TIME_OUTPUT_DATAframe)

        output_update_timer = gr.Timer(TIMER_TICK_INTERVAL)
        def get_rt_output():
            tmp_cfg = cfg.get_config()
            if tmp_cfg['REAL_TIME_START_FLAG']:
                return tmp_cfg['REAL_TIME_OUTPUT_DATA'],gr.update(value=loc.localize("real-time-tab-running-label"), interactive=False), gr.update(value=loc.localize("real-time-tab-stop-button-label"), interactive=True)
            else:
                return tmp_cfg['REAL_TIME_OUTPUT_DATA'],gr.update(value=loc.localize("real-time-tab-start-button-label"), interactive=True), gr.update(value=loc.localize("real-time-tab-stop-button-label"), interactive=False)
        output_update_timer.tick(get_rt_output,outputs=[REAL_TIME_OUTPUT_DATAframe,start_rt_button,stop_rt_button])

if __name__ == "__main__":
    gu.open_window(build_real_time_analysis_tab)
