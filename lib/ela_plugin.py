import os
import sys
import subprocess
from xml.dom import minidom
import shutil

SCRIPT_PATH=os.path.realpath(__file__)
TOOLCHAINS_DIR_PATH=os.path.dirname(os.path.dirname(SCRIPT_PATH))
TOOLCHAINS_DIR_NAME=os.path.basename(TOOLCHAINS_DIR_PATH)

# NOTE: Call setup_paths() to get those paths ready
app_dir_path = None
plugins_dir_path = None
app_plugin_path = None

ELECTRON_DIR_PATH = None
ELECTRON_TITLERBAR_DIR_PATH = None
ELECTRON_MAIN_DIR_PATH = None
ELECTRON_RENDERER_DIR_PATH = None
ELECTRON_SCRIPT_DIR_PATH = None

# Method that makes this script folders/paths ready for later use.
# It is mandatory to call this first.
def setup_paths(_app_dir_path, _plugins_dir_path):
    global app_dir_path, plugins_dir_path, app_plugin_path
    global ELECTRON_DIR_PATH, ELECTRON_TITLERBAR_DIR_PATH, ELECTRON_MAIN_DIR_PATH, ELECTRON_RENDERER_DIR_PATH, ELECTRON_SCRIPT_DIR_PATH

    app_dir_path = _app_dir_path
    plugins_dir_path = _plugins_dir_path
    app_plugin_path = os.path.realpath(os.path.join(app_dir_path, "plugins"))

    ELECTRON_DIR_PATH=os.path.join(app_dir_path, "platform_src/electron")
    ELECTRON_TITLERBAR_DIR_PATH=os.path.join(ELECTRON_DIR_PATH, "titlebar")
    ELECTRON_MAIN_DIR_PATH=os.path.join(ELECTRON_DIR_PATH, "main")
    ELECTRON_RENDERER_DIR_PATH=os.path.join(ELECTRON_DIR_PATH, "renderer")
    ELECTRON_SCRIPT_DIR_PATH=os.path.join(app_dir_path, "scripts/electron")

    # Dump a few info about used paths
    print("Runtime path: "+app_dir_path)
    print("Plugins path: "+plugins_dir_path)

def ensure_paths_are_setup():
    global app_dir_path, plugins_dir_path, app_plugin_path

    if app_dir_path is None or plugins_dir_path is None:
        print("Paths not configured. Please call ela_plugin's setup_paths() method first.")
        sys.exit(1)

def run_cmd(cmd, ignore_error=False):
    print("Running: " + cmd)
    ret = subprocess.call(cmd, shell=True)
    if not ignore_error and ret != 0:
        sys.exit(ret)

def plugin_prepare(check_update=False):
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    print("Preparing plugins with runtime plugin path: "+app_plugin_path)

    if os.path.isdir(app_plugin_path):
        if check_update:
            plugin_update()
    # else:
    #     plugin_convertTS2JS()

def plugin_update_dir(plugin_dir):
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    print("Updating plugin dir: "+plugin_dir)

    dirs = os.listdir(plugin_dir)
    for dir in dirs:
        filepath = os.path.join(plugin_dir, dir)
        print("Checking plugin dir: "+filepath)
        if os.path.isdir(filepath):
            try:
                is_changed = is_plugin_changed(dir)
                if is_changed:
                    print('Reinstalling plugin ' + dir)
                    re_install_plugin(filepath, False)
            except Exception as err:
                print("Error: " + str(err))
    restore_files()

def plugin_update():
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    print("Plugin update")

    plugin_update_dir(plugins_dir_path)

# # first build
# def plugin_convertTS2JS():
#     global app_dir_path, plugins_dir_path, app_plugin_path
#     ensure_paths_are_setup()

#     plugin_convertTS2JS_dir(plugins_dir_path)


# def plugin_convertTS2JS_dir(plugin_dir):
#     global app_dir_path, plugins_dir_path, app_plugin_path
#     ensure_paths_are_setup()

#     #print("Converting TS to JS with plugin dir: "+plugin_dir)

#     dirs = os.listdir(plugin_dir)
#     for dir in dirs:
#         filepath = os.path.join(plugin_dir, dir)
#         #print("Converting TS to JS with plugin sub-dir: "+filepath)
#         if os.path.isdir(filepath):
#             tsconfig = os.path.join(filepath, "www/tsconfig.json")
#             if os.path.isfile(tsconfig):
#                 run_cmd("tsc --build " + tsconfig)

