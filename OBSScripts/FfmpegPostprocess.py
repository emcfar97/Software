import obspython as obs
import subprocess
import os
import re
import datetime

# Info for potential OBS Python hackers!
# Tip 1 - Read the "OBS Studio Backend Design" documentation page. Read the documentation table of contents.
# Tip 2 - be sure to add obspython.py to your script path to enable completion.
# Tip 3 - Some of the Python API is generated at runtime, so it won't show up in obspython.py.
#         To search the full API for e.g. "frontend" functions, uncomment this line and reload your script:
# [print(i) for i in dir(obs) if i.lower().find("frontend") > -1]

# Tip 4 - Here's a set of ffmpeg flags to produce mobile-ready Telegram mp4s:
#            -an -vf scale=-1:720:flags=lanczos -vprofile baseline -pix_fmt yuv420p

class OBSDataModel:
    """Interact with an obs_data more comfortably using Python type checking.
    This class models a single obs_data object at a time.
    This ffmpeg plugin only ever interacts with a single "properties" data object, corresponding to user input boxes
    in the script settings.

    There are two access methods:
    1. Store config data persistently with store_data() and load_data().
    2. Non-persistent access with [] syntax: useful when the obs_data object is unavailable, eg. external callbacks.

    Initialized with a dict containing the names and default values of the data items.
    """
    getter_fun = {bool: obs.obs_data_get_bool, str: obs.obs_data_get_string,
                  int: obs.obs_data_get_int, float: obs.obs_data_get_double}
    setter_fun = {bool: obs.obs_data_set_bool, str: obs.obs_data_set_string,
                  int: obs.obs_data_set_int, float: obs.obs_data_set_double}
    default_fun = {bool: obs.obs_data_set_default_bool, str: obs.obs_data_set_default_string,
                   int: obs.obs_data_set_default_int, float: obs.obs_data_set_default_double}
    data_dict = None

    def __init__(self, default_dict):
        self.data_dict = default_dict

    def __getitem__(self, arg):
        return self.data_dict[arg]

    def __setitem__(self, arg, value):
        self.data_dict[arg] = value

    def store_data(self, obs_data, name, value):
        self.data_dict[name] = value
        self.setter_fun[type(value)](obs_data, name, value)

    def load_data(self, obs_data, name):
        self.data_dict[name] = self.getter_fun[type(self.data_dict[name])](obs_data, name)
        return self.data_dict[name]

    def set_data_defaults(self, obs_data):
        """First, default values for obs_data items according to contents of data_dict.
        Then synchronizes data_dict with obs_data."""
        for name, value in self.data_dict.items():
            self.default_fun[type(value)](obs_data, name, value)
            self.load_data(obs_data, name)


