import gradio as gr

import birdnet_analyzer.config as cfg
import birdnet_analyzer.gui.localization as loc
import birdnet_analyzer.gui.utils as gu

@gu.gui_runtime_error_handler
def run_live_analysis(
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
        non_stop=False,
        input_device=None,
    )

def build_live_analysis_tab():
    with gr.Tab(loc.localize("live-tab-title")):

        # checkbox for loopback mode selection
        loopback_cb = gr.Checkbox(
            value=False, 
            label=loc.localize("live-tab-loopback-checkbox-label"),
            info=loc.localize("live-tab-loopback-checkbox-info")
        )
            
        # dummy audio file path object (not used in real-time mode but required arg for run_analysis)
        audio_path_state = gr.State(value="./")

        # same settings as in other tabs
        sample_settings, species_settings = gu.sample_and_species_settings(opened=False)
        locale_radio = gu.locale()

        # buttons to start/stop live audio analysis
        with gr.Row():
            start_live_analysis_button = gr.Button(loc.localize("live-tab-start-button-label"), variant="huggingface", interactive=True)
            stop_live_analysis = gr.Button(loc.localize("live-tab-stop-button-label"), variant="huggingface", interactive=True)
        
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
            loopback_cb,
        ]
        start_live_analysis_button.click(run_live_analysis, inputs=inputs)

        
        def update_stop_flag():
            tmp_cfg = cfg.get_config()
            # print(tmp_cfg)
            if not tmp_cfg['LIVE_STOP_FLAG']:
                tmp_cfg['LIVE_STOP_FLAG'] = True
                cfg.set_config(tmp_cfg)
        stop_live_analysis.click(update_stop_flag)

if __name__ == "__main__":
    gu.open_window(build_live_analysis_tab)