def get_pluginId(directory):
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    xmldoc = minidom.parse(directory + '/plugin.xml')
    itemlist = xmldoc.getElementsByTagName('plugin')
    return itemlist[0].attributes['id'].value

def is_plugin_changed(directory):
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    filepath = os.path.join(plugins_dir_path, directory + '/www/' + directory + '.ts')
    if os.path.isfile(filepath):
        modify_time_1 = os.stat(filepath).st_mtime

        plugin_path = os.path.join(plugins_dir_path, directory)
        pluginId = get_pluginId(plugin_path)
        plugin_runtime = os.path.join(app_dir_path, 'plugins/' + pluginId + '/www/' + directory + '.ts')
        modify_time_2 = os.stat(plugin_runtime).st_mtime
        return (modify_time_1 > modify_time_2)

def re_install_plugin(plugindir, restore = True):
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    # tsconfig = plugindir + "/www/tsconfig.json"
    # if os.path.isfile(tsconfig):
    #     run_cmd("tsc --build " + tsconfig)
    os.chdir(app_dir_path)
    backup_files()
    run_cmd("cordova plugin rm " + get_pluginId(plugindir), True)
    run_cmd("cordova plugin add " + os.path.relpath(plugindir))
    if restore:
        restore_files()

def backup_files():
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    os.chdir(app_dir_path)
    if not os.path.isfile(os.path.join(app_dir_path + '/config.xml.buildbak')):
        if isWindows():
            run_cmd('copy config.xml config.xml.buildbak')
        else:
            run_cmd('cp config.xml config.xml.buildbak')
    if not os.path.isfile(os.path.join(app_dir_path + '/package.json.buildbak')):
        if isWindows():
            run_cmd('copy package.json package.json.buildbak')
        else:
            run_cmd('cp package.json package.json.buildbak')

def restore_files():
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    os.chdir(app_dir_path)
    if os.path.isfile(os.path.join(app_dir_path + '/config.xml.buildbak')):
        if isWindows():
            run_cmd('move config.xml.buildbak config.xml')
        else:
            run_cmd('mv config.xml.buildbak config.xml')
    if os.path.isfile(os.path.join(app_dir_path + '/package.json.buildbak')):
        if isWindows():
            run_cmd('move package.json.buildbak package.json')
        else:
            run_cmd('mv package.json.buildbak package.json')

def isWindows():
    return sys.platform == "win32"

def install_titlebar():
    global app_dir_path, plugins_dir_path, app_plugin_path, ELECTRON_TITLERBAR_DIR_PATH
    ensure_paths_are_setup()

    os.chdir(ELECTRON_TITLERBAR_DIR_PATH)
    run_cmd('npm install')
    run_cmd("ionic build --prod")

# moved from before_prepare script
def copy_electron_files():
    global app_dir_path, plugins_dir_path, app_plugin_path
    global ELECTRON_RENDERER_DIR_PATH
    ensure_paths_are_setup()

    os.chdir(app_dir_path)

    build_electron_files()
    shutil.copy2(ELECTRON_RENDERER_DIR_PATH + "/dapp_preload.js", "platforms/electron/platform_www")

    # copy_electron_plugin("AppManager")
    # copy_electron_plugin("DIDSessionManager")
    # copy_electron_plugin("NotificationManager")
    # copy_electron_plugin("PasswordManager")
    # copy_electron_plugin("TitleBarManager")

def build_electron_files():
    global app_dir_path, plugins_dir_path, app_plugin_path
    global ELECTRON_SCRIPT_DIR_PATH, ELECTRON_MAIN_DIR_PATH
    ensure_paths_are_setup()

    os.chdir(ELECTRON_SCRIPT_DIR_PATH)
    run_cmd("node build.main.js")
    run_cmd("node build.renderer.js")
    os.chdir(ELECTRON_MAIN_DIR_PATH)
    run_cmd("tsc --build tsconfig.json --force")
    os.chdir(app_dir_path)

def install_electron():
    global app_dir_path, plugins_dir_path, app_plugin_path
    ensure_paths_are_setup()

    os.chdir(app_dir_path)
    if not os.path.isdir("platforms/electron"):
        run_cmd("cordova platform rm electron")
        run_cmd("cordova platform add electron@2.0.0-nightly.2020.9.12.734bbe7c", True)
