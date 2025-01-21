settings put global window_animation_scale 0 && settings put global transition_animation_scale 0 && settings put global animator_duration_scale 0 && settings put global settings_system_manager_max_cpuload 5 && settings put global enable_gpu_debug_layers 1 && settings put global disable_overlays 1 && settings put global low_power 0
settings put global force_gpu_rendering 1
setprop debug.performance.tuning 1
settings put global force_gpu_rendering 1
settings put global master_sync_enabled 0
settings put global window_animation_scale 0
settings put global transition_animation_scale 0
settings put global animator_duration_scale 0
setprop debug.sys.fw.bg_apps_limit 4
settings put secure location_providers_allowed -gps,-network
pm disable-user --user 0 com.android.mms
pm disable-user --user 0 com.google.android.apps.photos
