import socket
import os
import signal

SOCKET_PATH = '/tmp/csbenchlab_matlab_daemon.sock'

def get_csb_path_from_matlab(eng):
    if eng is not None:
        eng.eval("path = which('csbenchlab');", nargout=0)
        path = eng.workspace['path']
        # try get path with which
        if path is None or path == "":
            if not check_installed():
                raise Exception("csbenchlab is not installed in MATLAB. " \
                "Please install it from MATLAB Add-On Explorer.")
            else:
                raise Exception("csbenchlab is installed but could not find path. " \
                "Try running the 'csbenchlab' application from directly from matlab first to " \
                "initialize the add-on properly. " \
                "Addidionally, please make sure it is added to MATLAB path.")
    return os.path.dirname(path)

def get_csb_path_from_env():
    path = os.getenv("CSB_M_PATH", None)
    return path



def check_csb_path(csb_path):
    if csb_path is None or csb_path == "":
        raise Exception("csbenchlab path is not set.")
    if not os.path.exists(csb_path):
        raise Exception(f"csbenchlab path '{csb_path}' does not exist.")
    if not os.path.exists(os.path.join(csb_path, "csbenchlab.m")):
        raise Exception(f"csbenchlab path '{csb_path}' is not valid. " \
        "Could not find 'csbenchlab.m' file in the specified path.")


def check_installed(eng):
    if eng is not None:
        command = """
        a = table2struct(matlab.addons.installedAddons());
        a = {[a.Name]};
        """
        eng.eval(command, nargout=0)
        addons = eng.workspace['a'][0]
        for a in addons:
            if a == "csbenchlab":
                return True
    return False

def start_daemon():
    import matlab.engine

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)


    eng = None
    eng = matlab.engine.start_matlab()
    eng.eval(f"matlab.engine.shareEngine;", nargout=0)

    # check csbenchlab_mat folder relative to this file


    csb_path = get_csb_path_from_env()
    if csb_path is None:
        csb_py_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csb_path = os.path.join(csb_py_path, 'csbenchlab_mat')
        if os.path.exists(os.path.join(csb_path, "csbenchlab.m")):
            eng.eval(f"addpath('{csb_path}');", nargout=0)
        # try to find csb path from matlab
        csb_path = get_csb_path_from_matlab(eng)
    if csb_path is None:
        raise Exception("Could not find csbenchlab installation. " \
        "Please make sure it is installed and added to MATLAB path or system PATH.")

    check_csb_path(csb_path)
    eng.eval(f"addpath(genpath('{csb_path}'));", nargout=0)
    eng.eval(f"source_libraries();", nargout=0)

    print("Daemon started, waiting for commands...")
    while True:
        conn, _ = server.accept()
        data = conn.recv(1024).decode()

        print(f"Received command: {data}")
        if data == "csb:exit":
            conn.send(b"Daemon exiting")
            conn.close()
            break
        if data == "csb:path":
            conn.send(csb_path.encode())
            conn.close()
            continue
        if data == "csb:ping":
            conn.send("csb:pong".encode())
            conn.close()
            continue

        try:
            data = data.strip('\n')
            eng.eval(data, nargout=0)
            # if has variable temp, return it as json
            exists = int(eng.eval("exist('temp', 'var');", nargout=1))
            if exists == 0:
                response = ""
            else:
                response = eng.workspace["temp"]
        except Exception as e:
            conn.send(bytearray([1]))
            conn.send(f"csb_err: {str(e)}".encode())
            conn.close()
            continue
        eng.eval("clear temp;", nargout=0)

        # Process command (echo example)
        # remove temp variable
        enc = bytearray(1) + len(response).to_bytes(4, byteorder='little') + response.encode()
        conn.send(enc)
        conn.close()

def cleanup():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)
        start_daemon()
    except Exception as e:
        cleanup()