class OBSPluginFfmpeg(OBSDataModel):
    """ Main class implementing OBS Ffmpeg Python Plugin."""

    # Default values for script options
    _defaults = ({"debug_enabled": False,
                  "auto_convert": True,
                  "src_regex": "",
                  "dst_regex": "",
                  "src_regex_validated": str(datetime.datetime.now().year),
                  "dst_regex_validated": "%SCENE%_" + str(datetime.datetime.now().year),
                  "record_folder": os.path.expanduser("~") + os.path.sep + "Videos",
                  "custom_flags": "-vf scale=-1:720:flags=lanczos"
                  })

    description = "<b>Ffmpeg Auto-converter</b>" + \
                  "<hr>" + \
                  "Automatically transcode OBS output with ffmpeg. Supports renaming with Python regular expressions. " + \
                  "Make sure ffmpeg is in the system path!<br/><br/>" + \
                  "Additional renaming tokens:<br/>" + \
                  "%SCENE% - name of current scene <br/>" + \
                  "%SRC1% - input source 1 (SRC2 for source 2, etc.)" + \
                  "<br/><br/>" + \
                  "©2018 Michael Abrahams. GPLv3 license." + \
                  "<hr>"

    # We install a callback in this signal handler to run ffmpeg when recording is finished
    recording_signal_handler = None

    last_ffmpeg_output = ""

    def __init__(self):
        super().__init__(self._defaults)

    def debug(self, text):
        if self['debug_enabled']:
            print(text)

    def set_defaults(self, settings):
        self.set_data_defaults(settings)
        self.debug(f"_____ script_defaults()\n Saved settings data:\n {obs.obs_data_get_json(settings)}")

    def load(self, settings):
        # Initialize text fields to the last fully validated version
        self.store_data(settings, "src_regex", self["src_regex_validated"])
        self.store_data(settings, "dst_regex", self["dst_regex_validated"])

    def save(self, settings):
        """Store any validation errors from ffmpeg_convert when we couldn't write settings."""
        # XXX: We can't trigger this every time plugin is reloaded, only when the user moves around in prefs menu.
        self.store_data(settings, "src_regex_validated", self["src_regex_validated"])
        self.store_data(settings, "dst_regex_validated", self["dst_regex_validated"])

    def update_settings(self, settings_data):
        """ Read updated data when user changes input fields."""
        self.debug("_____ update_settings()")
        [self.load_data(settings_data, d) for d in ["debug_enabled", "auto_convert", "src_regex", "dst_regex"]]

    def validate(self, properties, prop_id, settings_data):
        """ Validate user input regex with re.compile() """
        run_button = obs.obs_properties_get(properties, "run_button")
        try:
            re.compile(self["src_regex"])
            obs.obs_property_set_enabled(run_button, True)
            obs.obs_property_set_description(run_button, "Run")
            self.store_data(settings_data, "src_regex_validated", self["src_regex"])
            self.store_data(settings_data, "dst_regex_validated", self["dst_regex"])
        except Exception:
            self.debug("Invalid regex!")
            obs.obs_property_set_enabled(run_button, False)
            obs.obs_property_set_description(run_button, "Invalid regular expression!")
        self.debug(f"src validated: {self['src_regex_validated']}     dst validated: {self['dst_regex_validated']}")

    def recording_finished(self, stop_code):
        """ Implements post-recording callback. """
        self.debug(f"Recording finished with stop_code: {stop_code}")
        if self['auto_convert'] is True and stop_code is 0:
            self.ffmpeg_convert()

    def find_latest_obs_capture(self, capture_dir):
        # TODO: handle this better.
        def new_video_sort_key(f):
            if f.name[-3:] in ['flv', 'mp4', 'mov', 'mkv'] and f.name is not self.last_ffmpeg_output:
                return f.stat().st_mtime
            return 0
        newest_video_file = sorted(os.scandir(capture_dir), key=new_video_sort_key, reverse=True)[0]
        if new_video_sort_key(newest_video_file) is 0:
            print("Could not find any video files!")
            return None
        return newest_video_file.name

    def ffmpeg_convert(self):
        """Search $HOME/videos for most recently created file. Convert using custom ffmpeg command. """
        # XXX: We can get an object of type config_t but no Python methods are set up to access it.
        # Instead we have to prompt user to specify their video folder.
        # cfg = obs.obs_frontend_get_profile_config()
        capture_dir = self['record_folder'] + os.path.sep
        obs_capture_file_name = self.find_latest_obs_capture(capture_dir)
        if obs_capture_file_name is None:
            return False

        # Get current scene and source name for %SUBSTITUTION%
        current_scene = obs.obs_frontend_get_current_scene()  # Note - returns an "obs_source" object
        scene_name = obs.obs_source_get_name(current_scene)
        current_scene = obs.obs_scene_from_source(current_scene)
        scene_items = obs.obs_scene_enum_items(current_scene)
        source_names = [obs.obs_source_get_name(obs.obs_sceneitem_get_source(i)) for i in scene_items]
        obs.sceneitem_list_release(scene_items)

        # Do regexp and token substitutions
        out_file_name = obs_capture_file_name[0:-4]
        if self["src_regex_validated"] is not None:
            try:
                dst_regex_out = self["dst_regex_validated"].replace("%SCENE%", scene_name)
                for n, src in enumerate(source_names):
                    repl_str = f"%SOURCE{n + 1}%"
                    dst_regex_out = dst_regex_out.replace(repl_str, src)
                out_file_name = re.sub(self["src_regex_validated"], dst_regex_out, out_file_name)
            except Exception:
                ### XXX: Should invalidate src_regex and dst_regex if this happens
                print("Regular expression replacement failed!")
        out_file_name = out_file_name + ".mp4"

        # Run ffmpeg
        ffmpeg_command = f'ffmpeg -i "{capture_dir + obs_capture_file_name}" {self["custom_flags"]} "{capture_dir + out_file_name}"'
        self.debug(f"ffmpeg command: {ffmpeg_command}")
        try:
            res = subprocess.run(ffmpeg_command, check=True, universal_newlines=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(res.stderr)
            self.last_ffmpeg_output = out_file_name
        except subprocess.CalledProcessError as e:
            # Todo: send a louder message if this happens (and for failure of regex above)
            print(f"Ffmpeg failed! Command was: \n{ffmpeg_command}\n\nOutput was:")
            print(e.stderr)


# Instance plugin
ffplug = OBSPluginFfmpeg()



# Define global callbacks
def cb_button_pressed(properties, button):
    # XXX: unlike in search_str_callback, editing the button text in this callback doesn't work.
    ffplug.ffmpeg_convert()
    return True

def cb_search_text_changed(*args):
    ffplug.validate(*args)
    return True

def cb_recording_finished(callback_data):
    stop_code = obs.calldata_int(callback_data, "code")
    ffplug.recording_finished(stop_code)
    return True

def update_recording_callback(reconnect = True):
    if ffplug.recording_signal_handler is not None:
        obs.signal_handler_disconnect(ffplug.recording_signal_handler, "stop", cb_recording_finished)
    if reconnect:
        ffplug.recording_signal_handler = obs.obs_output_get_signal_handler(obs.obs_frontend_get_recording_output())
        obs.signal_handler_connect(ffplug.recording_signal_handler, "stop", cb_recording_finished)



# OBS API Hooks Start Below
def script_defaults(settings):
    # obs.obs_data_clear(settings)  # Clear saved plugin data. Useful for debugging.
    ffplug.set_defaults(settings)

def script_load(settings):
    ffplug.load(settings)
    update_recording_callback()
    # XXX: there's no good way to trigger callbacks when profiles are changed. Check every 10s instead.
    obs.timer_add(update_recording_callback, 10000)

def script_description():
    return ffplug.description

def script_update(settings):
    ffplug.update_settings(settings)

def script_unload():
    ffplug.debug("_____ script_unload()")
    update_recording_callback(False)
    obs.timer_remove(update_recording_callback)

def script_save(settings):
    ffplug.save(settings)

def script_properties():
    ffplug.debug("_____ script_properties()")
    p = obs.obs_properties_create()
    obs.obs_properties_add_bool(p, "auto_convert", "Autorun after recording")
    obs.obs_properties_add_bool(p, "debug_enabled", "Debug Mode")
    search_area = obs.obs_properties_add_text(p, "src_regex", "Find (regex)", 0)
    obs.obs_property_set_modified_callback(search_area, cb_search_text_changed)
    replace_area = obs.obs_properties_add_text(p, "dst_regex", "Replace (regex)", 0)
    obs.obs_property_set_modified_callback(replace_area, cb_search_text_changed)
    obs.obs_properties_add_path(p, "record_folder", "Recording folder",
                                obs.OBS_PATH_DIRECTORY, "", os.path.expanduser("~"))
    obs.obs_properties_add_text(p, "custom_flags", "Ffmpeg flags:", 0)
    obs.obs_properties_add_button(p, "run_button", "Run", cb_button_pressed)
    return p

